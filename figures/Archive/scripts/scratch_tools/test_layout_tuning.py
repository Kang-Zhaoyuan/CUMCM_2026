import os
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image

SCRATCH = r"C:\Users\kqdx\.gemini\antigravity\brain\984f8f9b-1caf-4e5e-a827-7c48f241b73b\scratch"
EDA_DIR = r"D:\HIT\数模2026\eda_figures"
base_img_path = os.path.join(EDA_DIR, "fvm_flux_flared_c2_refined.png")

img = Image.open(base_img_path)
W, H = img.size

def render_options(aligned=False, out_name="test_opt.png"):
    fig, ax = plt.subplots(figsize=(12, 12), dpi=300)
    ax.imshow(img)
    ax.set_xlim(0, W)
    ax.set_ylim(H, 0)
    ax.axis('off')

    plt.rcParams['mathtext.fontset'] = 'cm'
    plt.rcParams['font.serif'] = ['Times New Roman', 'DejaVu Serif']
    plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'DejaVu Sans']

    # 1. Radial Dimension on Near ring
    p_bi = np.array([627.3, 1533.0])
    p_bo = np.array([909.6, 1633.8])
    ext_len_r = 90
    d_offset_r = 60

    ax.plot([p_bi[0], p_bi[0]], [p_bi[1], p_bi[1] + ext_len_r],
            color='#333333', linestyle='--', linewidth=1.2, zorder=5)
    ax.plot([p_bo[0], p_bo[0]], [p_bo[1], p_bo[1] + ext_len_r],
            color='#333333', linestyle='--', linewidth=1.2, zorder=5)

    dim_r1 = p_bi + np.array([0, d_offset_r])
    dim_r2 = p_bo + np.array([0, d_offset_r])

    ax.annotate('', xy=dim_r1, xytext=dim_r2,
                arrowprops=dict(arrowstyle='<->', color='#000000', lw=1.5, shrinkA=0, shrinkB=0),
                zorder=6)

    dim_mid_r = (dim_r1 + dim_r2) / 2

    if aligned:
        # Rotated parallel to dimension line (-19.65 deg in display space)
        ax.text(dim_mid_r[0] - 8, dim_mid_r[1] + 28, r'$r_{i+1/2} - r_{i-1/2}$',
                fontsize=17, fontweight='bold', color='#000000', ha='center', va='top',
                rotation=-19.65, zorder=7)
    else:
        # Horizontal text, shifted slightly left to clear right dashed line completely
        ax.text(dim_mid_r[0] - 25, dim_mid_r[1] + 36, r'$r_{i+1/2} - r_{i-1/2}$',
                fontsize=17, fontweight='bold', color='#000000', ha='center', va='top', zorder=7)

    # 2. Axial Dimension on Outer ring (silhouette line)
    p_sil_top = np.array([1594.6, 739.7])
    p_sil_bot = np.array([1578.9, 1057.4])
    ext_len_z = 55
    d_offset_z = 35

    ax.plot([p_sil_top[0], p_sil_top[0] + ext_len_z], [p_sil_top[1], p_sil_top[1]],
            color='#333333', linestyle='--', linewidth=1.2, zorder=5)
    ax.plot([p_sil_bot[0], p_sil_bot[0] + ext_len_z], [p_sil_bot[1], p_sil_bot[1]],
            color='#333333', linestyle='--', linewidth=1.2, zorder=5)

    dim_z1 = p_sil_top + np.array([d_offset_z, 0])
    dim_z2 = p_sil_bot + np.array([d_offset_z, 0])

    ax.annotate('', xy=dim_z1, xytext=dim_z2,
                arrowprops=dict(arrowstyle='<->', color='#000000', lw=1.5, shrinkA=0, shrinkB=0),
                zorder=6)

    dim_mid_z = (dim_z1 + dim_z2) / 2
    ax.text(dim_mid_z[0] + 12, dim_mid_z[1], r'$z_{j+1/2} - z_{j-1/2}$',
            fontsize=17, fontweight='bold', color='#000000', ha='left', va='center', zorder=7)

    # 3. Coordinate System (Bottom-Left)
    orig = np.array([170, 1660])
    z_top = orig + np.array([0, -180])
    ax.annotate('', xy=z_top, xytext=orig,
                arrowprops=dict(arrowstyle='->', color='#000000', lw=2.2, mutation_scale=18),
                zorder=6)
    ax.text(z_top[0], z_top[1] - 15, r'$+z$', fontsize=20, fontweight='bold', color='#000000', ha='center', va='bottom')

    r_len = 150
    ray1 = orig + np.array([r_len * np.cos(np.radians(20)), r_len * np.sin(np.radians(20)) * 0.48])
    ray2 = orig + np.array([r_len * np.cos(np.radians(-28)), r_len * np.sin(np.radians(-28)) * 0.48])

    theta_angles = np.linspace(np.radians(-28), np.radians(20), 50)
    arc_pts_x = orig[0] + r_len * np.cos(theta_angles)
    arc_pts_y = orig[1] + r_len * np.sin(theta_angles) * 0.48

    sector_poly_x = [orig[0]] + list(arc_pts_x) + [orig[0]]
    sector_poly_y = [orig[1]] + list(arc_pts_y) + [orig[1]]
    ax.fill(sector_poly_x, sector_poly_y, color='#EBF3FB', alpha=0.85, zorder=4)
    ax.plot(sector_poly_x, sector_poly_y, color='#3B6077', linewidth=1.4, zorder=5)

    ax.annotate('', xy=ray1, xytext=orig,
                arrowprops=dict(arrowstyle='->', color='#000000', lw=2.0, mutation_scale=16),
                zorder=6)
    ax.text(ray1[0] + 16, ray1[1] + 6, r'$+r$', fontsize=20, fontweight='bold', color='#000000', ha='left', va='center')

    # 4. Heat Fluxes Q: Collinear with symmetry axes
    c_red = '#E01010'
    fsize = 19

    # Top: axis x = 765.0
    ax.text(765.0, 515, r'$Q_{i,\, j+1/2}$',
            fontsize=fsize, color=c_red, fontweight='bold', ha='center', va='center', zorder=8)

    # Bottom: axis x = 764.5
    ax.text(764.5, 1445, r'$Q_{i,\, j-1/2}$',
            fontsize=fsize, color=c_red, fontweight='bold', ha='center', va='center', zorder=8)

    # Left: line y = 0.2146 * x + 820.72
    ax.text(410.0, 0.2146 * 410.0 + 820.72, r'$Q_{i-1/2,\, j}$',
            fontsize=fsize, color=c_red, fontweight='bold', ha='center', va='center', zorder=8)

    # Right: line y = 0.2146 * x + 820.72
    ax.text(1210.0, 0.2146 * 1210.0 + 820.72, r'$Q_{i+1/2,\, j}$',
            fontsize=fsize, color=c_red, fontweight='bold', ha='center', va='center', zorder=8)

    out_png = os.path.join(SCRATCH, out_name)
    fig.savefig(out_png, dpi=300, bbox_inches='tight', pad_inches=0.02)
    plt.close(fig)
    print(f"Saved {out_png}")

render_options(aligned=False, out_name="test_opt_horiz.png")
render_options(aligned=True, out_name="test_opt_aligned.png")
