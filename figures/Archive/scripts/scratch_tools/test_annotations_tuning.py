import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Wedge, Arc, FancyArrowPatch
from PIL import Image
import shutil

SCRATCH = r"C:\Users\kqdx\.gemini\antigravity\brain\984f8f9b-1caf-4e5e-a827-7c48f241b73b\scratch"
EDA_DIR = r"D:\HIT\数模2026\eda_figures"
src_img_path = os.path.join(EDA_DIR, "fvm_flux_flared_c2_refined.png")

img = Image.open(src_img_path)
W, H = img.size

def render_annotated(style="slash", out_name="test_v1.png"):
    fig, ax = plt.subplots(figsize=(12, 12), dpi=300)
    ax.imshow(img)
    ax.set_xlim(0, W)
    ax.set_ylim(H, 0)
    ax.axis('off')

    plt.rcParams['mathtext.fontset'] = 'cm'
    plt.rcParams['font.serif'] = ['Times New Roman', 'DejaVu Serif']
    plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'DejaVu Sans']

    # 1. Delta R on Near ring bottom
    p_bi = np.array([627.3, 1533.0])
    p_bo = np.array([909.6, 1633.8])
    ext_len = 85
    d_offset = 60

    # Extension lines
    ax.plot([p_bi[0], p_bi[0]], [p_bi[1], p_bi[1] + ext_len],
            color='#333333', linestyle='--', linewidth=1.2, zorder=5)
    ax.plot([p_bo[0], p_bo[0]], [p_bo[1], p_bo[1] + ext_len],
            color='#333333', linestyle='--', linewidth=1.2, zorder=5)

    dim_p1 = p_bi + np.array([0, d_offset])
    dim_p2 = p_bo + np.array([0, d_offset])

    ax.annotate('', xy=dim_p1, xytext=dim_p2,
                arrowprops=dict(arrowstyle='<->', color='#000000', lw=1.5, shrinkA=0, shrinkB=0),
                zorder=6)

    dim_mid = (dim_p1 + dim_p2) / 2
    ax.text(dim_mid[0], dim_mid[1] + 32, r'$\Delta r$', fontsize=20, fontweight='bold',
            color='#000000', ha='center', va='top', zorder=7)

    # 2. Delta Z on Far ring left edge
    p_ti = np.array([619.4, 334.0])
    p_bi_far = np.array([621.7, 689.5])
    ext_len_z = 85
    d_offset_z = 60

    ax.plot([p_ti[0], p_ti[0] - ext_len_z], [p_ti[1], p_ti[1]],
            color='#333333', linestyle='--', linewidth=1.2, zorder=5)
    ax.plot([p_bi_far[0], p_bi_far[0] - ext_len_z], [p_bi_far[1], p_bi_far[1]],
            color='#333333', linestyle='--', linewidth=1.2, zorder=5)

    dim_z1 = p_ti - np.array([d_offset_z, 0])
    dim_z2 = p_bi_far - np.array([d_offset_z, 0])

    ax.annotate('', xy=dim_z1, xytext=dim_z2,
                arrowprops=dict(arrowstyle='<->', color='#000000', lw=1.5, shrinkA=0, shrinkB=0),
                zorder=6)

    dim_mid_z = (dim_z1 + dim_z2) / 2
    ax.text(dim_mid_z[0] - 18, dim_mid_z[1], r'$\Delta z$', fontsize=20, fontweight='bold',
            color='#000000', ha='right', va='center', zorder=7)

    # 3. Heat flux labels
    # Standard bright pure red
    c_red = '#E01010'
    
    if style == "slash":
        lbl_east = r'$Q_{i+1/2,\, j}$'
        lbl_west = r'$Q_{i-1/2,\, j}$'
        lbl_north = r'$Q_{i,\, j+1/2}$'
        lbl_south = r'$Q_{i,\, j-1/2}$'
        fsize = 19
    else:
        lbl_east = r'$Q_{i+\frac{1}{2},\, j}$'
        lbl_west = r'$Q_{i-\frac{1}{2},\, j}$'
        lbl_north = r'$Q_{i,\, j+\frac{1}{2}}$'
        lbl_south = r'$Q_{i,\, j-\frac{1}{2}}$'
        fsize = 18

    # East inflow (Right arrow): above arrow stem in outer ring face
    ax.text(1080, 930, lbl_east, fontsize=fsize, color=c_red, fontweight='bold', ha='center', va='bottom', zorder=8)

    # West outflow (Left arrow): above arrow stem in inner ring face
    ax.text(485, 880, lbl_west, fontsize=fsize, color=c_red, fontweight='bold', ha='center', va='bottom', zorder=8)

    # North inflow (Top arrow): inside Far ring face, above the top arrow
    ax.text(820, 560, lbl_north, fontsize=fsize, color=c_red, fontweight='bold', ha='center', va='center', zorder=8)

    # South outflow (Bottom arrow): inside Near ring face, right of the bottom arrow
    ax.text(850, 1380, lbl_south, fontsize=fsize, color=c_red, fontweight='bold', ha='left', va='center', zorder=8)

    # 4. Axis of symmetry (centerline on left)
    # Ends cleanly above the coordinate system to avoid visual clutter
    ax.plot([120, 120], [220, 1380], color='#555555', linestyle='-.', linewidth=1.5, zorder=2)
    ax.text(130, 240, r'$r = 0$' + '\n(中心对称轴 / Axis of Symmetry)', fontsize=13, color='#444444', ha='left', va='top')

    # 5. Upgraded Cylindrical Coordinate Frame with 3D Sector (扇形面)
    orig = np.array([170, 1660])

    # Vertical Z-axis
    z_top = orig + np.array([0, -180])
    ax.annotate('', xy=z_top, xytext=orig,
                arrowprops=dict(arrowstyle='->', color='#000000', lw=2.2, mutation_scale=18),
                zorder=6)
    ax.text(z_top[0], z_top[1] - 15, r'$+z$', fontsize=19, fontweight='bold', color='#000000', ha='center', va='bottom')

    # 3D Perspective Sector on the horizontal plane
    r_len = 145
    # Radial ray 1 (front edge, along perspective cut angle)
    ray1 = orig + np.array([r_len * np.cos(np.radians(20)), r_len * np.sin(np.radians(20)) * 0.48])
    # Radial ray 2 (far cut edge, sweep ~50 deg)
    ray2 = orig + np.array([r_len * np.cos(np.radians(-28)), r_len * np.sin(np.radians(-28)) * 0.48])

    theta_angles = np.linspace(np.radians(-28), np.radians(20), 50)
    arc_pts_x = orig[0] + r_len * np.cos(theta_angles)
    arc_pts_y = orig[1] + r_len * np.sin(theta_angles) * 0.48

    sector_poly_x = [orig[0]] + list(arc_pts_x) + [orig[0]]
    sector_poly_y = [orig[1]] + list(arc_pts_y) + [orig[1]]
    ax.fill(sector_poly_x, sector_poly_y, color='#EBF3FB', alpha=0.85, zorder=4)
    ax.plot(sector_poly_x, sector_poly_y, color='#3B6077', linewidth=1.4, zorder=5)

    # Ray 1 with arrow (+r)
    ax.annotate('', xy=ray1, xytext=orig,
                arrowprops=dict(arrowstyle='->', color='#000000', lw=2.0, mutation_scale=16),
                zorder=6)
    ax.text(ray1[0] + 16, ray1[1] + 6, r'$+r$', fontsize=19, fontweight='bold', color='#000000', ha='left', va='center')

    # Azimuthal rotation arrow (+theta)
    ax.annotate('', xy=(arc_pts_x[-1], arc_pts_y[-1]), xytext=(arc_pts_x[0], arc_pts_y[0]),
                arrowprops=dict(arrowstyle='->', color='#2F566B', lw=1.4, connectionstyle='arc3,rad=-0.32', mutation_scale=12),
                zorder=6)
    mid_idx = len(arc_pts_x) // 2
    ax.text(arc_pts_x[mid_idx] + 18, arc_pts_y[mid_idx] - 14, r'$+\theta$', fontsize=15, fontweight='bold', color='#2F566B', ha='left', va='bottom')

    out_png = os.path.join(SCRATCH, out_name)
    fig.savefig(out_png, dpi=300, bbox_inches='tight', pad_inches=0.02)
    plt.close(fig)
    print(f"Saved {out_png}")

render_annotated(style="slash", out_name="test_slash.png")
render_annotated(style="fraction", out_name="test_fraction.png")
