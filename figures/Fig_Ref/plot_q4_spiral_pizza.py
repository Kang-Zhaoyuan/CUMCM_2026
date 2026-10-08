import argparse
import base64
import io
import math
import subprocess
from pathlib import Path
import numpy as np
from PIL import Image
from scipy.interpolate import interp1d, PchipInterpolator, RegularGridInterpolator

PALETTES = {
    "coolwarm": (
        (0.00, np.array([59, 76, 192])),
        (0.25, np.array([141, 176, 254])),
        (0.50, np.array([221, 220, 220])),
        (0.75, np.array([244, 152, 122])),
        (1.00, np.array([180, 4, 38])),
    ),
    "thermal": (
        (0.00, np.array([0, 0, 4])),
        (0.25, np.array([87, 16, 110])),
        (0.50, np.array([188, 55, 84])),
        (0.75, np.array([249, 142, 9])),
        (1.00, np.array([252, 255, 164])),
    ),
}

FIELD_SCALES = {
    "coolwarm": {
        "minimum": 0.05,
        "maximum": 2.55,
        "ticks": (0.05, 0.50, 1.00, 1.50, 2.00, 2.55),
        "label_cn": "含水率",
        "unit": "(kg/kg)",
        "decimals": 2,
    },
    "thermal": {
        "minimum": 28.0,
        "maximum": 50.0,
        "ticks": (28.0, 32.0, 36.0, 40.0, 44.0, 48.0, 50.0),
        "label_cn": "温度",
        "unit": "(°C)",
        "decimals": 1,
    },
}

MILESTONES_MOISTURE = [
    (0.0, "0h"),
    (0.5, "0.5h"),
    (1.5, "1.5h"),
    (4.0, "4h"),
    (7.5, "7.5h"),
    (13.0, "13h"),
    (22.0, "22h"),
    (34.0, "34h"),
    (51.058, "51.1h"),
]

# Updated milestones for temperature as requested:
# 3.0h -> 15h, 3.5h -> 30h, 4.0h -> 51.1h
# Physical time mapping uses original smooth 0~4.0h progression,
# while the milestone labels display the user's updated timestamps.
MILESTONES_TEMPERATURE = [
    (0.0, "0h"),
    (0.5, "0.5h"),
    (1.0, "1.0h"),
    (1.5, "1.5h"),
    (2.0, "2.0h"),
    (2.5, "2.5h"),
    (3.0, "15h"),
    (3.5, "30h"),
    (4.0, "51.1h"),
]

def map_colors(val_arr, palette, vmin, vmax):
    stops = PALETTES[palette]
    pos = np.clip((val_arr - vmin) / (vmax - vmin), 0.0, 1.0)
    rgb = np.zeros((*pos.shape, 3), dtype=np.float32)
    for (x0, c0), (x1, c1) in zip(stops[:-1], stops[1:]):
        m = (pos >= x0) & (pos <= x1)
        if np.any(m):
            frac = ((pos[m] - x0) / (x1 - x0))[:, None]
            rgb[m] = c0[None, :] + frac * (c1 - c0)[None, :]
    m_high = pos >= stops[-1][0]
    if np.any(m_high):
        rgb[m_high] = stops[-1][1]
    return np.clip(rgb, 0, 255).astype(np.uint8)

def point(cx: float, cy: float, radius: float, angle: float) -> tuple[float, float]:
    return cx + radius * math.sin(angle), cy - radius * math.cos(angle)

def build_normalized_field(time_sec, radius_arr, field_arr, grid_r, eta_grid):
    n_times = len(time_sec)
    norm_field = np.zeros((n_times, len(eta_grid)), dtype=np.float64)
    for i in range(n_times):
        R = radius_arr[i]
        vals = field_arr[i]
        valid = np.where(np.isfinite(vals))[0]
        r_v = grid_r[valid]
        m_v = vals[valid]
        if r_v[-1] < R - 1e-5:
            slope = (m_v[-1] - m_v[-2]) / (r_v[-1] - r_v[-2])
            val_R = m_v[-1] + slope * (R - r_v[-1])
            if np.nanmin(field_arr) > 0.0:
                val_R = max(0.05, val_R)
            r_full = np.r_[r_v, R]
            m_full = np.r_[m_v, val_R]
        else:
            r_full = r_v
            m_full = m_v
        norm_field[i] = np.interp(eta_grid * R, r_full, m_full)
    return norm_field

