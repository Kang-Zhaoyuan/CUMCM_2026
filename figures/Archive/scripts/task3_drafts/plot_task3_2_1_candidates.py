import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, PathPatch, Rectangle, FancyArrowPatch
from matplotlib.path import Path

# 字体设置：支持中文标题与 LaTeX Computer Modern 数学符号
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'DejaVu Sans']
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['mathtext.fontset'] = 'cm'
plt.rcParams['axes.unicode_minus'] = False

def draw_beveled_3d_arrow(ax, start, end, head_len=0.68, head_w=0.19,
                          notch=0.12, c_light='#64748b', c_dark='#1e293b',
                          c_line='#0f172a', lw=2.0, zorder=20):
    start = np.array(start, dtype=float)
    end = np.array(end, dtype=float)
    d = end - start
    L = np.linalg.norm(d)
    if L < 1e-6:
        return
    u = d / L
    v = np.array([-u[1], u[0]])
    
    base_center = end - head_len * u
    notch_pt = base_center + notch * u
    
    ax.plot([start[0], notch_pt[0]], [start[1], notch_pt[1]],
            color=c_line, lw=lw, solid_capstyle='butt', zorder=zorder)
    
    p_tip = end
    p_left = base_center + head_w * v
    p_right = base_center - head_w * v
    
    poly_light = np.array([p_tip, p_left, notch_pt])
    ax.add_patch(Polygon(poly_light, closed=True, facecolor=c_light, edgecolor=c_line, lw=0.7, zorder=zorder+1))
    
    poly_dark = np.array([p_tip, notch_pt, p_right])
    ax.add_patch(Polygon(poly_dark, closed=True, facecolor=c_dark, edgecolor=c_line, lw=0.7, zorder=zorder+1))
    
    ax.plot([p_tip[0], notch_pt[0]], [p_tip[1], notch_pt[1]], color='#cbd5e1', lw=0.85, zorder=zorder+2)

def draw_ring_3d(ax, r_center, dr, z_center, dz, eps=0.20,
                 c_line='#d63031', c_fill='#ff7675', alpha_fill=0.5,
                 is_dashed=False, zorder_base=10):
    theta_full = np.linspace(0, 2 * np.pi, 300)
    theta_front = np.linspace(np.pi, 2 * np.pi, 150)
    theta_back = np.linspace(0, np.pi, 150)

    r_in = r_center - dr / 2.0
    r_out = r_center + dr / 2.0
    z_bot = z_center - dz / 2.0
    z_top = z_center + dz / 2.0

    ls_line = (0, (3.5, 2.5)) if is_dashed else '-'

    ax.plot(r_out * np.cos(theta_back), z_bot + r_out * np.sin(theta_back) * eps,
            color=c_line, lw=1.1, ls=(0, (3, 2.5)), zorder=zorder_base)
    ax.plot(r_in * np.cos(theta_back), z_bot + r_in * np.sin(theta_back) * eps,
            color=c_line, lw=0.9, ls=(0, (3, 2.5)), zorder=zorder_base)

    xin_b = r_in * np.cos(theta_back)
    yin_b_bot = z_bot + r_in * np.sin(theta_back) * eps
    yin_b_top = z_top + r_in * np.sin(theta_back) * eps
    poly_in = np.vstack([
        np.column_stack([xin_b, yin_b_bot]),
        np.column_stack([xin_b[::-1], yin_b_top[::-1]])
    ])
    ax.add_patch(Polygon(poly_in, closed=True, facecolor=c_fill, alpha=alpha_fill * 0.45, edgecolor='none', zorder=zorder_base+1))

    xout_f = r_out * np.cos(theta_front)
    yout_f_bot = z_bot + r_out * np.sin(theta_front) * eps
    yout_f_top = z_top + r_out * np.sin(theta_front) * eps
    poly_out = np.vstack([
        np.column_stack([xout_f, yout_f_bot]),
        np.column_stack([xout_f[::-1], yout_f_top[::-1]])
    ])
    ax.add_patch(Polygon(poly_out, closed=True, facecolor=c_fill, alpha=alpha_fill * 0.75, edgecolor='none', zorder=zorder_base+2))
    ax.plot(xout_f, yout_f_bot, color=c_line, lw=1.4, ls=ls_line, zorder=zorder_base+3)

    xin_f = r_in * np.cos(theta_front)
    yin_f_bot = z_bot + r_in * np.sin(theta_front) * eps
    ax.plot(xin_f, yin_f_bot, color=c_line, lw=0.85, ls=(0, (3, 2.5)), zorder=zorder_base+1)

    ax.plot([-r_out, -r_out], [z_bot, z_top], color=c_line, lw=1.4, ls=ls_line, zorder=zorder_base+4)
    ax.plot([r_out, r_out], [z_bot, z_top], color=c_line, lw=1.4, ls=ls_line, zorder=zorder_base+4)
    ax.plot([-r_in, -r_in], [z_bot, z_top], color=c_line, lw=1.0, ls=ls_line, zorder=zorder_base+4)
    ax.plot([r_in, r_in], [z_bot, z_top], color=c_line, lw=1.0, ls=ls_line, zorder=zorder_base+4)

    x_ann_out = r_out * np.cos(theta_full)
    y_ann_out = z_top + r_out * np.sin(theta_full) * eps
    x_ann_in = r_in * np.cos(theta_full[::-1])
    y_ann_in = z_top + r_in * np.sin(theta_full[::-1]) * eps

    verts_out = np.column_stack([x_ann_out, y_ann_out])
    verts_in = np.column_stack([x_ann_in, y_ann_in])
    path_verts = np.vstack([verts_out, verts_out[0:1], verts_in, verts_in[0:1]])
    path_codes = ([Path.MOVETO] + [Path.LINETO]*(len(verts_out)-1) + [Path.CLOSEPOLY] +
                  [Path.MOVETO] + [Path.LINETO]*(len(verts_in)-1) + [Path.CLOSEPOLY])
    annulus_path = Path(path_verts, path_codes)
    patch_annulus = PathPatch(annulus_path, facecolor=c_fill, alpha=alpha_fill, edgecolor='none', zorder=zorder_base+5)
    ax.add_patch(patch_annulus)

    ax.plot(x_ann_out, y_ann_out, color=c_line, lw=1.5, ls=ls_line, zorder=zorder_base+6)
    ax.plot(x_ann_in, y_ann_in, color=c_line, lw=1.2, ls=ls_line, zorder=zorder_base+6)

