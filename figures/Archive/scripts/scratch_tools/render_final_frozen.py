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

# Scheme 4 parameters (18% enlargement, shifted to top-left)
S = 1.18
shift = np.array([-95.0, -155.0])

def tf(p):
    return C + (p - C) * S + shift

# -------------------------------------------------------------------------
# Exact Base Coordinates for Geometry
# -------------------------------------------------------------------------
# Near ring bottom corners and edge directions
bi_base = np.array([787.0, 1694.0])
bo_base = np.array([1068.0, 1790.0])
v_left_base = np.array([0.00493, 1.0]) / np.sqrt(1.0 + 0.00493**2)
v_right_base = np.array([0.00307, 1.0]) / np.sqrt(1.0 + 0.00307**2)

# Outer ring diamond right corners and exact edge slopes
TR_base = np.array([1516.93, 1070.43])
BR_base = np.array([1504.89, 1463.82])

u_top_base = np.array([1.0, 0.17293]) / np.sqrt(1.0 + 0.17293**2)
u_bot_base = np.array([1.0, 0.22093]) / np.sqrt(1.0 + 0.22093**2)

# Vector along outermost vertical edge (from TR to BR)
v_edge_base = (BR_base - TR_base) / np.linalg.norm(BR_base - TR_base)

# -------------------------------------------------------------------------
# Q Positions (Calculated from Scheme 4 Canvas Coords + User's Exact Offsets)
# -------------------------------------------------------------------------
# Previous canvas coords:
# q_N: [806.24, 492.54]  -> User: down by 50 px  -> Y = 542.54
# q_S: [805.65, 1486.69] -> User: up by 45 px    -> Y = 1441.69
# q_W: [428.64, 924.66]  -> User: left by 19 px  -> X = 409.64
# q_E: [1284.14, 1087.61]-> User: right by 20 px -> X = 1304.14
q_N = np.array([806.24, 542.54])
q_S = np.array([805.65, 1441.69])
q_W = np.array([409.64, 924.66])
q_E = np.array([1304.14, 1087.61])

SCRATCH = r'C:\Users\kqdx\.gemini\antigravity\brain\984f8f9b-1caf-4e5e-a827-7c48f241b73b\scratch'
EDA_DIR = r'd:\HIT\数模2026\eda_figures'
ART_DIR = r'C:\Users\kqdx\.gemini\antigravity\brain\984f8f9b-1caf-4e5e-a827-7c48f241b73b'

def render_figure(show_grid=False, filename='fvm_flux_annotated_v2.png'):
    fig, ax = plt.subplots(figsize=(10, 10), dpi=300)
    
    # Base image extent under tf
    tl_corner = tf(np.array([0.0, 0.0]))
    br_corner = tf(np.array([float(W), float(H)]))
    extent = [tl_corner[0], br_corner[0], br_corner[1], tl_corner[1]]
    
    ax.imshow(base_img, extent=extent, interpolation='bilinear')
    ax.set_xlim(0, W)
    ax.set_ylim(H, 0)
    
    # -------------------------------------------------------------------------
    # 1. Delta r on Near Ring
    # -------------------------------------------------------------------------
    bi = tf(bi_base)
    bo = tf(bo_base)
    v_l = v_left_base
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
    # 2. Delta z on Outer Ring
    # -------------------------------------------------------------------------
    TR = tf(TR_base)
    BR = tf(BR_base)
    u_t = u_top_base
    u_b = u_bot_base
    v_edge = (BR - TR) / np.linalg.norm(BR - TR) # Exact direction of the outermost edge
    
    # Place top dimension point at d_off_z along top extension line:
    d_off_z = 56.0 * S
    p_top_dim = TR + d_off_z * u_t
    
    # Solve bottom dimension point p_bot_dim on bottom extension line so that
    # (p_bot_dim - p_top_dim) is STRICTLY PARALLEL to v_edge:
    # p_top_dim + lam * v_edge = BR + t * u_b
    # [u_b, -v_edge] * [t, lam]^T = p_top_dim - BR
    A_mat = np.column_stack([u_b, -v_edge])
    t_val, _ = np.linalg.solve(A_mat, p_top_dim - BR)
    p_bot_dim = BR + t_val * u_b
    
    # Extension lines continue slightly past the dimension arrow:
    L_ext_top = d_off_z + 24.0 * S
    L_ext_bot = t_val + 24.0 * S
    
    # Strictly collinear extension lines with the solid edges:
    ax.plot([TR[0], TR[0] + L_ext_top * u_t[0]], [TR[1], TR[1] + L_ext_top * u_t[1]],
            color='#333333', linestyle='--', linewidth=1.3, zorder=5)
    ax.plot([BR[0], BR[0] + L_ext_bot * u_b[0]], [BR[1], BR[1] + L_ext_bot * u_b[1]],
            color='#333333', linestyle='--', linewidth=1.3, zorder=5)
            
    # Double-headed arrow strictly parallel to the outermost edge:
    ax.annotate('', xy=p_top_dim, xytext=p_bot_dim,
                arrowprops=dict(arrowstyle='<->', color='#000000', lw=1.6, shrinkA=0, shrinkB=0), zorder=6)
                
    p_mid_z = (p_top_dim + p_bot_dim) / 2.0
    ax.text(p_mid_z[0] + 16, p_mid_z[1], r'$\Delta z$',
            fontsize=18 * S, fontweight='bold', color='#000000', ha='left', va='center', zorder=7)

    # -------------------------------------------------------------------------
    # 3. Four Q Labels (Precisely Shifted)
    # -------------------------------------------------------------------------
    c_red = '#E01010'
    fsize = 16.5 * S
    
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

    if show_grid:
        ax.axis('on')
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

# Render clean final version
render_figure(show_grid=False, filename='fvm_flux_annotated_v2.png')
# Also render grid version for reference
render_figure(show_grid=True, filename='fvm_flux_final_grid.png')

print('Final figures rendered and synced successfully!')