def render_field_image(
    palette: str,
    time_sec: np.ndarray,
    radius_arr: np.ndarray,
    field_arr: np.ndarray,
    grid_r: np.ndarray,
    t_func_sec,
    first_angle: float,
    sweep_angle: float,
    plot_radius: float,
    r0_cm: float,
    res: int = 2400,
) -> str:
    cx = cy = plot_radius
    xs = np.linspace(0, 2 * plot_radius, res)
    ys = np.linspace(0, 2 * plot_radius, res)
    X, Y = np.meshgrid(xs, ys)

    dx = X - cx
    dy = Y - cy
    r_pix = np.sqrt(dx**2 + dy**2)
    theta = np.arctan2(dx, -dy)

    rel_theta = (theta - first_angle) % (2 * math.pi)
    in_sweep = (rel_theta >= 0) & (rel_theta <= sweep_angle)

    s = np.clip(rel_theta / sweep_angle, 0.0, 1.0)
    t_eval = t_func_sec(s)
    radius_interp = interp1d(time_sec, radius_arr, kind="linear", fill_value="extrapolate")
    R_eval = radius_interp(t_eval)
    r_limit_px = plot_radius * (R_eval / r0_cm)

    # Subpixel mask
    mask = in_sweep & (r_pix <= r_limit_px + 0.5) & (r_pix > 0)

    eta_grid = np.linspace(0.0, 1.0, 41)
    norm_field = build_normalized_field(time_sec, radius_arr, field_arr, grid_r, eta_grid)
    rgi = RegularGridInterpolator((time_sec, eta_grid), norm_field, bounds_error=False, fill_value=None)

    eta = np.zeros_like(r_pix)
    eta[mask] = np.clip(r_pix[mask] / r_limit_px[mask], 0.0, 1.0)

    t_valid = t_eval[mask]
    eta_valid = eta[mask]
    pts = np.column_stack([t_valid, eta_valid])
    vals_valid = rgi(pts)

    scale = FIELD_SCALES[palette]
    data_min = float(scale["minimum"])
    data_max = float(scale["maximum"])

    rgba = np.zeros((res, res, 4), dtype=np.uint8)
    rgb_valid = map_colors(vals_valid, palette, data_min, data_max)
    rgba[mask, :3] = rgb_valid

    # Antialiased boundary edge
    dist_to_edge = r_limit_px[mask] - r_pix[mask]
    alpha = np.clip((dist_to_edge + 0.5) / 1.0, 0.0, 1.0) * 255.0
    rgba[mask, 3] = alpha.astype(np.uint8)

    img = Image.fromarray(rgba, mode="RGBA")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    b64 = base64.b64encode(buf.getvalue()).decode("ascii")
    return f"data:image/png;base64,{b64}"

