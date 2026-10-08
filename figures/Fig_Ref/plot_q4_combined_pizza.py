#!/usr/bin/env python3
"""Generate a publication-quality 1x2 combined panel for Problem 4.

Layout:
- Left: 含水率分布演变 (Moisture Field Evolution) - with R0 = 2 cm, r (cm), and 0.5, 1.0, 1.5
- Right: 温度分布演变 (Temperature Field Evolution) - with clean axis and 0.5, 1.0, 1.5 only
- Tailored for A4 page width (~160-165 mm):
  - Maximized circle diameters (~5.8 cm on printed A4).
  - Prominent, enlarged colorbar scale annotations (numbers, ticks, units).
  - Rotated 45-degree scale numbers along ruler, completely eliminating pizza overlap.
  - Asymmetric ruler annotation (Left retains full symbols, Right keeps minimal coordinates).
  - Seamless continuous scalar field with zero moire artifacts.
"""

from __future__ import annotations

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

PALETTES_HEX = {
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

def map_colors(val_arr: np.ndarray, palette: str, vmin: float, vmax: float) -> np.ndarray:
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

    dist_to_edge = r_limit_px[mask] - r_pix[mask]
    alpha = np.clip((dist_to_edge + 0.5) / 1.0, 0.0, 1.0) * 255.0
    rgba[mask, 3] = alpha.astype(np.uint8)

    img = Image.fromarray(rgba, mode="RGBA")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    b64 = base64.b64encode(buf.getvalue()).decode("ascii")
    return f"data:image/png;base64,{b64}"

def generate_subpanel_svg(
    palette: str,
    cx: float,
    cy: float,
    plot_radius: float,
    cb_x: float,
    cb_y: float,
    cb_w: float,
    cb_h: float,
    time_sec: np.ndarray,
    radius_arr: np.ndarray,
    field_arr: np.ndarray,
    grid_r: np.ndarray,
    is_left: bool = True,
) -> list[str]:
    r0_cm = 2.0
    gap_center_angle = math.radians(-45.0)
    gap_width_rad = math.radians(34.2857)
    first_angle = gap_center_angle + gap_width_rad / 2.0
    sweep_angle = 2.0 * math.pi - gap_width_rad
    data_end_angle = first_angle + sweep_angle

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
        milestone_physical_hours = [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0]
        milestone_labels = [m[1] for m in milestones]
        s_milestones = np.linspace(0.0, 1.0, len(milestones))
        t_func_sec = interp1d(s_milestones, [h * 3600.0 for h in milestone_physical_hours], kind="linear")

    radius_interp = interp1d(time_sec, radius_arr, kind="linear", fill_value="extrapolate")

    field_b64_uri = render_field_image(
        palette, time_sec, radius_arr, field_arr, grid_r,
        t_func_sec, first_angle, sweep_angle, plot_radius, r0_cm, res=2400
    )

    p = []
    # Outer circle reference
    p.append(f'<circle cx="{cx}" cy="{cy}" r="{plot_radius}" fill="none" stroke="#263f4c" stroke-width="2.2"/>')

    # Concentric reference arcs (void region)
    ref_concentric_r = [0.50, 1.00, 1.50]
    for r_cm in ref_concentric_r:
        r_px = plot_radius * (r_cm / r0_cm)
        rx0, ry0 = point(cx, cy, r_px, first_angle)
        rx1, ry1 = point(cx, cy, r_px, data_end_angle)
        p.append(
            f'<path d="M {rx0:.2f},{ry0:.2f} A {r_px:.2f},{r_px:.2f} 0 1 1 {rx1:.2f},{ry1:.2f}" '
            f'fill="none" stroke="#a4b7c4" stroke-width="1.1" stroke-dasharray="3 4" stroke-opacity="0.50"/>'
        )

    # Embed smooth raster field
    field_x = cx - plot_radius
    field_y = cy - plot_radius
    field_dim = 2 * plot_radius
    p.append(
        f'<image x="{field_x:.2f}" y="{field_y:.2f}" width="{field_dim:.2f}" height="{field_dim:.2f}" '
        f'href="{field_b64_uri}"/>'
    )

    # Concentric dashed rings inside pizza
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
            d_arc = f"M {arc_pts[0][0]:.2f},{arc_pts[0][1]:.2f} " + " ".join(f"L {pt[0]:.2f},{pt[1]:.2f}" for pt in arc_pts[1:])
            p.append(
                f'<path d="{d_arc}" fill="none" stroke="#ffffff" stroke-width="1.3" '
                'stroke-opacity="0.55" stroke-dasharray="4 5"/>'
            )

    # Milestone radial lines & labels
    for s_m, label_str in zip(s_milestones, milestone_labels):
        ang_m = first_angle + s_m * sweep_angle
        t_m_sec = float(t_func_sec(s_m))
        r_m_cm = float(radius_interp(t_m_sec))
        r_m_px = plot_radius * (r_m_cm / r0_cm)

        x_tip, y_tip = point(cx, cy, r_m_px, ang_m)
        x_rim, y_rim = point(cx, cy, plot_radius, ang_m)

        p.append(
            f'<line x1="{cx}" y1="{cy}" x2="{x_tip:.2f}" y2="{y_tip:.2f}" '
            'stroke="#ffffff" stroke-width="1.3" stroke-opacity="0.80"/>'
        )
        if r_m_px < plot_radius - 2.0:
            p.append(
                f'<line x1="{x_tip:.2f}" y1="{y_tip:.2f}" x2="{x_rim:.2f}" y2="{y_rim:.2f}" '
                'stroke="#a0b4c2" stroke-width="1.1" stroke-dasharray="3 4" stroke-opacity="0.65"/>'
            )

        label_radius = plot_radius + 40.0
        lx, ly = point(cx, cy, label_radius, ang_m)
        angle_deg = (math.degrees(ang_m)) % 360.0
        rotation = angle_deg
        if 90.0 < angle_deg < 270.0:
            rotation += 180.0
        p.append(
            f'<text x="{lx:.2f}" y="{ly:.2f}" text-anchor="middle" dominant-baseline="central" '
            f'transform="rotate({rotation:.2f} {lx:.2f} {ly:.2f})" '
            'font-family="Latin Modern Roman, CMU Serif, Computer Modern, serif" '
            f'font-size="39" font-weight="700" fill="#263f4c">'
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
    p.append(f'<path d="{spiral_d}" fill="none" stroke="#243b48" stroke-width="2.2"/>')

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

    return p

def make_q4_combined_svg(npz_path: Path) -> str:
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

    data = np.load(npz_path)
    time_sec = data["time"]
    radius_arr = data["current_radius_cm"]
    grid_r = data["radius_grid"]

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
        '<linearGradient id="cb-grad-coolwarm" x1="0" y1="1" x2="0" y2="0">'
        + "".join(f'<stop offset="{pos:.0%}" stop-color="{col}"/>' for pos, col in PALETTES_HEX["coolwarm"])
        + "</linearGradient>"
        '<linearGradient id="cb-grad-thermal" x1="0" y1="1" x2="0" y2="0">'
        + "".join(f'<stop offset="{pos:.0%}" stop-color="{col}"/>' for pos, col in PALETTES_HEX["thermal"])
        + "</linearGradient>"
        + "</defs>"
    )

    parts.append(f'<rect width="{width}" height="{height}" fill="#ffffff"/>')

    # Subpanel Left (Moisture - 含水率先行, is_left=True)
    panel_left = generate_subpanel_svg(
        "coolwarm", cx_left, cy, plot_radius, cb_x_left, cb_y_left, cb_w, cb_h,
        time_sec, radius_arr, data["moisture"], grid_r, is_left=True
    )
    parts.extend(panel_left)

    # Subpanel Right (Temperature - 温度在后, is_left=False)
    panel_right = generate_subpanel_svg(
        "thermal", cx_right, cy, plot_radius, cb_x_right, cb_y_right, cb_w, cb_h,
        time_sec, radius_arr, data["temperature"], grid_r, is_left=False
    )
    parts.extend(panel_right)

    parts.append("</svg>")
    return "\n".join(parts)

def main() -> None:
    script_dir = Path(__file__).resolve().parent
    npz_path = script_dir / "q4_solution_data.npz"
    svg_str = make_q4_combined_svg(npz_path)
    out_svg = script_dir / "q4_combined_pizza.svg"
    out_svg.write_text(svg_str, encoding="utf-8")
    print(f"Wrote {out_svg}")

    chrome = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    out_png = script_dir / "q4_combined_pizza.png"
    subprocess.run([
        chrome, "--headless", "--disable-gpu", "--force-device-scale-factor=2",
        "--window-size=3200,1380", f"--screenshot={out_png}", out_svg.as_uri()
    ], check=True)
    print(f"Rendered {out_png}")

if __name__ == "__main__":
    main()
