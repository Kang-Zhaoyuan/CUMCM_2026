import os
import numpy as np
import matplotlib.pyplot as plt
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

# Coordinates of the 5 centroids
pts = {
    'P': (765, 985),
    'W': (426, 912),
    'E': (1169, 1072),
    'N': (765, 529),
    'S': (764, 1418),
}

# 1. Subtle dashed topology grid lines (broken around center so as not to clutter the arrows)
# Horizontal: W to P (stop before arrow), and E to P (stop before arrow)
ax.plot([pts['W'][0], 550], [pts['W'][1], 938], color='#888888', linestyle='--', linewidth=1.4, alpha=0.7, zorder=3)
ax.plot([970, pts['E'][0]], [1028, pts['E'][1]], color='#888888', linestyle='--', linewidth=1.4, alpha=0.7, zorder=3)

# Vertical: N to P (stop before arrow), and S to P (stop before arrow)
ax.plot([pts['N'][0], pts['P'][0]], [pts['N'][1], 700], color='#888888', linestyle='--', linewidth=1.4, alpha=0.7, zorder=3)
ax.plot([pts['S'][0], pts['P'][0]], [pts['S'][1], 1260], color='#888888', linestyle='--', linewidth=1.4, alpha=0.7, zorder=3)

# 2. Centroid dots & Stencil Labels
for k, (x, y) in pts.items():
    if k == 'P':
        ax.scatter(x, y, s=80, color='#000000', edgecolors='none', zorder=7)
        # Position label in lower-left of mother square where it is clean
        ax.text(x - 50, y + 60, r'$\mathbf{P}\ (i, j)$', fontsize=18, fontweight='bold',
                color='#000000', ha='right', va='top', zorder=8)
    else:
        ax.scatter(x, y, s=55, color='#333333', edgecolors='none', zorder=7)
        
    if k == 'W':
        ax.text(x - 25, y - 25, r'$\mathbf{W}\ (i-1, j)$', fontsize=16, color='#222222', ha='right', va='bottom', zorder=8)
    elif k == 'E':
        ax.text(x + 25, y - 25, r'$\mathbf{E}\ (i+1, j)$', fontsize=16, color='#222222', ha='left', va='bottom', zorder=8)
    elif k == 'N':
        ax.text(x + 25, y - 20, r'$\mathbf{N}\ (i, j+1)$', fontsize=16, color='#222222', ha='left', va='bottom', zorder=8)
    elif k == 'S':
        ax.text(x + 25, y + 25, r'$\mathbf{S}\ (i, j-1)$', fontsize=16, color='#222222', ha='left', va='top', zorder=8)

# 3. Heat Flux LaTeX Annotations
# E -> P (Right Inflow)
ax.text(1030, 960, r'$Q_{i+\frac{1}{2},\, j}$', fontsize=17, color='#D31010', fontweight='bold', ha='center', va='bottom', zorder=8)
# P -> W (Left Outflow)
ax.text(520, 890, r'$Q_{i-\frac{1}{2},\, j}$', fontsize=16, color='#D31010', fontweight='bold', ha='center', va='bottom', zorder=8)
# N -> P (Top Inflow)
ax.text(830, 680, r'$Q_{i,\, j+\frac{1}{2}}$', fontsize=17, color='#D31010', fontweight='bold', ha='left', va='center', zorder=8)
# P -> S (Bottom Outflow)
ax.text(820, 1270, r'$Q_{i,\, j-\frac{1}{2}}$', fontsize=16, color='#D31010', fontweight='bold', ha='left', va='center', zorder=8)

# 4. Dimension Lines: Delta r and Delta z
# Delta z on Left Edge of Mother Ring (between y=760 and y=1210, offset to x=560)
ax.annotate('', xy=(560, 770), xytext=(560, 1200),
            arrowprops=dict(arrowstyle='<->', color='#222222', lw=1.5, shrinkA=0, shrinkB=0))
ax.text(540, (770 + 1200) / 2, r'$\Delta z$', fontsize=16, color='#222222', ha='right', va='center')

# Delta r on Top of Small Ring (x from 300 to 570, clean space!)
# Small ring top boundary in screen coords: around y ~ 720
ax.annotate('', xy=(305, 715), xytext=(570, 755),
            arrowprops=dict(arrowstyle='<->', color='#222222', lw=1.5, shrinkA=0, shrinkB=0))
ax.text((305 + 570) / 2, (715 + 755) / 2 - 25, r'$\Delta r$', fontsize=16, color='#222222', ha='center', va='bottom')

# 5. Axis of Symmetry (Centerline) on Far Left
ax.plot([130, 130], [250, 1550], color='#555555', linestyle='-.', linewidth=1.8, zorder=2)
ax.text(145, 270, r'$\mathbf{r = 0}$' + '\n(中心对称轴 / Axis of Symmetry)', fontsize=13, color='#444444', ha='left', va='top')

# 6. Global Coordinate Frame (in bottom-left corner)
ax.annotate('', xy=(280, 1640), xytext=(170, 1640),
            arrowprops=dict(arrowstyle='->', color='#000000', lw=2.0))
ax.text(295, 1640, r'$+r$', fontsize=16, fontweight='bold', ha='left', va='center')

ax.annotate('', xy=(170, 1530), xytext=(170, 1640),
            arrowprops=dict(arrowstyle='->', color='#000000', lw=2.0))
ax.text(170, 1515, r'$+z$', fontsize=16, fontweight='bold', ha='center', va='bottom')

# 7. Ambient Environment / Heat Source Context (Top Right corner)
ax.text(1650, 350, r'$\mathbf{T_\infty, C_\infty}$' + '\n(外部干燥/烘房环境)', fontsize=14, color='#666666', ha='right', va='top',
        bbox=dict(boxstyle='round,pad=0.5', facecolor='#F9F9F9', edgecolor='#CCCCCC', lw=1.0))
# Subtle arrow pointing from environment towards Large ring
ax.annotate('', xy=(1450, 520), xytext=(1550, 420),
            arrowprops=dict(arrowstyle='->', color='#888888', lw=1.2, linestyle=':'))

plt.tight_layout()
out_png = os.path.join(SCRATCH, "fvm_flux_enriched_preview.png")
fig.savefig(out_png, dpi=300, bbox_inches='tight', pad_inches=0.02)
plt.close(fig)

# Sync to artifacts & EDA
import shutil
shutil.copy(out_png, os.path.join(EDA_DIR, "fvm_flux_enriched_preview.png"))
shutil.copy(out_png, r"C:\Users\kqdx\.gemini\antigravity\brain\984f8f9b-1caf-4e5e-a827-7c48f241b73b\fvm_flux_enriched_preview.png")

print("Saved fvm_flux_enriched_preview.png successfully!")
