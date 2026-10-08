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

# Scheme 4 parameters
S = 1.18
shift = np.array([-95.0, -155.0])

def tf(p):
    return C + (p - C) * S + shift

# -------------------------------------------------------------------------
# Exact Base Coordinates
# -------------------------------------------------------------------------
# Near ring bottom corners
bi_base = np.array([787.0, 1694.0])
bo_base = np.array([1068.0, 1790.0])
v_left_base = np.array([0.00493, 1.0]) / np.sqrt(1.0 + 0.00493**2)
v_right_base = np.array([0.00307, 1.0]) / np.sqrt(1.0 + 0.00307**2)

# Outer ring diamond right corners and edge directions
TR_base = np.array([1514.0, 1070.0])
BR_base = np.array([1514.0, 1460.0])

u_top_base = np.array([1.0, 0.17115]) / np.sqrt(1.0 + 0.17115**2)
u_bot_base = np.array([1.0, 0.16417]) / np.sqrt(1.0 + 0.16417**2)
u_avg_base = (u_top_base + u_bot_base) / 2.0
u_avg_base /= np.linalg.norm(u_avg_base)

# Perpendicular unit vector (slanted downwards by ~9.5 deg)
v_perp_base = np.array([-u_avg_base[1], u_avg_base[0]])

# Q positions in base_img
p_q_N = np.array([925.0, 710.0])
p_q_S = np.array([924.5, 1552.5])
p_q_W = np.array([605.0, 1076.2])
p_q_E = np.array([1330.0, 1214.3])

SCRATCH = r'C:\Users\kqdx\.gemini\antigravity\brain\984f8f9b-1caf-4e5e-a827-7c48f241b73b\scratch'
EDA_DIR = r'd:\HIT\数模2026\eda_figures'
ART_DIR = r'C:\Users\kqdx\.gemini\antigravity\brain\984f8f9b-1caf-4e5e-a827-7c48f241b73b'

