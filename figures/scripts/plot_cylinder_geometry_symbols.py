"""
Publication-grade 3D cylinder geometry and symbols diagram for CUMCM 2026 Problem A.
Frozen view: elev = -30.0, azim = -126.5, roll = 0.0, aspect_ratio = 3.60.
Refined line weights matching interactive HTML viewer.
Minimalist, pure scientific symbols (Zero formula overload, <= 3 colors).
"""

import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from PIL import Image
from matplotlib.patches import FancyArrowPatch
from mpl_toolkits.mplot3d.proj3d import proj_transform
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from mpl_toolkits.mplot3d import Axes3D

class Arrow3D(FancyArrowPatch):
    def __init__(self, xs, ys, zs, *args, **kwargs):
        super().__init__((0, 0), (0, 0), shrinkA=0, shrinkB=0, *args, **kwargs)
        self._verts3d = xs, ys, zs

    def do_3d_projection(self, renderer=None):
        xs3d, ys3d, zs3d = self._verts3d
        xs, ys, zs = proj_transform(xs3d, ys3d, zs3d, self.axes.M)
        self.set_positions((xs[0], ys[0]), (xs[1], ys[1]))
        return 50.0

def render_cylinder(has_meridians=False, base_center_label=None, L_half=7.5, theta_arrow_style='->', out_path='cylinder_geometry_symbols_dot_only.png'):
    # LaTeX Computer Modern font styling
    plt.rcParams['mathtext.fontset'] = 'cm'
    plt.rcParams['font.family'] = 'serif'
    plt.rcParams['font.serif'] = ['Times New Roman', 'DejaVu Serif', 'STIXGeneral']
    plt.rcParams['axes.unicode_minus'] = False

    fig = plt.figure(figsize=(24.0, 7.5), dpi=300)
    ax = fig.add_subplot(111, projection='3d')

    R = 1.0
    elev = -30.0
    azim = -126.5

    # Palette (Strict scientific palette: <= 3 colors)
    c_black = '#0f172a'        # Color 1: Deep Slate Black (main contours, coordinates, text)
    c_slate = '#64748b'        # Color 2: Slate Gray (layers, dimension lines, ticks)
    c_meridian = '#94a3b8'     # Lighter Slate Gray for subtle surface meridians
    c_red = '#d63031'          # Color 3: Crimson Red (origin O focus)

    # Line weights
    lw_main = 1.55       # Main silhouette & cut outlines
    lw_inner_dash = 1.15 # Occluded base arc
    lw_layer = 0.90      # Concentric gradient shells
    lw_dim = 1.15        # Engineering dimension lines

    # Camera silhouette calculation
    elev_rad = np.deg2rad(elev)
    azim_rad = np.deg2rad(azim)
    ce, se = np.cos(elev_rad), np.sin(elev_rad)
    sa = np.sin(azim_rad)
    dy = -ce * sa
    dz = -se
    th1 = np.arctan2(dy, -dz) % (2 * np.pi)
    th2 = (th1 + np.pi) % (2 * np.pi)
    if th1 > th2:
        th1, th2 = th2, th1

    # Silhouette generator line coordinates
    y_top = R * np.cos(th1)
    z_top = R * np.sin(th1)
    y_bot = R * np.cos(th2)
    z_bot = R * np.sin(th2)

    # -------------------------------------------------------------
    # 1. Concentric Radial Shells (2 uniform gray layers at R/3, 2R/3)
    # -------------------------------------------------------------
    radii = [R / 3.0, 2.0 * R / 3.0]
    th_cut = np.linspace(0, np.pi / 2, 40)
    theta_3oct = np.linspace(np.pi / 2, 2 * np.pi, 70)

    for r in radii:
        # Midplane quarter-arc at z = 0
        ax.plot(np.zeros_like(th_cut), r * np.cos(th_cut), r * np.sin(th_cut),
                color=c_slate, lw=lw_layer, ls='-', zorder=12)
        # Horizontal cut shelf line (z in [0, L_half])
        ax.plot([0, L_half], [r, r], [0, 0],
                color=c_slate, lw=lw_layer, ls=(0, (3.5, 2.5)), zorder=12)
        # Vertical cut wall line (z in [0, L_half])
        ax.plot([0, L_half], [0, 0], [r, r],
                color=c_slate, lw=lw_layer, ls=(0, (3.5, 2.5)), zorder=12)
        # Right end cap 270-degree concentric arc (z = L_half)
        ax.plot(np.full_like(theta_3oct, L_half), r * np.cos(theta_3oct), r * np.sin(theta_3oct),
                color=c_slate, lw=lw_layer, ls='-', zorder=12)

    # -------------------------------------------------------------
    # 2. Surface Meridians (母线) - Optional 6 lines every 60 degrees
    # -------------------------------------------------------------
    if has_meridians:
        meridian_degs = [30, 90, 150, 210, 270, 330]
        for deg in meridian_degs:
            th = np.deg2rad(deg)
            ym = R * np.cos(th)
            zm = R * np.sin(th)
            ax.plot([-L_half, 0], [ym, ym], [zm, zm],
                    color=c_meridian, lw=0.85, ls=(0, (3.0, 3.0)), zorder=9)
            if deg >= 90:
                ax.plot([0, L_half], [ym, ym], [zm, zm],
                        color=c_meridian, lw=0.85, ls=(0, (3.0, 3.0)), zorder=9)

    # -------------------------------------------------------------
    # 3. Left End Cap (z = -L_half): Full Circular Base
    # -------------------------------------------------------------
    arc_inner = np.linspace(th1, th2, 60)
    arc_outer = np.linspace(th2, th1 + 2 * np.pi, 60)
    # Inner occluded arc -> Dashed
    ax.plot(np.full_like(arc_inner, -L_half), R * np.cos(arc_inner), R * np.sin(arc_inner),
            color=c_black, lw=lw_inner_dash, ls=(0, (3.5, 2.5)), zorder=10)
    # Outer visible silhouette arc -> Solid
    ax.plot(np.full_like(arc_outer, -L_half), R * np.cos(arc_outer), R * np.sin(arc_outer),
            color=c_black, lw=lw_main, ls='-', zorder=10)

    # Base Center Marking at (-L_half, 0, 0)
    ax.plot([-L_half], [0], [0], marker='o', markersize=5.2, color=c_black, markeredgecolor='white', markeredgewidth=0.8, zorder=35)
    if base_center_label == "O_prime":
        ax.text(-L_half + 0.16, 0.14, -0.20, r"$O'$", color=c_black, fontsize=12.5, fontweight='bold', zorder=35,
                path_effects=[pe.withStroke(linewidth=2.8, foreground='white')])

    # -------------------------------------------------------------
    # 4. Outer Silhouette Generator Lines (母线)
    # -------------------------------------------------------------
    for th in [th1, th2]:
        y = R * np.cos(th)
        z = R * np.sin(th)
        # Left half generator line: from -L_half to 0
        ax.plot([-L_half, 0], [y, y], [z, z], color=c_black, lw=lw_main, ls='-', zorder=10)
        # Right half generator line: exists for theta in [pi/2, 2*pi]
        if th >= np.pi / 2 and th <= 2 * np.pi:
            ax.plot([0, L_half], [y, y], [z, z], color=c_black, lw=lw_main, ls='-', zorder=10)

    # -------------------------------------------------------------
    # 5. 7-Octant Cutaway Sharp Edges
    # -------------------------------------------------------------
    # Internal corner along cylinder axis inside cut: (0,0,0) to (L_half, 0, 0)
    ax.plot([0, L_half], [0, 0], [0, 0], color=c_black, lw=lw_main * 1.15, ls='-', zorder=15)
    # Midplane radial cuts at z = 0
    ax.plot([0, 0], [0, R], [0, 0], color=c_black, lw=lw_main, ls='-', zorder=15)
    ax.plot([0, 0], [0, 0], [0, R], color=c_black, lw=lw_main, ls='-', zorder=15)
    ax.plot(np.zeros_like(th_cut), R * np.cos(th_cut), R * np.sin(th_cut), color=c_black, lw=lw_main, ls='-', zorder=15)
    # Longitudinal shelf and wall outer edges
    ax.plot([0, L_half], [R, R], [0, 0], color=c_black, lw=lw_main, ls='-', zorder=15)
    ax.plot([0, L_half], [0, 0], [R, R], color=c_black, lw=lw_main, ls='-', zorder=15)

    # -------------------------------------------------------------
    # 6. Right End Cap (z = L_half)
    # -------------------------------------------------------------
    ax.plot(np.full_like(theta_3oct, L_half), R * np.cos(theta_3oct), R * np.sin(theta_3oct),
            color=c_black, lw=lw_main, ls='-', zorder=15)
    ax.plot([L_half, L_half], [0, R], [0, 0], color=c_black, lw=lw_main, ls='-', zorder=15)
    ax.plot([L_half, L_half], [0, 0], [0, R], color=c_black, lw=lw_main, ls='-', zorder=15)

    # -------------------------------------------------------------
    # 7. Polar Coordinates (r, theta) on Midplane Cut (z = 0)
    # -------------------------------------------------------------
    # Red letter O: carefully positioned below-right of the origin with zero overlap to red dot
    ax.text(0.35, 0.45, -0.48, r'$O$', color=c_red, fontsize=13.5, fontweight='bold', zorder=40,
            path_effects=[pe.withStroke(linewidth=2.8, foreground='white')])

    # Radial axis +r rotated counter-clockwise on screen by ~30 deg (downwards away from shelf edge)
    th_r = np.deg2rad(-30.0)
    cos_r, sin_r = np.cos(th_r), np.sin(th_r)
    arr_r = Arrow3D([0, 0],
                    [0, 1.42 * R * cos_r],
                    [0, 1.42 * R * sin_r],
                    mutation_scale=13, lw=1.45, arrowstyle='-|>', color=c_black, zorder=35)
    ax.add_artist(arr_r)
    # Text r placed cleanly at tip with zero overlap
    ax.text(0, 1.68 * R * cos_r, 1.68 * R * sin_r,
            r'$r$', color=c_black, fontsize=13.5, fontweight='bold', ha='center', va='top', zorder=35,
            path_effects=[pe.withStroke(linewidth=2.8, foreground='white')])

    # Azimuthal angle theta arc & clean single arrow at 55 deg (shifted upper-left to eliminate overlap with cut shell)
    r_th = 1.34 * R
    th_start = np.deg2rad(2.0)
    th_end = np.deg2rad(55.0)
    th_arc_end = th_end - np.deg2rad(12.0)
    th_arc = np.linspace(th_start, th_arc_end, 30)
    ax.plot(np.zeros_like(th_arc), r_th * np.cos(th_arc), r_th * np.sin(th_arc),
            color=c_black, lw=1.35, zorder=26)

    arr_th = Arrow3D([0, 0],
                     [r_th * np.cos(th_arc_end), r_th * np.cos(th_end)],
                     [r_th * np.sin(th_arc_end), r_th * np.sin(th_end)],
                     mutation_scale=13, lw=1.45, arrowstyle=theta_arrow_style, color=c_black, zorder=35)
    ax.add_artist(arr_th)

    # Label theta shifted towards UPPER-LEFT, ensuring zero overlap with arc/arrow
    th_label_deg = 33.0
    th_label_rad = np.deg2rad(th_label_deg)
    r_label = 1.64 * R
    ax.text(0, r_label * np.cos(th_label_rad), r_label * np.sin(th_label_rad),
            r'$\theta$', color=c_black, fontsize=13.5, fontweight='bold', ha='right', va='center', zorder=30,
            path_effects=[pe.withStroke(linewidth=2.8, foreground='white')])

    # Origin Dot guaranteed on top layer (Line3D with zorder=100 ensures it is drawn on top of all lines)
    ax.plot([0], [0], [0], marker='o', markersize=6.8, color=c_red,
            markeredgecolor='white', markeredgewidth=1.2, zorder=100)

    # -------------------------------------------------------------
    # 8. Engineering Dimension: Diameter 2R at Cylinder Back (z = -L_half)
    # -------------------------------------------------------------
    d_ext_2r = 0.95
    d_dim_2r = 0.60

    # Collinear extension dashed lines extending along -x
    ax.plot([-L_half, -L_half - d_ext_2r], [y_top, y_top], [z_top, z_top],
            color=c_slate, lw=lw_dim, ls=(0, (3.5, 2.5)), zorder=20)
    ax.plot([-L_half, -L_half - d_ext_2r], [y_bot, y_bot], [z_bot, z_bot],
            color=c_slate, lw=lw_dim, ls=(0, (3.5, 2.5)), zorder=20)

    # Double-headed dimension arrow <-> across full diameter 2R
    arr_2r = Arrow3D([-L_half - d_dim_2r, -L_half - d_dim_2r],
                     [y_bot, y_top],
                     [z_bot, z_top],
                     mutation_scale=12, lw=1.4, arrowstyle='<->', color=c_black, zorder=30)
    ax.add_artist(arr_2r)

    # Value text 2R placed beside dimension line on the left
    ax.text(-L_half - d_dim_2r - 0.22, (y_top + y_bot) / 2.0, (z_top + z_bot) / 2.0,
            r'$2R$', color=c_black, fontsize=13, fontweight='bold', ha='right', va='center', zorder=35)

    # -------------------------------------------------------------
    # 9. Engineering Dimension: z-axis datum positions (-L/2, z = 0, +L/2)
    #    (Strict drafting standard: extension lines terminate cleanly, text floating above with halo)
    # -------------------------------------------------------------
    d_dim_z = 0.55
    d_ext_z = d_dim_z + 0.08  # Extension line only extends 0.08 past dimension line
    d_txt_z = d_dim_z + 0.20  # Text placed safely above the extension line tips

    ny = np.cos(th1)
    nz = np.sin(th1)

    # 1. Extension lines at -L/2 and +L/2
    for x_pos in [-L_half, L_half]:
        ax.plot([x_pos, x_pos],
                [y_top, y_top + d_ext_z * ny],
                [z_top, z_top + d_ext_z * nz],
                color=c_slate, lw=lw_dim, ls=(0, (3.5, 2.5)), zorder=20)

    # 2. Extension line at z = 0 (stops right at dimension line)
    ax.plot([0.0, 0.0],
            [y_top, y_top + d_dim_z * ny],
            [z_top, z_top + d_dim_z * nz],
            color=c_slate, lw=lw_dim, ls=(0, (3.5, 2.5)), zorder=20)

    # 3. Horizontal datum dimension line
    ax.plot([-L_half, L_half],
            [y_top + d_dim_z * ny, y_top + d_dim_z * ny],
            [z_top + d_dim_z * nz, z_top + d_dim_z * nz],
            color=c_slate, lw=lw_dim, ls=(0, (3.5, 2.5)), zorder=20)

    # 4. Tick mark at z = 0
    tick_half = 0.06
    ax.plot([0.0, 0.0],
            [y_top + (d_dim_z - tick_half) * ny, y_top + (d_dim_z + tick_half) * ny],
            [z_top + (d_dim_z - tick_half) * nz, z_top + (d_dim_z + tick_half) * nz],
            color=c_black, lw=lw_main, ls='-', zorder=25)

    # 5. Datum texts with white halos
    ax.text(-L_half, y_top + d_txt_z * ny, z_top + d_txt_z * nz,
            r'$-L/2$', color=c_black, fontsize=12, fontweight='bold', ha='center', va='bottom', zorder=30,
            path_effects=[pe.withStroke(linewidth=2.8, foreground='white')])
    ax.text(0.0, y_top + d_txt_z * ny, z_top + d_txt_z * nz,
            r'$z = 0$', color=c_black, fontsize=12.5, fontweight='bold', ha='center', va='bottom', zorder=30,
            path_effects=[pe.withStroke(linewidth=2.8, foreground='white')])
    ax.text(L_half, y_top + d_txt_z * ny, z_top + d_txt_z * nz,
            r'$+L/2$', color=c_black, fontsize=12, fontweight='bold', ha='center', va='bottom', zorder=30,
            path_effects=[pe.withStroke(linewidth=2.8, foreground='white')])

    # -------------------------------------------------------------
    # 10. Strict Isotropic 1:1:1 Data Scaling (True Circular Cylinder)
    # -------------------------------------------------------------
    yl = ax.get_ylim()
    zl = ax.get_zlim()

    # Enforce symmetric identical limits for Y and Z
    yz_max = max(abs(yl[0]), abs(yl[1]), abs(zl[0]), abs(zl[1])) * 1.05
    ax.set_ylim(-yz_max, yz_max)
    ax.set_zlim(-yz_max, yz_max)

    # Compute physical spans
    xl = ax.get_xlim()
    yl = ax.get_ylim()
    zl = ax.get_zlim()
    dx = xl[1] - xl[0]
    dy = yl[1] - yl[0]
    dz = zl[1] - zl[0]

    # Equal scale across all 3 axes: scale_x == scale_y == scale_z
    ax.set_box_aspect((dx, dy, dz))

    # View configuration & render
    ax.axis('off')
    ax.view_init(elev=elev, azim=azim, roll=0.0)

    plt.savefig(out_path, bbox_inches='tight', dpi=300, facecolor='white')
    plt.close()

    # Auto-crop to flat publication-grade landscape aspect ratio (padding = 45px)
    try:
        raw_img = Image.open(out_path)
        arr = np.array(raw_img.convert('RGB'))
        non_white = np.any(arr < 250, axis=2)
        rows = np.where(non_white.any(axis=1))[0]
        cols = np.where(non_white.any(axis=0))[0]
        if len(rows) > 0 and len(cols) > 0:
            pad = 45
            box = (
                max(0, int(cols.min()) - pad),
                max(0, int(rows.min()) - pad),
                min(raw_img.width, int(cols.max()) + pad),
                min(raw_img.height, int(rows.max()) + pad)
            )
            cropped_img = raw_img.crop(box)
            cropped_img.save(out_path)
            print(f'Successfully cropped to flat aspect {cropped_img.width}x{cropped_img.height} (ratio: {cropped_img.width/cropped_img.height:.2f}): {out_path}')
    except Exception as e:
        print(f'Cropping fallback: {e}')

def main():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    
    # Primary frozen version: dot_only with open single arrow (->), no meridians, no base center label
    path_dot_only = os.path.join(base_dir, 'cylinder_geometry_symbols_dot_only.png')
    render_cylinder(has_meridians=False, base_center_label=None, theta_arrow_style='->', out_path=path_dot_only)
    print(f'>>> Successfully generated frozen figure: {path_dot_only}')

if __name__ == '__main__':
    main()