def draw_macro_cylinder_shrunk(ax, 
                               R0=2.0, 
                               shrink_ratio=0.80, 
                               H=10.5, 
                               eps=0.20,
                               r_ring0=1.35, 
                               dr0=0.18, 
                               z_ring=4.8, 
                               dz=0.22,
                               num_radial=5, 
                               num_layers=7, 
                               num_meridians=8,
                               style_mode='A'):
    Rs = R0 * shrink_ratio
    r_ring_s = r_ring0 * shrink_ratio
    dr_s = dr0 * shrink_ratio

    r_grids0 = np.linspace(R0 / num_radial, R0 * (num_radial - 1) / num_radial, num_radial - 1)
    z_grids = np.linspace(H / num_layers, H * (num_layers - 1) / num_layers, num_layers - 1)

    theta_full = np.linspace(0, 2 * np.pi, 300)
    theta_front = np.linspace(np.pi, 2 * np.pi, 150)
    theta_back = np.linspace(0, np.pi, 150)

    c_edge_out = '#0F172A' if style_mode != 'B' else '#64748B'
    ls_out = '-' if style_mode != 'B' else (0, (6, 4))
    lw_out = 2.0 if style_mode != 'B' else 1.6

    c_edge_shrunk = '#0F172A'
    c_grid_solid = '#94A3B8'
    c_grid_dash = '#CBD5E1'

    for rg in r_grids0:
        ax.plot(rg * np.cos(theta_back), rg * np.sin(theta_back) * eps,
                color=c_grid_dash, lw=0.75, ls=(0, (3.5, 3)), zorder=2)
        ax.plot(rg * np.cos(theta_front), rg * np.sin(theta_front) * eps,
                color=c_grid_solid, lw=0.85, ls='-', zorder=2)

    ax.plot(R0 * np.cos(theta_back), R0 * np.sin(theta_back) * eps,
            color=c_edge_out, lw=lw_out * 0.8, ls=(0, (4, 3)), zorder=3)
    ax.plot(R0 * np.cos(theta_front), R0 * np.sin(theta_front) * eps,
            color=c_edge_out, lw=lw_out, ls=ls_out, zorder=5)

    ax.plot(Rs * np.cos(theta_front), Rs * np.sin(theta_front) * eps,
            color=c_edge_shrunk, lw=1.8, ls='-', zorder=6)

    poly_shrunk_front = np.vstack([
        np.column_stack([Rs * np.cos(theta_front), Rs * np.sin(theta_front) * eps]),
        np.column_stack([Rs * np.cos(theta_front[::-1]), H + Rs * np.sin(theta_front[::-1]) * eps])
    ])
    shrunk_fill_color = '#E2E8F0' if style_mode in ['A', 'C'] else '#F1F5F9'
    ax.add_patch(Polygon(poly_shrunk_front, closed=True, facecolor=shrunk_fill_color, alpha=0.55, edgecolor='none', zorder=4))

    poly_shrunk_top = np.column_stack([Rs * np.cos(theta_full), H + Rs * np.sin(theta_full) * eps])
    ax.add_patch(Polygon(poly_shrunk_top, closed=True, facecolor=shrunk_fill_color, alpha=0.85, edgecolor='none', zorder=7))
    ax.plot(Rs * np.cos(theta_full), H + Rs * np.sin(theta_full) * eps, color=c_edge_shrunk, lw=1.8, ls='-', zorder=8)

    ax.plot([-Rs, -Rs], [0, H], color=c_edge_shrunk, lw=2.0, ls='-', zorder=7)
    ax.plot([Rs, Rs], [0, H], color=c_edge_shrunk, lw=2.0, ls='-', zorder=7)

    for zg in z_grids:
        if abs(zg - z_ring) < dz * 1.3:
            continue
        ax.plot(R0 * np.cos(theta_back), zg + R0 * np.sin(theta_back) * eps,
                color=c_grid_dash, lw=0.75, ls=(0, (3.5, 3)), zorder=2)
        ax.plot(R0 * np.cos(theta_front), zg + R0 * np.sin(theta_front) * eps,
                color=c_grid_solid, lw=0.85, ls='-', zorder=2)
        ax.plot(Rs * np.cos(theta_front), zg + Rs * np.sin(theta_front) * eps,
                color='#94A3B8', lw=0.9, ls='-', zorder=5)

    phi_meridians = np.linspace(np.pi, 2 * np.pi, num_meridians + 2)[1:-1]
    for phi in phi_meridians:
        xm0 = R0 * np.cos(phi)
        ym0_bot = R0 * np.sin(phi) * eps
        ym0_top = H + R0 * np.sin(phi) * eps
        ax.plot([xm0, xm0], [ym0_bot, ym0_top], color=c_grid_solid, lw=0.75, zorder=2)

    if style_mode == 'A':
        draw_ring_3d(ax, r_ring0, dr0, z_ring, dz, eps=eps,
                     c_line='#EF4444', c_fill='#FCA5A5', alpha_fill=0.35, is_dashed=True, zorder_base=10)
        draw_ring_3d(ax, r_ring_s, dr_s, z_ring, dz, eps=eps,
                     c_line='#B91C1C', c_fill='#DC2626', alpha_fill=0.75, is_dashed=False, zorder_base=16)
        phi_arr = 1.5 * np.pi
        x_src = r_ring0 * np.cos(phi_arr)
        y_src = z_ring + r_ring0 * np.sin(phi_arr) * eps - 0.05
        x_tgt = r_ring_s * np.cos(phi_arr)
        y_tgt = z_ring + r_ring_s * np.sin(phi_arr) * eps + 0.05
        arr = FancyArrowPatch((x_src, y_src), (x_tgt, y_tgt),
                               arrowstyle='-|>,head_length=5.0,head_width=3.2',
                               color='#B91C1C', lw=1.8, zorder=25)
        ax.add_patch(arr)

    elif style_mode == 'B':
        draw_ring_3d(ax, r_ring0, dr0, z_ring, dz, eps=eps,
                     c_line='#C0392B', c_fill='#FF7675', alpha_fill=0.35, is_dashed=True, zorder_base=10)
        draw_ring_3d(ax, r_ring_s, dr_s, z_ring, dz, eps=eps,
                     c_line='#991B1B', c_fill='#DC2626', alpha_fill=0.85, is_dashed=False, zorder_base=16)

    elif style_mode == 'C':
        draw_ring_3d(ax, r_ring0, dr0, z_ring, dz, eps=eps,
                     c_line='#DC2626', c_fill='#F87171', alpha_fill=0.40, is_dashed=False, zorder_base=10)
        draw_ring_3d(ax, r_ring_s, dr_s, z_ring, dz, eps=eps,
                     c_line='#7F1D1D', c_fill='#991B1B', alpha_fill=0.80, is_dashed=False, zorder_base=16)

    elif style_mode == 'D':
        # 风格 D: 真实微元全宽度，两圆环在径向发生空间重叠 (Overlap)
        dr_cell0 = 0.32
        dr_cell_s = dr_cell0 * shrink_ratio
        # 初始圆环 (较宽微元)
        draw_ring_3d(ax, r_ring0, dr_cell0, z_ring, dz, eps=eps,
                     c_line='#DC2626', c_fill='#FCA5A5', alpha_fill=0.35, is_dashed=True, zorder_base=10)
        # 收缩圆环 (向内位移并发生物理交叠)
        draw_ring_3d(ax, r_ring_s, dr_cell_s, z_ring, dz, eps=eps,
                     c_line='#991B1B', c_fill='#DC2626', alpha_fill=0.75, is_dashed=False, zorder_base=16)
        
        # 径向收缩微箭头
        phi_arr = 1.5 * np.pi
        x_src = (r_ring0 + dr_cell0/2.0) * np.cos(phi_arr)
        y_src = z_ring + (r_ring0 + dr_cell0/2.0) * np.sin(phi_arr) * eps - 0.05
        x_tgt = (r_ring_s - dr_cell_s/2.0) * np.cos(phi_arr)
        y_tgt = z_ring + (r_ring_s - dr_cell_s/2.0) * np.sin(phi_arr) * eps + 0.05
        arr = FancyArrowPatch((x_src, y_src), (x_tgt, y_tgt),
                               arrowstyle='-|>,head_length=5.0,head_width=3.2',
                               color='#991B1B', lw=1.8, zorder=25)
        ax.add_patch(arr)

    ax.plot([-R0, -R0], [0, H], color=c_edge_out, lw=lw_out, ls=ls_out, zorder=6)
    ax.plot([R0, R0], [0, H], color=c_edge_out, lw=lw_out, ls=ls_out, zorder=6)

    for rg in r_grids0:
        if abs(rg - Rs) < 1e-4:
            continue
        ax.plot(rg * np.cos(theta_full), H + rg * np.sin(theta_full) * eps,
                color=c_grid_solid, lw=0.85, ls='-', zorder=7)
    ax.plot(R0 * np.cos(theta_full), H + R0 * np.sin(theta_full) * eps,
            color=c_edge_out, lw=lw_out, ls=ls_out, zorder=8)

    z_start = -0.75
    z_end = H + 1.30
    draw_beveled_3d_arrow(ax, (0, z_start), (0, z_end), head_len=0.70, head_w=0.20, lw=2.0, zorder=20)
    ax.text(0, z_end + 0.32, r'$z$', fontsize=22, ha='center', va='bottom', color='#0F172A', zorder=25)

    phi_rad = np.radians(-24)
    r_axis_len = R0 + 1.35
    x_r_end = r_axis_len * np.cos(phi_rad)
    y_r_end = r_axis_len * np.sin(phi_rad) * eps
    draw_beveled_3d_arrow(ax, (0, 0), (x_r_end, y_r_end), head_len=0.70, head_w=0.20, lw=2.0, zorder=20)
    ax.text(x_r_end + 0.28, y_r_end - 0.05, r'$r$', fontsize=22, ha='left', va='center', color='#0F172A', zorder=25)

    ax.scatter([0], [0], s=28, facecolor='#FFFFFF', edgecolor='#0F172A', lw=1.8, zorder=24)

    ax.set_xlim(-R0 - 0.7, r_axis_len + 0.9)
    ax.set_ylim(z_start - 0.5, z_end + 0.9)