def render_figure(show_grid=False, filename='fvm_flux_step2_review.png'):
    fig, ax = plt.subplots(figsize=(10, 10), dpi=300)
    
    # Base image extent
    tl_corner = tf(np.array([0.0, 0.0]))
    br_corner = tf(np.array([float(W), float(H)]))
    extent = [tl_corner[0], br_corner[0], br_corner[1], tl_corner[1]]
    
    ax.imshow(base_img, extent=extent, interpolation='bilinear')
    ax.set_xlim(0, W)
    ax.set_ylim(H, 0)
    
    # -------------------------------------------------------------------------
    # 1. Delta r on Near Ring (Exact collinear extension + parallel double arrow)
    # -------------------------------------------------------------------------
    bi = tf(bi_base)
    bo = tf(bo_base)
    v_l = v_left_base # direction remains unchanged under isotropic scaling S
    v_r = v_right_base
    
    d_off_r = 52.0 * S
    L_ext_r = d_off_r + 26.0 * S
    
    # Collinear extension lines:
    ax.plot([bi[0], bi[0] + L_ext_r * v_l[0]], [bi[1], bi[1] + L_ext_r * v_l[1]],
            color='#333333', linestyle='--', linewidth=1.3, zorder=5)
    ax.plot([bo[0], bo[0] + L_ext_r * v_r[0]], [bo[1], bo[1] + L_ext_r * v_r[1]],
            color='#333333', linestyle='--', linewidth=1.3, zorder=5)
            
    p_dim_r1 = bi + d_off_r * v_l
    p_dim_r2 = bo + d_off_r * v_r
    
    ax.annotate('', xy=p_dim_r1, xytext=p_dim_r2,
                arrowprops=dict(arrowstyle='<->', color='#000000', lw=1.6, shrinkA=0, shrinkB=0), zorder=6)
    
    dim_mid_r = (p_dim_r1 + p_dim_r2) / 2.0
    ax.text(dim_mid_r[0], max(bi[1], bo[1]) + L_ext_r + 28, r'$\Delta r$',
            fontsize=18 * S, fontweight='bold', color='#000000', ha='center', va='top', zorder=7)

    # -------------------------------------------------------------------------
    # 2. Delta z on Outer Ring (Exact collinear extension + perpendicular slanted arrow)
    # -------------------------------------------------------------------------
    TR = tf(TR_base)
    BR = tf(BR_base)
    u_t = u_top_base
    u_b = u_bot_base
    u_avg = u_avg_base
    v_p = v_perp_base
    
    mid_edge_z = (TR + BR) / 2.0
    d_off_z = 62.0 * S
    mid_dim_z = mid_edge_z + d_off_z * u_avg
    
    # Solve exact perpendicular intersection with top and bottom lines:
    A_top = np.column_stack([u_t, -v_p])
    s_top, _ = np.linalg.solve(A_top, mid_dim_z - TR)
    p_top_dim = TR + s_top * u_t
    
    A_bot = np.column_stack([u_b, -v_p])
    t_bot, _ = np.linalg.solve(A_bot, mid_dim_z - BR)
    p_bot_dim = BR + t_bot * u_b
    
    L_ext_top = s_top + 26.0 * S
    L_ext_bot = t_bot + 26.0 * S
    
    # Perfectly collinear extension lines:
    ax.plot([TR[0], TR[0] + L_ext_top * u_t[0]], [TR[1], TR[1] + L_ext_top * u_t[1]],
            color='#333333', linestyle='--', linewidth=1.3, zorder=5)
    ax.plot([BR[0], BR[0] + L_ext_bot * u_b[0]], [BR[1], BR[1] + L_ext_bot * u_b[1]],
            color='#333333', linestyle='--', linewidth=1.3, zorder=5)
            
    # Slanted double-headed arrow perpendicular to the extension lines:
    ax.annotate('', xy=p_top_dim, xytext=p_bot_dim,
                arrowprops=dict(arrowstyle='<->', color='#000000', lw=1.6, shrinkA=0, shrinkB=0), zorder=6)
                
    p_mid_z = (p_top_dim + p_bot_dim) / 2.0
    ax.text(p_mid_z[0] + 16, p_mid_z[1], r'$\Delta z$',
            fontsize=18 * S, fontweight='bold', color='#000000', ha='left', va='center', zorder=7)

    # -------------------------------------------------------------------------
    # 3. Four Q Labels
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
    # 4. Bottom-Left Coordinate System (FIXED at canvas corner)
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

    # Optional Grid Overlay for Step 3 tuning
    if show_grid:
        ax.axis('on')
        # Major ticks every 100 px, minor ticks every 50 px
        ax.set_xticks(np.arange(0, W + 1, 100))
        ax.set_yticks(np.arange(0, H + 1, 100))
        ax.set_xticks(np.arange(0, W + 1, 50), minor=True)
        ax.set_yticks(np.arange(0, H + 1, 50), minor=True)
        ax.grid(which='major', color='#3498DB', linestyle='-', linewidth=0.75, alpha=0.45)
        ax.grid(which='minor', color='#85C1E9', linestyle=':', linewidth=0.5, alpha=0.35)
        ax.tick_params(axis='both', which='major', labelsize=8, colors='#2C3E50')
    else:
        ax.axis('off')

    out_file = os.path.join(SCRATCH, filename)
    fig.savefig(out_file, dpi=300, bbox_inches='tight', pad_inches=0.04)
    plt.close(fig)
    print(f'Rendered {out_file}')
    
    shutil.copy(out_file, os.path.join(EDA_DIR, filename))
    shutil.copy(out_file, os.path.join(ART_DIR, filename))

# Render clean review version
render_figure(show_grid=False, filename='fvm_flux_step2_review.png')
# Render grid version for Step 3 coordinate reference
render_figure(show_grid=True, filename='fvm_flux_step2_grid.png')

print('Step 2 and Grid figures generated successfully!')
