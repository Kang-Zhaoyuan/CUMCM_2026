import os
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image

SCRATCH = r"C:\Users\kqdx\.gemini\antigravity\brain\984f8f9b-1caf-4e5e-a827-7c48f241b73b\scratch"
EDA_DIR = r"D:\HIT\数模2026\eda_figures"
src_img_path = os.path.join(EDA_DIR, "fvm_flux_flared_c2_refined.png")

img = Image.open(src_img_path)
W, H = img.size

fig, ax = plt.subplots(figsize=(10, 10), dpi=300)
ax.imshow(img)
ax.set_xlim(0, W)
ax.set_ylim(H, 0) # Invert Y to match image coords
ax.axis('off')

# Mathtext font styling
plt.rcParams['mathtext.fontset'] = 'cm' # Computer Modern
plt.rcParams['font.family'] = 'serif'

# 1. Five Node Stencil Centroids (Calculated from 3D projection)
# P: (764.7, 984.8), W: (426.0, 912.1), E: (1168.6, 1071.5), N: (765.4, 528.9), S: (764.0, 1417.6)
pts = {
    'P': (765, 985),
    'W': (426, 912),
    'E': (1169, 1072),
    'N': (765, 529),
    'S': (764, 1418),
}

# Draw subtle dashed grid lines between nodes
ax.plot([pts['W'][0], pts['P'][0], pts['E'][0]], [pts['W'][1], pts['P'][1], pts['E'][1]], 
        color='#777777', linestyle='--', linewidth=1.2, alpha=0.6, zorder=3)
ax.plot([pts['N'][0], pts['P'][0], pts['S'][0]], [pts['N'][1], pts['P'][1], pts['S'][1]], 
        color='#777777', linestyle='--', linewidth=1.2, alpha=0.6, zorder=3)

# Draw Node points and labels
for k, (x, y) in pts.items():
    # Node dot
    if k == 'P':
        # Central node P
        ax.scatter(x, y, s=60, color='#000000', edgecolors='none', zorder=5)
        ax.text(x + 24, y - 24, r'$\mathbf{P}\ (i, j)$', fontsize=15, fontweight='bold', 
                color='#000000', ha='left', va='bottom', zorder=6)
    else:
        ax.scatter(x, y, s=45, color='#444444', edgecolors='none', zorder=5)
        
    if k == 'W':
        ax.text(x - 18, y - 18, r'$\mathbf{W}\ (i-1, j)$', fontsize=13, color='#222222', ha='right', va='bottom', zorder=6)
    elif k == 'E':
        ax.text(x + 18, y - 18, r'$\mathbf{E}\ (i+1, j)$', fontsize=13, color='#222222', ha='left', va='bottom', zorder=6)
    elif k == 'N':
        ax.text(x + 18, y - 18, r'$\mathbf{N}\ (i, j+1)$', fontsize=13, color='#222222', ha='left', va='bottom', zorder=6)
    elif k == 'S':
        ax.text(x + 18, y + 18, r'$\mathbf{S}\ (i, j-1)$', fontsize=13, color='#222222', ha='left', va='top', zorder=6)

# 2. Heat Flux Labels near the 4 red arrows
# Right arrow: Inflow from E to P
ax.text(1020, 960, r'$Q_{i+\frac{1}{2}, j}$', fontsize=15, color='#D31010', fontweight='bold', ha='center', va='bottom', zorder=6)
# Left arrow: Outflow from P to W
ax.text(530, 910, r'$Q_{i-\frac{1}{2}, j}$', fontsize=14, color='#D31010', fontweight='bold', ha='center', va='bottom', zorder=6)
# Top arrow: Inflow from N to P
ax.text(820, 680, r'$Q_{i, j+\frac{1}{2}}$', fontsize=15, color='#D31010', fontweight='bold', ha='left', va='center', zorder=6)
# Bottom arrow: Outflow from P to S
ax.text(810, 1260, r'$Q_{i, j-\frac{1}{2}}$', fontsize=14, color='#D31010', fontweight='bold', ha='left', va='center', zorder=6)

# 3. Discretization Dimensions: Delta r and Delta z
# Dimension for Delta z along the left edge of Mother Ring
# Mother ring left edge in screen coords is around x ~ 620, y from 760 to 1210
# Let's put a clean dimension bracket
ax.annotate('', xy=(590, 760), xytext=(590, 1210),
            arrowprops=dict(arrowstyle='<->', color='#333333', lw=1.2))
ax.text(575, (760 + 1210) / 2, r'$\Delta z$', fontsize=14, color='#333333', ha='right', va='center', rotation=90)

# Dimension for Delta r on top of Mother Ring
ax.annotate('', xy=(625, 740), xytext=(925, 795),
            arrowprops=dict(arrowstyle='<->', color='#333333', lw=1.2))
ax.text((625 + 925) / 2 - 10, (740 + 795) / 2 - 25, r'$\Delta r$', fontsize=14, color='#333333', ha='center', va='bottom')

# 4. Axis of Symmetry (Centerline) on the left
ax.plot([140, 140], [250, 1550], color='#555555', linestyle='-.', linewidth=1.5, zorder=2)
ax.text(155, 300, r'$\mathbf{r = 0}$' + '\n(中心对称轴)', fontsize=12, color='#555555', ha='left', va='top')

# 5. Cylindrical Coordinate Frame (in bottom-left)
ax.annotate('', xy=(280, 1620), xytext=(180, 1620),
            arrowprops=dict(arrowstyle='->', color='#000000', lw=1.5))
ax.text(295, 1620, r'$+r$', fontsize=13, ha='left', va='center')

ax.annotate('', xy=(180, 1520), xytext=(180, 1620),
            arrowprops=dict(arrowstyle='->', color='#000000', lw=1.5))
ax.text(180, 1505, r'$+z$', fontsize=13, ha='center', va='bottom')

plt.tight_layout()
out_path = os.path.join(SCRATCH, "test_annotated_rich.png")
fig.savefig(out_path, dpi=300, bbox_inches='tight', pad_inches=0.02)
plt.close(fig)

print("Saved test_annotated_rich.png")
