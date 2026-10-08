#!/usr/bin/env python3
"""Generate a publication-quality 1x2 combined panel for Problem 1.

Layout:
- Left: 含水率分布演变 (Moisture Field Evolution) - with R0 = 2 cm, r (cm), and 0.5, 1.0, 1.5
- Right: 温度分布演变 (Temperature Field Evolution) - with clean axis and 0.5, 1.0, 1.5 only
- Tailored for A4 page width (~160-165 mm):
  - Maximized circle diameters (~5.8 cm on printed A4).
  - Prominent, enlarged colorbar scale annotations (numbers, ticks, units).
  - Rotated 45-degree scale numbers along ruler, completely eliminating pizza overlap.
  - Asymmetric ruler annotation (Left retains full symbols, Right keeps minimal coordinates).
"""

from __future__ import annotations

import csv
import math
import subprocess
from pathlib import Path

PALETTES = {
    "coolwarm": (
        (0.00, "#3b4cc0"),
        (0.25, "#8db0fe"),
        (0.50, "#dddcdc"),
        (0.75, "#f4987a"),
        (1.00, "#b40426"),
    ),
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

def colour(value: float, low: float, high: float, stops: tuple[tuple[float, str], ...]) -> str:
    position = min(1.0, max(0.0, (value - low) / (high - low)))
    for (x0, c0), (x1, c1) in zip(stops[:-1], stops[1:]):
        if position <= x1:
            return blend(c0, c1, (position - x0) / (x1 - x0))
    return stops[-1][1]

def point(cx: float, cy: float, radius: float, angle: float) -> tuple[float, float]:
    """Polar point with zero at 12 o'clock and positive angles clockwise."""
    return cx + radius * math.sin(angle), cy - radius * math.cos(angle)

def annular_sector_path(cx: float, cy: float, inner: float, outer: float, start: float, end: float) -> str:
    x1, y1 = point(cx, cy, inner, start)
    x2, y2 = point(cx, cy, outer, start)
    x3, y3 = point(cx, cy, outer, end)
    x4, y4 = point(cx, cy, inner, end)
    if inner <= 1e-8:
        return f"M {cx:.3f},{cy:.3f} L {x2:.3f},{y2:.3f} A {outer:.3f},{outer:.3f} 0 0 1 {x3:.3f},{y3:.3f} Z"
    return (
        f"M {x1:.3f},{y1:.3f} L {x2:.3f},{y2:.3f} "
        f"A {outer:.3f},{outer:.3f} 0 0 1 {x3:.3f},{y3:.3f} "
        f"L {x4:.3f},{y4:.3f} "
        f"A {inner:.3f},{inner:.3f} 0 0 0 {x1:.3f},{y1:.3f} Z"
    )

def read_profiles(path: Path, initial_value: float) -> tuple[list[int], list[float], list[list[float]]]:
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
    return times, radii, profiles

def generate_q1_subpanel(
    palette: str,
    cx: float,
    cy: float,
    plot_radius: float,
    cb_x: float,
    cb_y: float,
    cb_w: float,
    cb_h: float,
    times: list[int],
    radii: list[float],
    profiles: list[list[float]],
    is_left: bool = True,
) -> tuple[list[str], list[str]]:
    """Return defs and SVG elements for a single Problem 1 subpanel."""
    defs: list[str] = []
    p: list[str] = []

    stops = PALETTES[palette]
    scale = FIELD_SCALES[palette]
    data_min = float(scale["minimum"])
    data_max = float(scale["maximum"])
    r0_cm = 2.0

    gap_sectors = 2
    sector_angle = 2.0 * math.pi / (len(times) + gap_sectors)
    gap_angle = gap_sectors * sector_angle
    gap_center_angle = math.radians(-45.0)
    first_angle = gap_center_angle + gap_angle / 2.0
    data_end_angle = first_angle + len(times) * sector_angle

    # Radial gradient defs
    for index, profile in enumerate(profiles):
        defs.append(
            f'<radialGradient id="q1-grad-{palette}-{index}" gradientUnits="userSpaceOnUse" '
            f'cx="{cx}" cy="{cy}" r="{plot_radius}">'
        )
        for radius_cm, value in zip(radii, profile):
            offset = radius_cm / radii[-1]
            defs.append(
                f'<stop offset="{offset:.2%}" '
                f'stop-color="{colour(value, data_min, data_max, stops)}"/>'
            )
        defs.append("</radialGradient>")

    # Outer circle reference
    p.append(f'<circle cx="{cx}" cy="{cy}" r="{plot_radius}" fill="none" stroke="#263f4c" stroke-width="2.2"/>')

    # Annular sectors with gradients
    for index in range(len(profiles)):
        start = first_angle + index * sector_angle
        path = annular_sector_path(
            cx, cy, 0.0, plot_radius,
            start - 0.0004, start + sector_angle + 0.0004,
        )
        p.append(f'<path d="{path}" fill="url(#q1-grad-{palette}-{index})"/>')

    # Radial dashed guides at r = 0.5, 1.0, 1.5 cm
    for fraction in (0.25, 0.50, 0.75):
        radius = plot_radius * fraction
        x0, y0 = point(cx, cy, radius, first_angle)
        x1, y1 = point(cx, cy, radius, data_end_angle)
        p.append(
            f'<path d="M {x0:.2f},{y0:.2f} A {radius:.2f},{radius:.2f} 0 1 1 {x1:.2f},{y1:.2f}" '
            'fill="none" stroke="#ffffff" stroke-width="1.3" '
            'stroke-opacity="0.55" stroke-dasharray="4 5"/>'
        )

    # Sector divider lines
    for index in range(len(times) + 1):
        angle = first_angle + index * sector_angle
        x, y = point(cx, cy, plot_radius, angle)
        p.append(
            f'<line x1="{cx}" y1="{cy}" x2="{x:.2f}" y2="{y:.2f}" '
            'stroke="#ffffff" stroke-width="1.3" stroke-opacity="0.80"/>'
        )

    # Boundary outline of the active pizza
    outer_x0, outer_y0 = point(cx, cy, plot_radius, first_angle)
    outer_x1, outer_y1 = point(cx, cy, plot_radius, data_end_angle)
    p.append(
        f'<path d="M {cx:.2f},{cy:.2f} L {outer_x0:.2f},{outer_y0:.2f} '
        f'A {plot_radius:.2f},{plot_radius:.2f} 0 1 1 {outer_x1:.2f},{outer_y1:.2f} Z" '
        'fill="none" stroke="#243b48" stroke-width="2.2"/>'
    )

    # Milestone labels at 300s intervals (0, 300, 600, 900, 1200, 1500, 1800s)
    for index in (0, 3, 6, 9, 12, 15, len(times) - 1):
        time_val = times[index]
        angle = first_angle + (index + 0.5) * sector_angle
        label_radius = plot_radius + 40.0
        x, y = point(cx, cy, label_radius, angle)
        angle_deg = math.degrees(angle) % 360.0
        rotation = angle_deg
        if 90.0 < angle_deg < 270.0:
            rotation += 180.0
        p.append(
            f'<text x="{x:.2f}" y="{y:.2f}" text-anchor="middle" dominant-baseline="central" '
            f'transform="rotate({rotation:.2f} {x:.2f} {y:.2f})" '
            'font-family="Latin Modern Roman, CMU Serif, Computer Modern, serif" '
            'font-size="39" font-weight="700" fill="#263f4c">'
            '<tspan font-style="italic">t</tspan>'
            f'<tspan xml:space="preserve"> = {time_val}s</tspan></text>'
        )

    # Ruler scale in -45 deg gap
    gap_axis_ang = gap_center_angle
    ax0, ay0 = point(cx, cy, 0.0, gap_axis_ang)
    ax1, ay1 = point(cx, cy, plot_radius, gap_axis_ang)
    p.append(f'<line x1="{ax0:.2f}" y1="{ay0:.2f}" x2="{ax1:.2f}" y2="{ay1:.2f}" stroke="#314c5b" stroke-width="2.2"/>')

    ang_tick = gap_axis_ang - math.pi / 2.0

    # Intermediate ticks: 0.5, 1.0, 1.5
    for r_cm, txt in [(0.50, "0.5"), (1.00, "1.0"), (1.50, "1.5")]:
        r_px = plot_radius * (r_cm / r0_cm)
        tx, ty = point(cx, cy, r_px, gap_axis_ang)
        tick_len = 10.0
        tx1 = tx + tick_len * math.sin(ang_tick)
        ty1 = ty - tick_len * math.cos(ang_tick)
        p.append(f'<line x1="{tx:.2f}" y1="{ty:.2f}" x2="{tx1:.2f}" y2="{ty1:.2f}" stroke="#2a4353" stroke-width="2.0"/>')
        
        # Parallel rotated label: centered in corridor, zero pizza overlap
        offset = 19.0
        lx = tx + offset * math.sin(ang_tick)
        ly = ty - offset * math.cos(ang_tick)
        p.append(
            f'<text x="{lx:.2f}" y="{ly:.2f}" text-anchor="middle" dominant-baseline="central" '
            f'transform="rotate(45 {lx:.2f} {ly:.2f})" '
            'font-family="Latin Modern Roman, CMU Serif, Computer Modern, serif" '
            f'font-size="28" font-weight="700" fill="#425a69">{txt}</text>'
        )

    # R0 and r information: ONLY on the left figure (Moisture)
    if is_left:
        # Outer rim tick and R0 = 2 cm
        r_px = plot_radius
        tx, ty = point(cx, cy, r_px, gap_axis_ang)
        tick_len = 16.0
        tx1 = tx + tick_len * math.sin(ang_tick)
        ty1 = ty - tick_len * math.cos(ang_tick)
        p.append(f'<line x1="{tx:.2f}" y1="{ty:.2f}" x2="{tx1:.2f}" y2="{ty1:.2f}" stroke="#2a4353" stroke-width="2.4"/>')
        p.append(
            f'<text x="{tx1 - 10:.2f}" y="{ty1 - 12:.2f}" text-anchor="end" dominant-baseline="central" '
            'font-family="Latin Modern Roman, CMU Serif, Computer Modern, serif" '
            'font-size="33" font-weight="700" fill="#203744">'
            '<tspan font-style="italic">R</tspan>₀ = 2 cm</text>'
        )

        # r (cm) label on right side of ruler
        norm_above_x = -math.sin(ang_tick)
        norm_above_y = math.cos(ang_tick)
        rx_mid, ry_mid = point(cx, cy, plot_radius * 0.54, gap_axis_ang)
        lbl_x = rx_mid + 32.0 * norm_above_x
        lbl_y = ry_mid + 32.0 * norm_above_y
        p.append(
            f'<text x="{lbl_x:.2f}" y="{lbl_y:.2f}" text-anchor="middle" dominant-baseline="central" '
            f'transform="rotate(45 {lbl_x:.2f} {lbl_y:.2f})" xml:space="preserve" '
            'font-family="Latin Modern Roman, CMU Serif, Computer Modern, serif" '
            'font-size="29" font-weight="700" fill="#2a4353">'
            '<tspan font-style="italic">r</tspan>'
            '<tspan font-weight="500">&#160;(cm)</tspan></text>'
        )

    # Time arrow
    arrow_radius = plot_radius + 92.0
    first_time_angle = first_angle + 0.5 * sector_angle
    arrow_start = first_time_angle + 0.50 * sector_angle
    arrow_end = arrow_start + math.radians(24.0)
    arrow_x0, arrow_y0 = point(cx, cy, arrow_radius, arrow_start)
    arrow_x1, arrow_y1 = point(cx, cy, arrow_radius, arrow_end)
    p.append(
        f'<path d="M {arrow_x0:.2f},{arrow_y0:.2f} A {arrow_radius:.2f},{arrow_radius:.2f} 0 0 1 {arrow_x1:.2f},{arrow_y1:.2f}" '
        'fill="none" stroke="#314c5b" stroke-width="3.8" marker-end="url(#time-arrow)"/>'
    )

    # Colorbar
    grad_id = f"cb-grad-{palette}"
    p.append(
        f'<rect x="{cb_x:.2f}" y="{cb_y:.2f}" width="{cb_w:.2f}" '
        f'height="{cb_h:.2f}" fill="url(#{grad_id})" stroke="#314c5b" stroke-width="1.6"/>'
    )
    for tick in scale["ticks"]:
        tick_value = float(tick)
        y = cb_y + cb_h * (1.0 - (tick_value - data_min) / (data_max - data_min))
        # Extended tick line
        p.append(
            f'<line x1="{cb_x + cb_w}" y1="{y:.2f}" '
            f'x2="{cb_x + cb_w + 18}" y2="{y:.2f}" stroke="#314c5b" stroke-width="2.2"/>'
        )
        tick_label = f'{tick_value:.{int(scale["decimals"])}f}'
        # Greatly enlarged and bolded tick annotations
        p.append(
            f'<text x="{cb_x + cb_w + 28}" y="{y:.2f}" dominant-baseline="central" '
            f'font-family="Latin Modern Roman, CMU Serif, Computer Modern, serif" '
            f'font-size="38" font-weight="700" fill="#182d3b">{tick_label}</text>'
        )

    # Colorbar label below (enlarged)
    p.append(
        f'<text x="{cb_x + cb_w / 2:.2f}" y="{cb_y + cb_h + 68:.2f}" '
        'text-anchor="middle" font-size="36" fill="#182d3b">'
        '<tspan font-family="Microsoft YaHei, 微软雅黑, PingFang SC, sans-serif" font-weight="700">'
        f'{scale["label_cn"]}</tspan>'
        '<tspan dx="10" font-family="Latin Modern Roman, CMU Serif, Computer Modern, serif" font-weight="600">'
        f'{scale["unit"]}</tspan></text>'
    )

    return defs, p

def make_q1_combined_svg(temp_csv: Path, moist_csv: Path) -> str:
    width, height = 3200, 1380
    cy = 670.0
    plot_radius = 560.0

    # Panel Left (Moisture - 含水率先行, is_left=True)
    cx_left = 680.0
    cb_x_left = 1355.0
    cb_y_left = 155.0
    cb_w = 46.0
    cb_h = 1030.0

    # Panel Right (Temperature - 温度在后, is_left=False)
    cx_right = 2170.0
    cb_x_right = 2845.0
    cb_y_right = 155.0

    t_times, t_radii, t_profiles = read_profiles(temp_csv, float(FIELD_SCALES["thermal"]["initial"]))
    m_times, m_radii, m_profiles = read_profiles(moist_csv, float(FIELD_SCALES["coolwarm"]["initial"]))

    # Subpanel Left: Moisture (is_left=True -> has R0=2 cm and r)
    defs_left, panel_left = generate_q1_subpanel(
        "coolwarm", cx_left, cy, plot_radius, cb_x_left, cb_y_left, cb_w, cb_h,
        m_times, m_radii, m_profiles, is_left=True
    )
    # Subpanel Right: Temperature (is_left=False -> minimal axis with 0.5, 1.0, 1.5 only)
    defs_right, panel_right = generate_q1_subpanel(
        "thermal", cx_right, cy, plot_radius, cb_x_right, cb_y_right, cb_w, cb_h,
        t_times, t_radii, t_profiles, is_left=False
    )

    parts: list[str] = []
    parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img" shape-rendering="geometricPrecision">'
    )
    parts.append("<defs>")
    parts.append(
        '<marker id="time-arrow" markerWidth="12" markerHeight="12" refX="10" refY="4" orient="auto">'
        '<path d="M0,0 L0,8 L11,4 z" fill="#314c5b"/>'
        '</marker>'
    )
    parts.append(
        '<linearGradient id="cb-grad-coolwarm" x1="0" y1="1" x2="0" y2="0">'
        + "".join(f'<stop offset="{pos:.0%}" stop-color="{col}"/>' for pos, col in PALETTES["coolwarm"])
        + "</linearGradient>"
    )
    parts.append(
        '<linearGradient id="cb-grad-thermal" x1="0" y1="1" x2="0" y2="0">'
        + "".join(f'<stop offset="{pos:.0%}" stop-color="{col}"/>' for pos, col in PALETTES["thermal"])
        + "</linearGradient>"
    )
    parts.extend(defs_left)
    parts.extend(defs_right)
    parts.append("</defs>")

    parts.append(f'<rect width="{width}" height="{height}" fill="#ffffff"/>')
    parts.extend(panel_left)
    parts.extend(panel_right)
    parts.append("</svg>")

    return "\n".join(parts)

def main() -> None:
    script_dir = Path(__file__).resolve().parent
    temp_csv = script_dir / "temperature.csv"
    moist_csv = script_dir / "moisture.csv"
    svg_str = make_q1_combined_svg(temp_csv, moist_csv)

    out_svg = script_dir / "q1_combined_pizza.svg"
    out_svg.write_text(svg_str, encoding="utf-8")
    print(f"Wrote {out_svg}")

    chrome = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    out_png = script_dir / "q1_combined_pizza.png"
    subprocess.run([
        chrome, "--headless", "--disable-gpu", "--force-device-scale-factor=2",
        "--window-size=3200,1380", f"--screenshot={out_png}", out_svg.as_uri()
    ], check=True)
    print(f"Rendered {out_png}")

if __name__ == "__main__":
    main()
