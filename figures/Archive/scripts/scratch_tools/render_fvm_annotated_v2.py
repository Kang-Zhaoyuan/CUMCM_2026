import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Wedge, Arc, FancyArrowPatch
from PIL import Image

SCRATCH = r"C:\Users\kqdx\.gemini\antigravity\brain\984f8f9b-1caf-4e5e-a827-7c48f241b73b\scratch"
EDA_DIR = r"D:\HIT\数模2026\eda_figures"
src_img_path = os.path.join(EDA_DIR, "fvm_flux_flared_c2_refined.png")

img = Image.open(src_img_path)
W, H = img.size

fig, ax = plt.subplots(figsize=(12, 12), dpi=300)
ax.imshow(img)
ax.set_xlim(0, W)
ax.set_ylim(H, 0)
ax.axis('off')

# Enable Computer Modern math rendering
plt.rcParams['mathtext.fontset'] = 'cm'
plt.rcParams['font.serif'] = ['Times New Roman', 'DejaVu Serif']
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'DejaVu Sans']

# =========================================================================
# 1. Engineering Dimensioning: Delta R on Near Ring (近环截面底部)
# Exact vertices:
# Bottom-inner: (627.3, 1533.0)
# Bottom-outer: (909.6, 1633.8)
# =========================================================================
p_bi = np.array([627.3, 1533.0])
p_bo = np.array([909.6, 1633.8])

# Extension direction: along the vertical side edge of the near ring
# Side edge direction is approximately straight down (0, 1)
ext_len = 90
d_offset = 65

# Extension lines (thin dashed lines extending from geometry vertices)
ax.plot([p_bi[0], p_bi[0]], [p_bi[1], p_bi[1] + ext_len],
        color='#333333', linestyle='--', linewidth=1.2, zorder=5)
ax.plot([p_bo[0], p_bo[0]], [p_bo[1], p_bo[1] + ext_len],
        color='#333333', linestyle='--', linewidth=1.2, zorder=5)

# Dimension line (parallel to bottom edge, shifted downwards by d_offset)
dim_p1 = p_bi + np.array([0, d_offset])
dim_p2 = p_bo + np.array([0, d_offset])

# Draw double-ended arrow for Delta R
ax.annotate('', xy=dim_p1, xytext=dim_p2,
            arrowprops=dict(arrowstyle='<->', color='#000000', lw=1.5, shrinkA=0, shrinkB=0),
            zorder=6)

# Text Delta R centered along dimension line
dim_mid = (dim_p1 + dim_p2) / 2
ax.text(dim_mid[0] - 10, dim_mid[1] + 35, r'$\Delta r$', fontsize=20, fontweight='bold',
        color='#000000', ha='center', va='top', zorder=7)

# =========================================================================
# 2. Engineering Dimensioning: Delta Z on Far Ring (远环截面厚度)
# Exact vertices on Left Edge of Far Ring front face:
# Top-inner: (619.4, 334.0)
# Bottom-inner: (621.7, 689.5)
# =========================================================================
p_ti = np.array([619.4, 334.0])
p_bi_far = np.array([621.7, 689.5])

# Extension direction: horizontally to the left (-1, 0)
ext_len_z = 90
d_offset_z = 65

# Extension lines (thin dashed lines extending to the left)
ax.plot([p_ti[0], p_ti[0] - ext_len_z], [p_ti[1], p_ti[1]],
        color='#333333', linestyle='--', linewidth=1.2, zorder=5)
ax.plot([p_bi_far[0], p_bi_far[0] - ext_len_z], [p_bi_far[1], p_bi_far[1]],
        color='#333333', linestyle='--', linewidth=1.2, zorder=5)

# Dimension line (vertical, offset to the left)
dim_z1 = p_ti - np.array([d_offset_z, 0])
dim_z2 = p_bi_far - np.array([d_offset_z, 0])

ax.annotate('', xy=dim_z1, xytext=dim_z2,
            arrowprops=dict(arrowstyle='<->', color='#000000', lw=1.5, shrinkA=0, shrinkB=0),
            zorder=6)

# Text Delta Z centered along vertical dimension line
dim_mid_z = (dim_z1 + dim_z2) / 2
ax.text(dim_mid_z[0] - 20, dim_mid_z[1], r'$\Delta z$', fontsize=20, fontweight='bold',
        color='#000000', ha='right', va='center', zorder=7)

# =========================================================================
# 3. Heat Flux LaTeX Annotations (Letter positions near 4 flared arrows)
# =========================================================================
# Inflow from East (Right Arrow)
ax.text(1070, 960, r'$Q_{i+\frac{1}{2},\, j}$', fontsize=18, color='#D31010', fontweight='bold', ha='center', va='bottom', zorder=8)

