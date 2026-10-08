#!/usr/bin/env python3
"""Create pizza-style radial field plots for Problem 1.

Each of the 18 sectors represents one time from 100 s to 1800 s.  Within a
sector, colour is the radial field profile at the cylinder mid-plane.
The script intentionally uses only the Python standard library so that the
figure can be regenerated without a plotting-library dependency.
"""

from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path



PALETTES = {
    # Matplotlib-style coolwarm: low concentration is blue, high is red.
    "coolwarm": (
        (0.00, "#3b4cc0"),
        (0.25, "#8db0fe"),
        (0.50, "#dddcdc"),
        (0.75, "#f4987a"),
        (1.00, "#b40426"),
    ),
    # Inferno-like thermodynamic palette: cold dark, hot bright yellow.
    "thermal": (
        (0.00, "#000004"),
        (0.25, "#57106e"),
        (0.50, "#bc3754"),
        (0.75, "#f98e09"),
        (1.00, "#fcffa4"),
    ),
}

FIELD_SCALES = {
    "coolwarm": {
        "minimum": 1.50,
        "maximum": 2.55,
        "ticks": (1.50, 1.75, 2.00, 2.25, 2.55),
        "label_cn": "含水率",
        "unit": "(kg/kg)",
        "decimals": 2,
        "initial": 2.55,
    },
    "thermal": {
        "minimum": 28.0,
        "maximum": 36.8,
        "ticks": (28.0, 30.0, 32.0, 34.0, 36.0, 36.8),
        "label_cn": "温度",
        "unit": "(°C)",
        "decimals": 1,
        "initial": 28.0,
    },
}


def hex_to_rgb(value: str) -> tuple[int, int, int]:
    value = value.lstrip("#")
    return tuple(int(value[i : i + 2], 16) for i in (0, 2, 4))


def blend(a: str, b: str, fraction: float) -> str:
    rgb_a, rgb_b = hex_to_rgb(a), hex_to_rgb(b)
    rgb = tuple(round(x + (y - x) * fraction) for x, y in zip(rgb_a, rgb_b))
    return "#" + "".join(f"{channel:02x}" for channel in rgb)


def colour(
    value: float,
    low: float,
    high: float,
    stops: tuple[tuple[float, str], ...],
) -> str:
    position = min(1.0, max(0.0, (value - low) / (high - low)))
    for (x0, c0), (x1, c1) in zip(stops[:-1], stops[1:]):
        if position <= x1:
            return blend(c0, c1, (position - x0) / (x1 - x0))
    return stops[-1][1]


def point(cx: float, cy: float, radius: float, angle: float) -> tuple[float, float]:
    """Polar point with zero at 12 o'clock and positive angles clockwise."""
    return cx + radius * math.sin(angle), cy - radius * math.cos(angle)


def annular_sector_path(
    cx: float,
    cy: float,
    inner: float,
    outer: float,
    start: float,
    end: float,
) -> str:
    x1, y1 = point(cx, cy, inner, start)
    x2, y2 = point(cx, cy, outer, start)
    x3, y3 = point(cx, cy, outer, end)
    x4, y4 = point(cx, cy, inner, end)
    if inner <= 1e-8:
        return (
            f"M {cx:.3f},{cy:.3f} L {x2:.3f},{y2:.3f} "
            f"A {outer:.3f},{outer:.3f} 0 0 1 {x3:.3f},{y3:.3f} Z"
        )
    return (
        f"M {x1:.3f},{y1:.3f} L {x2:.3f},{y2:.3f} "
        f"A {outer:.3f},{outer:.3f} 0 0 1 {x3:.3f},{y3:.3f} "
        f"L {x4:.3f},{y4:.3f} "
        f"A {inner:.3f},{inner:.3f} 0 0 0 {x1:.3f},{y1:.3f} Z"
    )


def interpolate(radii: list[float], values: list[float], radius: float) -> float:
    if radius <= radii[0]:
        return values[0]
    if radius >= radii[-1]:
        return values[-1]
    for i in range(1, len(radii)):
        if radius <= radii[i]:
            f = (radius - radii[i - 1]) / (radii[i] - radii[i - 1])
            return values[i - 1] + f * (values[i] - values[i - 1])
    raise RuntimeError("radius interpolation failed")


def read_profiles(
    path: Path,
    initial_value: float,
) -> tuple[list[int], list[float], list[list[float]]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.reader(handle))
    if not rows or len(rows[0]) < 2:
        raise ValueError(f"No radial data found in {path}")
    radii = [float(label.split("=")[1].removesuffix("cm")) for label in rows[0][1:]]
    times = [int(float(row[0])) for row in rows[1:]]
    profiles = [[float(value) for value in row[1:]] for row in rows[1:]]
    source_times = list(range(100, 1801, 100))
    if times == source_times:
        times.insert(0, 0)
        profiles.insert(0, [initial_value] * len(radii))
    expected = list(range(0, 1801, 100))
    if times != expected:
        raise ValueError(f"Expected times {expected}, got {times}")
    if any(len(profile) != len(radii) for profile in profiles):
        raise ValueError("Radial profile length does not match the radius header")
    return times, radii, profiles


