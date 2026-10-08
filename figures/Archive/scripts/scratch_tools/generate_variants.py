import os, shutil
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PIL import Image

plt.rcParams['mathtext.fontset'] = 'cm'
plt.rcParams['font.serif'] = ['Times New Roman', 'DejaVu Serif']
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'DejaVu Sans']

base_path = r'd:\HIT\数模2026\eda_figures\fvm_flux_flared_c2_refined.png'
base_img = Image.open(base_path)
W, H = base_img.size
C = np.array([W / 2.0, H / 2.0])

# Key points in base_img (2114 x 2114):
p_bi = np.array([790.0, 1694.0])
p_bo = np.array([1068.0, 1790.0])

p_tr = np.array([1515.0, 1068.0])
p_br = np.array([1514.0, 1464.0])
p_tl = np.array([1160.0, 958.0])
p_bl = np.array([1157.0, 1412.0])

# Q positions in base_img:
# 1. N: shifted slightly down by 35px
p_q_N = np.array([925.0, 710.0])
# 2. S: shifted up by 1.5 * 35 = 52.5px
p_q_S = np.array([924.5, 1552.5])
# 3. W: unchanged as requested
p_q_W = np.array([605.0, 1076.2])
# 4. E: shifted left by 35px, up by 25px
p_q_E = np.array([1330.0, 1214.3])

variants = [
    ('variant_1_shift_moderate', 1.00, np.array([-70.0, -110.0]), '方案1：适度向左上平移（1.0倍原比例）'),
    ('variant_2_shift_strong',   1.00, np.array([-110.0, -165.0]), '方案2：较大幅度向左上平移（1.0倍原比例）'),
    ('variant_3_scale_110',      1.10, np.array([-85.0, -135.0]), '方案3：等比例放大10% + 居中平衡（1.10倍）'),
    ('variant_4_scale_118',      1.18, np.array([-95.0, -155.0]), '方案4：等比例放大18% + 饱满版面（1.18倍）')
]

SCRATCH = r'C:\Users\kqdx\.gemini\antigravity\brain\984f8f9b-1caf-4e5e-a827-7c48f241b73b\scratch'
EDA_DIR = r'd:\HIT\数模2026\eda_figures'
ART_DIR = r'C:\Users\kqdx\.gemini\antigravity\brain\984f8f9b-1caf-4e5e-a827-7c48f241b73b'