# Outflow to West (Left Arrow)
ax.text(490, 885, r'$Q_{i-\frac{1}{2},\, j}$', fontsize=17, color='#D31010', fontweight='bold', ha='center', va='bottom', zorder=8)

# Inflow from North (Top Arrow)
ax.text(820, 680, r'$Q_{i,\, j+\frac{1}{2}}$', fontsize=18, color='#D31010', fontweight='bold', ha='left', va='center', zorder=8)

# Outflow to South (Bottom Arrow)
ax.text(810, 1280, r'$Q_{i,\, j-\frac{1}{2}}$', fontsize=17, color='#D31010', fontweight='bold', ha='left', va='center', zorder=8)

# =========================================================================
# 4. Upgraded Cylindrical Coordinate Frame with 3D Sector (扇形坐标系)
# In bottom-left:
# Z-axis is vertical straight up.
# R-axis is a 3D perspective circular sector!
# =========================================================================
orig = np.array([170, 1660])

# Vertical Z-axis with arrow
z_top = orig + np.array([0, -180])
ax.annotate('', xy=z_top, xytext=orig,
            arrowprops=dict(arrowstyle='->', color='#000000', lw=2.2, mutation_scale=18),
            zorder=6)
ax.text(z_top[0], z_top[1] - 15, r'$+z$', fontsize=18, fontweight='bold', color='#000000', ha='center', va='bottom')

# 3D Sector on the horizontal plane:
# In 3D isometric/perspective:
# Radial ray 1 (along cut direction, matching theta = 60 cut face):
r_len = 130
ray1 = orig + np.array([r_len * np.cos(np.radians(20)), r_len * np.sin(np.radians(20)) * 0.5])
# Radial ray 2 (far cut edge, sweep 60 deg):
ray2 = orig + np.array([r_len * np.cos(np.radians(-25)), r_len * np.sin(np.radians(-25)) * 0.5])

# Draw a smooth elliptic arc connecting ray2 to ray1
theta_angles = np.linspace(np.radians(-25), np.radians(20), 40)
arc_pts_x = orig[0] + r_len * np.cos(theta_angles)
arc_pts_y = orig[1] + r_len * np.sin(theta_angles) * 0.5

# Fill the sector face with subtle transparent shade
sector_poly_x = [orig[0]] + list(arc_pts_x) + [orig[0]]
sector_poly_y = [orig[1]] + list(arc_pts_y) + [orig[1]]
ax.fill(sector_poly_x, sector_poly_y, color='#E8EEF5', alpha=0.75, zorder=4)
ax.plot(sector_poly_x, sector_poly_y, color='#4A6572', linewidth=1.2, zorder=5)

# Radial ray 1 with arrow (+r)
ax.annotate('', xy=ray1, xytext=orig,
            arrowprops=dict(arrowstyle='->', color='#000000', lw=2.0, mutation_scale=16),
            zorder=6)
ax.text(ray1[0] + 18, ray1[1] + 8, r'$+r$', fontsize=18, fontweight='bold', color='#000000', ha='left', va='center')

# Subtle azimuthal arc arrow (+theta)
mid_arc_idx = len(arc_pts_x) // 2
ax.annotate('', xy=(arc_pts_x[-1], arc_pts_y[-1]), xytext=(arc_pts_x[0], arc_pts_y[0]),
            arrowprops=dict(arrowstyle='->', color='#4A6572', lw=1.2, connectionstyle='arc3,rad=-0.35'),
            zorder=6)
ax.text(arc_pts_x[mid_arc_idx] + 16, arc_pts_y[mid_arc_idx] - 12, r'$+\theta$', fontsize=14, color='#4A6572', ha='left', va='bottom')

# Axis of symmetry centerline on the left
ax.plot([120, 120], [220, 1660], color='#666666', linestyle='-.', linewidth=1.5, zorder=2)
ax.text(130, 240, r'$r = 0$' + '\n(中心对称轴 / Axis of Symmetry)', fontsize=13, color='#444444', ha='left', va='top')

out_png = os.path.join(SCRATCH, "fvm_flux_v2_updated.png")
fig.savefig(out_png, dpi=300, bbox_inches='tight', pad_inches=0.02)
plt.close(fig)

# Sync to EDA figures and artifacts
shutil_path_eda = os.path.join(EDA_DIR, "fvm_flux_v2_updated.png")
shutil_path_art = r"C:\Users\kqdx\.gemini\antigravity\brain\984f8f9b-1caf-4e5e-a827-7c48f241b73b\fvm_flux_v2_updated.png"

import shutil
shutil.copy(out_png, shutil_path_eda)
shutil.copy(out_png, shutil_path_art)

print("Rendered and synced fvm_flux_v2_updated.png successfully!")