def make_svg(
    times: list[int],
    radii: list[float],
    profiles: list[list[float]],
    palette: str,
) -> str:
    """Return an SVG with 19 time sectors and a two-sector directional gap."""
    width, height = 1680, 1400
    cx = cy = 700.0
    plot_radius = 555.0
    gap_sectors = 2
    sector_angle = 2.0 * math.pi / (len(times) + gap_sectors)
    gap_angle = gap_sectors * sector_angle
    # Centre the blank wedge 45 degrees to the upper-left.
    gap_center_angle = math.radians(-45.0)
    first_angle = gap_center_angle + gap_angle / 2.0
    stops = PALETTES[palette]
    scale = FIELD_SCALES[palette]
    data_min = float(scale["minimum"])
    data_max = float(scale["maximum"])
    parts: list[str] = []

    field_gradient_defs: list[str] = []
    for index, profile in enumerate(profiles):
        field_gradient_defs.append(
            f'<radialGradient id="field-gradient-{index}" gradientUnits="userSpaceOnUse" '
            f'cx="{cx}" cy="{cy}" r="{plot_radius}">'
        )
        for radius_cm, value in zip(radii, profile):
            offset = radius_cm / radii[-1]
            field_gradient_defs.append(
                f'<stop offset="{offset:.2%}" '
                f'stop-color="{colour(value, data_min, data_max, stops)}"/>'
            )
        field_gradient_defs.append("</radialGradient>")

    parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img" shape-rendering="geometricPrecision">'
    )
    parts.append(
        "<defs>"
        '<filter id="shadow" x="-20%" y="-20%" width="140%" height="140%">'
        '<feDropShadow dx="0" dy="5" stdDeviation="9" flood-color="#14212b" flood-opacity="0.18"/>'
        "</filter>"
        '<marker id="time-arrow" markerWidth="12" markerHeight="12" refX="10" refY="4" orient="auto">'
        '<path d="M0,0 L0,8 L11,4 z" fill="#314c5b"/>'
        "</marker>"
        '<linearGradient id="colorbar-gradient" x1="0" y1="1" x2="0" y2="0">'
        + "".join(
            f'<stop offset="{position:.0%}" stop-color="{shade}"/>'
            for position, shade in stops
        )
        + "</linearGradient>"
        + "".join(field_gradient_defs)
        + "</defs>"
    )
    parts.append(f'<rect width="{width}" height="{height}" fill="#ffffff"/>')
    parts.append(
        f'<circle cx="{cx}" cy="{cy}" r="{plot_radius + 4}" fill="#ffffff" filter="url(#shadow)"/>'
    )

    for index in range(len(profiles)):
        start = first_angle + index * sector_angle
        path = annular_sector_path(
            cx, cy, 0.0, plot_radius,
            start - 0.00035, start + sector_angle + 0.00035,
        )
        parts.append(
            f'<g><path d="{path}" fill="url(#field-gradient-{index})"/></g>'
        )

    data_end_angle = first_angle + len(times) * sector_angle
    # Radial guides at r/R = 0.25, 0.50, 0.75; leave the blank wedge open.
    for fraction in (0.25, 0.50, 0.75):
        radius = plot_radius * fraction
        x0, y0 = point(cx, cy, radius, first_angle)
        x1, y1 = point(cx, cy, radius, data_end_angle)
        parts.append(
            f'<path d="M {x0:.2f},{y0:.2f} A {radius:.2f},{radius:.2f} 0 1 1 {x1:.2f},{y1:.2f}" '
            'fill="none" stroke="#ffffff" stroke-width="1.3" '
            'stroke-opacity="0.46" stroke-dasharray="5 6"/>'
        )
    outer_x0, outer_y0 = point(cx, cy, plot_radius, first_angle)
    outer_x1, outer_y1 = point(cx, cy, plot_radius, data_end_angle)
    parts.append(
        f'<path d="M {cx:.2f},{cy:.2f} L {outer_x0:.2f},{outer_y0:.2f} '
        f'A {plot_radius:.2f},{plot_radius:.2f} 0 1 1 {outer_x1:.2f},{outer_y1:.2f} Z" '
        'fill="none" stroke="#243b48" stroke-width="2.4"/>'
    )
    for index in range(len(times) + 1):
        angle = first_angle + index * sector_angle
        x, y = point(cx, cy, plot_radius, angle)
        parts.append(
            f'<line x1="{cx}" y1="{cy}" x2="{x:.2f}" y2="{y:.2f}" '
            'stroke="#ffffff" stroke-width="1.45" stroke-opacity="0.82"/>'
        )

    # Mark 300 s intervals plus both endpoints. The initial time is larger,
    # bold, and closer to the rim.
    for index in (0, 3, 6, 9, 12, 15, len(times) - 1):
        time = times[index]
        angle = first_angle + (index + 0.5) * sector_angle
        label_radius = 590.0
        font_size = 48
        font_weight = 700
        x, y = point(cx, cy, label_radius, angle)
        angle_deg = math.degrees(angle)
        rotation = angle_deg
        if 90 < angle_deg < 270:
            rotation += 180
        parts.append(
            f'<text x="{x:.2f}" y="{y:.2f}" text-anchor="middle" dominant-baseline="central" '
            f'transform="rotate({rotation:.2f} {x:.2f} {y:.2f})" '
            'font-family="Latin Modern Roman, CMU Serif, Computer Modern, serif" '
            f'font-size="{font_size}" font-weight="{font_weight}" fill="#263f4c">'
            '<tspan font-style="italic">t</tspan>'
            f'<tspan xml:space="preserve"> = {time}s</tspan></text>'
        )

    # A short exterior arc beside the start time indicates clockwise flow
    # without wrapping around the whole disk.
    arrow_radius = 603.0
    first_time_angle = first_angle + 0.5 * sector_angle
    arrow_start = first_time_angle + 0.50 * sector_angle
    arrow_end = arrow_start + math.radians(28.0)
    arrow_x0, arrow_y0 = point(cx, cy, arrow_radius, arrow_start)
    arrow_x1, arrow_y1 = point(cx, cy, arrow_radius, arrow_end)
    parts.append(
        f'<path d="M {arrow_x0:.2f},{arrow_y0:.2f} '
        f'A {arrow_radius:.2f},{arrow_radius:.2f} 0 0 1 {arrow_x1:.2f},{arrow_y1:.2f}" '
        'fill="none" stroke="#314c5b" stroke-width="4.2" '
        'marker-end="url(#time-arrow)"/>'
    )

    # Full-height colorbar moved closer to the disk. Its horizontal physical
    # quantity label sits directly below the bar.
    colorbar_x, colorbar_y = 1395.0, 145.0
    colorbar_width, colorbar_height = 72.0, 1110.0
    parts.append(
        f'<text x="{colorbar_x + colorbar_width / 2:.2f}" '
        f'y="{colorbar_y + colorbar_height + 70:.2f}" '
        'text-anchor="middle" font-size="35" fill="#263f4c">'
        '<tspan font-family="Microsoft YaHei, 微软雅黑, PingFang SC, sans-serif" '
        f'font-weight="600">{scale["label_cn"]}</tspan>'
        '<tspan dx="13" font-family="Latin Modern Roman, CMU Serif, Computer Modern, serif" '
        f'font-weight="400">{scale["unit"]}</tspan></text>'
    )
    parts.append(
        f'<rect x="{colorbar_x}" y="{colorbar_y}" width="{colorbar_width}" '
        f'height="{colorbar_height}" fill="url(#colorbar-gradient)" '
        'stroke="#314c5b" stroke-width="1.4"/>'
    )
    for tick in scale["ticks"]:
        tick_value = float(tick)
        y = colorbar_y + colorbar_height * (
            1.0 - (tick_value - data_min) / (data_max - data_min)
        )
        parts.append(
            f'<line x1="{colorbar_x + colorbar_width}" y1="{y:.2f}" '
            f'x2="{colorbar_x + colorbar_width + 17}" y2="{y:.2f}" '
            'stroke="#314c5b" stroke-width="1.8"/>'
        )
        tick_label = f'{tick_value:.{int(scale["decimals"])}f}'
        parts.append(
            f'<text x="{colorbar_x + colorbar_width + 31}" y="{y:.2f}" '
            'dominant-baseline="central" '
            'font-family="Latin Modern Roman, CMU Serif, Computer Modern, serif" '
            f'font-size="31" fill="#263f4c">{tick_label}</text>'
        )

    parts.append("</svg>")
    return "\n".join(parts)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input",
        type=Path,
        default=(
            Path(__file__).with_name("moisture.csv")
            if Path(__file__).with_name("moisture.csv").exists()
            else Path(__file__).resolve().parents[1] / "moisture.csv"
        ),
        help="Problem 1 radial field CSV",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).with_name("q1_moisture_pizza.svg"),
        help="Output SVG path",
    )
    parser.add_argument(
        "--palette",
        choices=tuple(PALETTES),
        default="coolwarm",
        help="Colour palette for the field",
    )
    args = parser.parse_args()
    initial_value = float(FIELD_SCALES[args.palette]["initial"])
    times, radii, profiles = read_profiles(args.input, initial_value)
    svg = make_svg(times, radii, profiles, args.palette)
    args.output.write_text(svg, encoding="utf-8")
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