def main():
    eda_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    out_dir = os.path.join(eda_dir, 'task3_candidates')
    os.makedirs(out_dir, exist_ok=True)

    # 1. 对比总图 (1 x 4 四大方案横向横评)
    fig, axes = plt.subplots(1, 4, figsize=(18.0, 9.5), dpi=300)
    fig.patch.set_facecolor('#FFFFFF')

    titles = [
        '方案 A: 虚实同轴分离 (初始虚线珊瑚红 + 收缩深红实线)',
        '方案 B: 轮廓脱胎 (初始外边界虚线 + 收缩实柱体)',
        '方案 C: 双实线高对比 (经典正红 + 紧凑深酒红)',
        '方案 D: 控制体径向空间重叠 (微元厚度重叠交错)'
    ]

    for idx, mode in enumerate(['A', 'B', 'C', 'D']):
        ax = axes[idx]
        ax.set_aspect('equal')
        ax.axis('off')
        draw_macro_cylinder_shrunk(ax, style_mode=mode)
        ax.set_title(titles[idx], fontsize=10.5, fontweight='bold', color='#0F172A', pad=12)

    plt.tight_layout()
    cmp_path = os.path.join(out_dir, 'macro_cylinder_shrinkage_candidates_comparison.png')
    fig.savefig(cmp_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print(f'[OK] Comparison saved: {cmp_path}')

    # 2. 单图分别生成
    for mode in ['A', 'B', 'C', 'D']:
        fig_s = plt.figure(figsize=(4.8, 10.2), dpi=300)
        ax_s = fig_s.add_axes([0.08, 0.05, 0.84, 0.90])
        ax_s.set_aspect('equal')
        ax_s.axis('off')
        draw_macro_cylinder_shrunk(ax_s, style_mode=mode)
        
        single_path = os.path.join(out_dir, f'macro_cylinder_shrinkage_style_{mode.lower()}.png')
        fig_s.savefig(single_path, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close(fig_s)
        print(f'[OK] Single saved: {single_path}')

if __name__ == '__main__':
    main()