def make_pizza_svg(palette: str, npz_path: Path) -> str:
    width, height = 1680, 1400
    cx = cy = 700.0
    r0_cm = 2.0
    plot_radius = 555.0

    gap_center_angle = math.radians(-45.0)
    gap_width_rad = math.radians(34.2857)
    first_angle = gap_center_angle + gap_width_rad / 2.0
    sweep_angle = 2.0 * math.pi - gap_width_rad
    data_end_angle = first_angle + sweep_angle

    data = np.load(npz_path)
    time_sec = data["time"]
    radius_arr = data["current_radius_cm"]
    field_arr = data["moisture"] if palette == "coolwarm" else data["temperature"]
    grid_r = data["radius_grid"]

    scale = FIELD_SCALES[palette]
    data_min = float(scale["minimum"])
    data_max = float(scale["maximum"])

    if palette == "coolwarm":
        milestones = MILESTONES_MOISTURE
        milestone_hours = [m[0] for m in milestones]
        milestone_labels = [m[1] for m in milestones]
        s_milestones = np.linspace(0.0, 1.0, len(milestone_hours))
        t_func_sec = PchipInterpolator(s_milestones, [h * 3600.0 for h in milestone_hours])
    else:
        milestones = MILESTONES_TEMPERATURE
        # Use 0~4.0h physical linear progression for smooth shrinkage and thermal field
        milestone_physical_hours = [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0]
        milestone_labels = [m[1] for m in milestones]
        s_milestones = np.linspace(0.0, 1.0, len(milestones))
        t_func_sec = interp1d(s_milestones, [h * 3600.0 for h in milestone_physical_hours], kind="linear")

    radius_interp = interp1d(time_sec, radius_arr, kind="linear", fill_value="extrapolate")

    field_b64_uri = render_field_image(
        palette, time_sec, radius_arr, field_arr, grid_r,
        t_func_sec, first_angle, sweep_angle, plot_radius, r0_cm, res=2400
    )

    stops_hex = {
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
    }[palette]

    parts = []
    parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img" shape-rendering="geometricPrecision">'
    )
    parts.append(
        "<defs>"
        '<marker id="time-arrow" markerWidth="12" markerHeight="12" refX="10" refY="4" orient="auto">'
        '<path d="M0,0 L0,8 L11,4 z" fill="#314c5b"/>'
        "</marker>"
        '<linearGradient id="colorbar-gradient" x1="0" y1="1" x2="0" y2="0">'
        + "".join(f'<stop offset="{pos:.0%}" stop-color="{col}"/>' for pos, col in stops_hex)
        + "</linearGradient>"
        + "</defs>"
    )

    parts.append(f'<rect width="{width}" height="{height}" fill="#ffffff"/>')
    parts.append(f'<circle cx="{cx}" cy="{cy}" r="{plot_radius}" fill="none" stroke="#263f4c" stroke-width="2.2"/>')

    ref_concentric_r = [0.50, 1.00, 1.50]
    for r_cm in ref_concentric_r:
        r_px = plot_radius * (r_cm / r0_cm)
        rx0, ry0 = point(cx, cy, r_px, first_angle)
        rx1, ry1 = point(cx, cy, r_px, data_end_angle)
        parts.append(
            f'<path d="M {rx0:.2f},{ry0:.2f} A {r_px:.2f},{r_px:.2f} 0 1 1 {rx1:.2f},{ry1:.2f}" '
            f'fill="none" stroke="#a4b7c4" stroke-width="1.1" stroke-dasharray="3 4" stroke-opacity="0.50"/>'
        )

    # Embed smooth raster field
    field_x = cx - plot_radius
    field_y = cy - plot_radius
    field_dim = 2 * plot_radius
    parts.append(
        f'<image x="{field_x:.2f}" y="{field_y:.2f}" width="{field_dim:.2f}" height="{field_dim:.2f}" '
        f'href="{field_b64_uri}"/>'
    )

    # Concentric dashed rings inside the pizza
    num_eval_pts = 720
    d_phi = sweep_angle / num_eval_pts
    boundary_radii_px = []
    for i in range(num_eval_pts + 1):
        s_val = i / num_eval_pts
        t_val = float(t_func_sec(s_val))
        r_val = float(radius_interp(t_val))
        boundary_radii_px.append(plot_radius * (r_val / r0_cm))

    for r_cm in ref_concentric_r:
        r_px = plot_radius * (r_cm / r0_cm)
        arc_pts = []
        for i in range(num_eval_pts + 1):
            ang = first_angle + i * d_phi
            r_limit = boundary_radii_px[i]
            if r_px <= r_limit + 1.0:
                x, y = point(cx, cy, r_px, ang)
                arc_pts.append((x, y))
        if len(arc_pts) > 1:
            d_arc = f"M {arc_pts[0][0]:.2f},{arc_pts[0][1]:.2f} " + " ".join(f"L {p[0]:.2f},{p[1]:.2f}" for p in arc_pts[1:])
            parts.append(
                f'<path d="{d_arc}" fill="none" stroke="#ffffff" stroke-width="1.3" '
                'stroke-opacity="0.55" stroke-dasharray="4 5"/>'
            )

    # Milestone radial lines
    for s_m, label_str in zip(s_milestones, milestone_labels):
        ang_m = first_angle + s_m * sweep_angle
        t_m_sec = float(t_func_sec(s_m))
        r_m_cm = float(radius_interp(t_m_sec))
        r_m_px = plot_radius * (r_m_cm / r0_cm)

        x_tip, y_tip = point(cx, cy, r_m_px, ang_m)
        x_rim, y_rim = point(cx, cy, plot_radius, ang_m)

        parts.append(
            f'<line x1="{cx}" y1="{cy}" x2="{x_tip:.2f}" y2="{y_tip:.2f}" '
            'stroke="#ffffff" stroke-width="1.3" stroke-opacity="0.80"/>'
        )
        if r_m_px < plot_radius - 2.0:
            parts.append(
                f'<line x1="{x_tip:.2f}" y1="{y_tip:.2f}" x2="{x_rim:.2f}" y2="{y_rim:.2f}" '
                'stroke="#a0b4c2" stroke-width="1.1" stroke-dasharray="3 4" stroke-opacity="0.65"/>'
            )

        label_radius = 595.0
        lx, ly = point(cx, cy, label_radius, ang_m)
        angle_deg = (math.degrees(ang_m)) % 360.0
        rotation = angle_deg
        if 90.0 < angle_deg < 270.0:
            rotation += 180.0
        parts.append(
            f'<text x="{lx:.2f}" y="{ly:.2f}" text-anchor="middle" dominant-baseline="central" '
            f'transform="rotate({rotation:.2f} {lx:.2f} {ly:.2f})" '
            'font-family="Latin Modern Roman, CMU Serif, Computer Modern, serif" '
            f'font-size="42" font-weight="700" fill="#263f4c">'
            '<tspan font-style="italic">t</tspan>'
            f'<tspan xml:space="preserve"> = {label_str}</tspan></text>'
        )

    # Boundary outline of spiral
    spiral_pts = []
    for i in range(num_eval_pts + 1):
        ang = first_angle + i * d_phi
        r_limit = boundary_radii_px[i]
        x, y = point(cx, cy, r_limit, ang)
        spiral_pts.append(f"{x:.2f},{y:.2f}")

    start_pt = point(cx, cy, boundary_radii_px[0], first_angle)
    spiral_d = f"M {cx:.2f},{cy:.2f} L {start_pt[0]:.2f},{start_pt[1]:.2f} " + " ".join(f"L {pt}" for pt in spiral_pts) + f" L {cx:.2f},{cy:.2f} Z"
    parts.append(f'<path d="{spiral_d}" fill="none" stroke="#243b48" stroke-width="2.2"/>')

    # Ruler in gap
    gap_axis_ang = gap_center_angle
    ax0, ay0 = point(cx, cy, 0.0, gap_axis_ang)
    ax1, ay1 = point(cx, cy, plot_radius, gap_axis_ang)
    parts.append(f'<line x1="{ax0:.2f}" y1="{ay0:.2f}" x2="{ax1:.2f}" y2="{ay1:.2f}" stroke="#314c5b" stroke-width="2.0"/>')

    ang_tick = gap_axis_ang - math.pi / 2.0
    ruler_ticks = [(0.50, "0.5", False), (1.00, "1.0", False), (1.50, "1.5", False), (2.00, "2.0", True)]

    for r_cm, txt, is_max in ruler_ticks:
        r_px = plot_radius * (r_cm / r0_cm)
        tx, ty = point(cx, cy, r_px, gap_axis_ang)
        tick_len = 16.0 if is_max else 11.0
        tx1 = tx + tick_len * math.sin(ang_tick)
        ty1 = ty - tick_len * math.cos(ang_tick)
        parts.append(f'<line x1="{tx:.2f}" y1="{ty:.2f}" x2="{tx1:.2f}" y2="{ty1:.2f}" stroke="#2a4353" stroke-width="{2.2 if is_max else 1.5}"/>')
        lx = tx1 - 10.0
        ly = ty1 + 1.0
        if is_max:
            parts.append(
                f'<text x="{lx - 4:.2f}" y="{ly - 10:.2f}" text-anchor="end" dominant-baseline="central" '
                'font-family="Latin Modern Roman, CMU Serif, Computer Modern, serif" '
                'font-size="31" font-weight="700" fill="#203744">'
                '<tspan font-style="italic">R</tspan>₀ = 2.0 cm</text>'
            )
        else:
            parts.append(
                f'<text x="{lx:.2f}" y="{ly:.2f}" text-anchor="end" dominant-baseline="central" '
                'font-family="Latin Modern Roman, CMU Serif, Computer Modern, serif" '
                f'font-size="26" font-weight="600" fill="#465e6d">{txt}</text>'
            )

    norm_above_x = -math.sin(ang_tick)
    norm_above_y = math.cos(ang_tick)
    rx_mid, ry_mid = point(cx, cy, plot_radius * 0.54, gap_axis_ang)
    lbl_x = rx_mid + 32.0 * norm_above_x
    lbl_y = ry_mid + 32.0 * norm_above_y
    parts.append(
        f'<text x="{lbl_x:.2f}" y="{lbl_y:.2f}" text-anchor="middle" dominant-baseline="central" '
        f'transform="rotate(45 {lbl_x:.2f} {lbl_y:.2f})" xml:space="preserve" '
        'font-family="Latin Modern Roman, CMU Serif, Computer Modern, serif" '
        'font-size="28" font-weight="700" fill="#2a4353">'
        '<tspan font-style="italic">r</tspan>'
        '<tspan font-weight="400">&#160;(cm)</tspan></text>'
    )

    # Time arrow
    arrow_radius = 648.0
    arrow_start = first_angle + 0.05 * sweep_angle
    arrow_end = arrow_start + math.radians(22.0)
    arrow_x0, arrow_y0 = point(cx, cy, arrow_radius, arrow_start)
    arrow_x1, arrow_y1 = point(cx, cy, arrow_radius, arrow_end)
    parts.append(
        f'<path d="M {arrow_x0:.2f},{arrow_y0:.2f} A {arrow_radius:.2f},{arrow_radius:.2f} 0 0 1 {arrow_x1:.2f},{arrow_y1:.2f}" '
        'fill="none" stroke="#314c5b" stroke-width="4.0" marker-end="url(#time-arrow)"/>'
    )

    # Colorbar
    colorbar_x, colorbar_y = 1395.0, 145.0
    colorbar_width, colorbar_height = 72.0, 1110.0
    parts.append(
        f'<text x="{colorbar_x + colorbar_width / 2:.2f}" y="{colorbar_y + colorbar_height + 70:.2f}" '
        'text-anchor="middle" font-size="35" fill="#263f4c">'
        '<tspan font-family="Microsoft YaHei, 微软雅黑, PingFang SC, sans-serif" font-weight="600">'
        f'{scale["label_cn"]}</tspan>'
        '<tspan dx="13" font-family="Latin Modern Roman, CMU Serif, Computer Modern, serif" font-weight="400">'
        f'{scale["unit"]}</tspan></text>'
    )
    parts.append(
        f'<rect x="{colorbar_x}" y="{colorbar_y}" width="{colorbar_width}" '
        f'height="{colorbar_height}" fill="url(#colorbar-gradient)" stroke="#314c5b" stroke-width="1.4"/>'
    )
    for tick in scale["ticks"]:
        tick_value = float(tick)
        y = colorbar_y + colorbar_height * (1.0 - (tick_value - data_min) / (data_max - data_min))
        parts.append(
            f'<line x1="{colorbar_x + colorbar_width}" y1="{y:.2f}" '
            f'x2="{colorbar_x + colorbar_width + 17}" y2="{y:.2f}" stroke="#314c5b" stroke-width="1.8"/>'
        )
        tick_label = f'{tick_value:.{int(scale["decimals"])}f}'
        parts.append(
            f'<text x="{colorbar_x + colorbar_width + 31}" y="{y:.2f}" dominant-baseline="central" '
            f'font-family="Latin Modern Roman, CMU Serif, Computer Modern, serif" '
            f'font-size="31" fill="#263f4c">{tick_label}</text>'
        )

    parts.append("</svg>")
    return "\n".join(parts)

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input",
        type=Path,
        default=Path(__file__).with_name("q4_solution_data.npz"),
        help="Problem 4 solution npz file",
    )
    parser.add_argument(
        "--palette",
        choices=tuple(PALETTES),
        default=None,
        help="Colour palette for the field",
    )
    args = parser.parse_args()

    palettes = [args.palette] if args.palette else ["coolwarm", "thermal"]
    chrome = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    cur_dir = Path(__file__).resolve().parent

    for pal in palettes:
        svg_name = "q4_moisture_pizza.svg" if pal == "coolwarm" else "q4_temperature_pizza.svg"
        png_name = "q4_moisture_pizza.png" if pal == "coolwarm" else "q4_temperature_pizza.png"
        out_svg = (cur_dir / svg_name).resolve()
        out_png = (cur_dir / png_name).resolve()

        svg_str = make_pizza_svg(pal, args.input)
        out_svg.write_text(svg_str, encoding="utf-8")
        print(f"Wrote {out_svg}")

        if Path(chrome).exists():
            subprocess.run([
                chrome, "--headless", "--disable-gpu", "--force-device-scale-factor=2",
                "--window-size=1680,1400", f"--screenshot={out_png}", out_svg.as_uri()
            ], check=True)
            print(f"Rendered {out_png}")


if __name__ == "__main__":
    main()