for name, S, shift, desc in variants:
    def tf(p):
        return C + (p - C) * S + shift

    fig, ax = plt.subplots(figsize=(10, 10), dpi=300)
    
    # Base image extent
    tl_corner = tf(np.array([0.0, 0.0]))
    br_corner = tf(np.array([float(W), float(H)]))
    extent = [tl_corner[0], br_corner[0], br_corner[1], tl_corner[1]]
    
    ax.imshow(base_img, extent=extent, interpolation='bilinear')
    ax.set_xlim(0, W)
    ax.set_ylim(H, 0)
    ax.axis('off')
    
    # -------------------------------------------------------------------------
    # 1. Delta r on Near ring
    # -------------------------------------------------------------------------
    bi = tf(p_bi)
    bo = tf(p_bo)
    ext_len_r = 70 * S
    d_off_r = 52 * S
    
    ax.plot([bi[0], bi[0]], [bi[1], bi[1] + ext_len_r], color='#333333', linestyle='--', linewidth=1.3, zorder=5)
    ax.plot([bo[0], bo[0]], [bo[1], bo[1] + ext_len_r], color='#333333', linestyle='--', linewidth=1.3, zorder=5)
    
    dim_r1 = bi + np.array([0, d_off_r])
    dim_r2 = bo + np.array([0, d_off_r])
    ax.annotate('', xy=dim_r1, xytext=dim_r2,
                arrowprops=dict(arrowstyle='<->', color='#000000', lw=1.6, shrinkA=0, shrinkB=0), zorder=6)
    dim_mid_r = (dim_r1 + dim_r2) / 2
    ax.text(dim_mid_r[0], max(bi[1], bo[1]) + ext_len_r + 28, r'$\Delta r$',
            fontsize=18 * S, fontweight='bold', color='#000000', ha='center', va='top', zorder=7)
            
    # -------------------------------------------------------------------------
    # 2. Delta z on Outer ring diamond
    # -------------------------------------------------------------------------
    tr = tf(p_tr)
    br = tf(p_br)
    tl = tf(p_tl)
    bl = tf(p_bl)
    
    dir_top = (tr - tl) / np.linalg.norm(tr - tl)
    dir_bot = (br - bl) / np.linalg.norm(br - bl)
    
    L_ext_z = 80 * S
    d_off_z = 52 * S
    
    ax.plot([tr[0], tr[0] + L_ext_z * dir_top[0]], [tr[1], tr[1] + L_ext_z * dir_top[1]],
            color='#333333', linestyle='--', linewidth=1.3, zorder=5)
    ax.plot([br[0], br[0] + L_ext_z * dir_bot[0]], [br[1], br[1] + L_ext_z * dir_bot[1]],
            color='#333333', linestyle='--', linewidth=1.3, zorder=5)
            
    dim_z1 = tr + d_off_z * dir_top
    dim_z2 = br + d_off_z * dir_bot
    ax.annotate('', xy=dim_z1, xytext=dim_z2,
                arrowprops=dict(arrowstyle='<->', color='#000000', lw=1.6, shrinkA=0, shrinkB=0), zorder=6)
    dim_mid_z = (dim_z1 + dim_z2) / 2
    ax.text(dim_mid_z[0] + 16, dim_mid_z[1], r'$\Delta z$',
            fontsize=18 * S, fontweight='bold', color='#000000', ha='left', va='center', zorder=7)
            
    # -------------------------------------------------------------------------
    # 3. Four Q labels
    # -------------------------------------------------------------------------
    c_red = '#E01010'
    fsize = 16.5 * S
    
    q_N = tf(p_q_N)
    q_S = tf(p_q_S)
    q_W = tf(p_q_W)
    q_E = tf(p_q_E)
    
    ax.text(q_N[0], q_N[1], r'$Q_{i,\, j+1/2}$', fontsize=fsize, color=c_red, fontweight='bold', ha='center', va='center', zorder=8)
    ax.text(q_S[0], q_S[1], r'$Q_{i,\, j-1/2}$', fontsize=fsize, color=c_red, fontweight='bold', ha='center', va='center', zorder=8)
    ax.text(q_W[0], q_W[1], r'$Q_{i-1/2,\, j}$', fontsize=fsize, color=c_red, fontweight='bold', ha='center', va='center', zorder=8)
    ax.text(q_E[0], q_E[1], r'$Q_{i+1/2,\, j}$', fontsize=fsize, color=c_red, fontweight='bold', ha='center', va='center', zorder=8)
    
    # -------------------------------------------------------------------------
    # 4. Bottom-Left coordinate system (FIXED at canvas corner, invariant)
    # -------------------------------------------------------------------------
    orig = np.array([160.0, H - 160.0])
    z_top = orig + np.array([0, -180.0])
    ax.annotate('', xy=z_top, xytext=orig,
                arrowprops=dict(arrowstyle='->', color='#000000', lw=2.2, mutation_scale=18), zorder=6)
    ax.text(z_top[0], z_top[1] - 15, r'$+z$', fontsize=20, fontweight='bold', color='#000000', ha='center', va='bottom')
    
    r_len = 155.0
    ray1 = orig + np.array([r_len * np.cos(np.radians(20)), r_len * np.sin(np.radians(20)) * 0.48])
    theta_angles = np.linspace(np.radians(-28), np.radians(20), 50)
    arc_pts_x = orig[0] + r_len * np.cos(theta_angles)
    arc_pts_y = orig[1] + r_len * np.sin(theta_angles) * 0.48
    sector_poly_x = [orig[0]] + list(arc_pts_x) + [orig[0]]
    sector_poly_y = [orig[1]] + list(arc_pts_y) + [orig[1]]
    ax.fill(sector_poly_x, sector_poly_y, color='#EBF3FB', alpha=0.85, zorder=4)
    ax.plot(sector_poly_x, sector_poly_y, color='#3B6077', linewidth=1.4, zorder=5)
    
    ax.annotate('', xy=ray1, xytext=orig,
                arrowprops=dict(arrowstyle='->', color='#000000', lw=2.0, mutation_scale=16), zorder=6)
    ax.text(ray1[0] + 16, ray1[1] + 6, r'$+r$', fontsize=20, fontweight='bold', color='#000000', ha='left', va='center')
    
    out_file = os.path.join(SCRATCH, f'{name}.png')
    fig.savefig(out_file, dpi=300, bbox_inches='tight', pad_inches=0.04)
    plt.close(fig)
    print(f'Rendered {out_file}')
    
    shutil.copy(out_file, os.path.join(EDA_DIR, f'{name}.png'))
    shutil.copy(out_file, os.path.join(ART_DIR, f'{name}.png'))

print('All 4 variants rendered and synced successfully!')
