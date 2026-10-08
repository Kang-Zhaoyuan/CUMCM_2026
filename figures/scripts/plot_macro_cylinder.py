"""
Final Generator for Slender FVM Macro Cylinder Diagram.
Addresses:
1. Scientific rigorous notation: Lowercase italic r and z for coordinate axes.
2. Authentic LaTeX Computer Modern font rendering (cmmi10).
3. Highly dimensional 3D beveled coordinate arrows, origin anchor, and perspective base grounding.
"""

import os
import shutil
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, PathPatch
from matplotlib.path import Path

# 严格配置 LaTeX Computer Modern 数学字体
plt.rcParams['mathtext.fontset'] = 'cm'
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.serif'] = ['Times New Roman', 'DejaVu Serif', 'STIXGeneral']

def draw_beveled_3d_arrow(ax, start, end, head_len=0.68, head_w=0.19,
                          notch=0.12, c_light='#64748b', c_dark='#1e293b',
                          c_line='#0f172a', lw=2.0, zorder=20):
    """
    绘制极具质感、棱角分明的 3D 棱面立体箭头 (Beveled 3D Vector Arrow)
    """
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
    
    # 箭杆
    ax.plot([start[0], notch_pt[0]], [start[1], notch_pt[1]],
            color=c_line, lw=lw, solid_capstyle='butt', zorder=zorder)
    
    p_tip = end
    p_left = base_center + head_w * v
    p_right = base_center - head_w * v
    
    # 斜上方受光面 (Light Slate)
    poly_light = np.array([p_tip, p_left, notch_pt])
    ax.add_patch(Polygon(poly_light, closed=True, facecolor=c_light, edgecolor=c_line, lw=0.7, zorder=zorder+1))
    
    # 背光暗面 (Deep Charcoal Navy)
    poly_dark = np.array([p_tip, notch_pt, p_right])
    ax.add_patch(Polygon(poly_dark, closed=True, facecolor=c_dark, edgecolor=c_line, lw=0.7, zorder=zorder+1))
    
    # 中轴立体反光脊线
    ax.plot([p_tip[0], notch_pt[0]], [p_tip[1], notch_pt[1]], color='#cbd5e1', lw=0.85, zorder=zorder+2)

def draw_fvm_macro_cylinder(ax, R=2.0, H=10.5, eps=0.20,
                            r_ring=1.35, dr=0.14, z_ring=4.8, dz=0.22,
                            axis_mode='perspective_ray', num_meridians=8,
                            num_layers=7, num_radial=5):
    """
    绘制完整宏观圆柱有限体积网格模型
    """
    r_grids = np.linspace(R / num_radial, R * (num_radial - 1) / num_radial, num_radial - 1)
    z_grids = np.linspace(H / num_layers, H * (num_layers - 1) / num_layers, num_layers - 1)
    
    theta_full = np.linspace(0, 2 * np.pi, 300)
    theta_front = np.linspace(np.pi, 2 * np.pi, 150)
    theta_back = np.linspace(0, np.pi, 150)
    
    c_edge = '#111111'          # 外轮廓深黑
    c_grid_solid = '#8a9ba8'    # 可见网格雅致岩灰
    c_grid_dash = '#c4cdd5'     # 隐藏网格柔和浅灰
    c_red_line = '#d63031'      # 正红轮廓
    c_red_fill = '#ff7675'      # 正红填充
    
    # -------------------------------------------------------------
    # 0. 底面柱坐标透视扇面 (立体化基准，契合 fvm_flux_annotated_v2.png)
    # -------------------------------------------------------------
    if axis_mode == 'perspective_ray':
        phi_sec = np.linspace(0, np.radians(-26), 35)
        r_sec = R * 0.96
        sec_x = [0.0] + list(r_sec * np.cos(phi_sec)) + [0.0]
        sec_y = [0.0] + list(r_sec * np.sin(phi_sec) * eps) + [0.0]
        ax.fill(sec_x, sec_y, color='#EBF3FB', alpha=0.90, zorder=3)
        ax.plot(sec_x, sec_y, color='#4A7C99', lw=1.2, zorder=4)
        
        # 极轻底面方位角弧线 (不标注字母，仅起立体空间暗示作用)
        r_arc = R * 0.52
        phi_arc = np.linspace(0, np.radians(-26), 25)
        ax.plot(r_arc * np.cos(phi_arc), r_arc * np.sin(phi_arc) * eps,
                color='#3B6077', lw=1.0, ls='-', zorder=5)
    
    # -------------------------------------------------------------
    # 1. 底部端面网格 (z = 0)
    # -------------------------------------------------------------
    for rg in r_grids:
        ax.plot(rg * np.cos(theta_back), rg * np.sin(theta_back) * eps,
                color=c_grid_dash, lw=0.8, ls=(0, (3.5, 3)), zorder=2)
        ax.plot(rg * np.cos(theta_front), rg * np.sin(theta_front) * eps,
                color=c_grid_solid, lw=0.85, ls='-', zorder=2)
    
    ax.plot(R * np.cos(theta_back), R * np.sin(theta_back) * eps,
            color=c_edge, lw=1.6, ls=(0, (4, 3)), zorder=3)
    ax.plot(R * np.cos(theta_front), R * np.sin(theta_front) * eps,
            color=c_edge, lw=2.2, ls='-', zorder=5)
    
    # -------------------------------------------------------------
    # 2. 轴向各高度层水平截面网格 (z_grids)
    # -------------------------------------------------------------
    for zg in z_grids:
        if abs(zg - z_ring) < dz * 1.3:
            continue
        ax.plot(R * np.cos(theta_back), zg + R * np.sin(theta_back) * eps,
                color=c_grid_dash, lw=0.75, ls=(0, (3.5, 3)), zorder=2)
        ax.plot(R * np.cos(theta_front), zg + R * np.sin(theta_front) * eps,
                color=c_grid_solid, lw=0.85, ls='-', zorder=2)
    
    # -------------------------------------------------------------
    # 3. 纵向外表面素线与内壳经线网格
    # -------------------------------------------------------------
    phi_meridians = np.linspace(np.pi, 2 * np.pi, num_meridians + 2)[1:-1]
    for phi in phi_meridians:
        xm = R * np.cos(phi)
        ym_bot = R * np.sin(phi) * eps
        ym_top = H + R * np.sin(phi) * eps
        ax.plot([xm, xm], [ym_bot, ym_top], color=c_grid_solid, lw=0.8, zorder=2)
    
    for rg in r_grids:
        ax.plot([rg, rg], [0, H], color=c_grid_solid, lw=0.55, ls=':', alpha=0.7, zorder=2)
        ax.plot([-rg, -rg], [0, H], color=c_grid_solid, lw=0.55, ls=':', alpha=0.7, zorder=2)
    
    # -------------------------------------------------------------
    # 4. 红色超薄圆环 (待求解控制体单元，厚度非常薄)
    # -------------------------------------------------------------
    r_in = r_ring - dr / 2.0
    r_out = r_ring + dr / 2.0
    z_bot = z_ring - dz / 2.0
    z_top = z_ring + dz / 2.0
    
    # 红色圆环下底面后侧消隐线 (红色虚线)
    ax.plot(r_out * np.cos(theta_back), z_bot + r_out * np.sin(theta_back) * eps,
            color=c_red_line, lw=1.2, ls=(0, (3, 2.5)), zorder=10)
    ax.plot(r_in * np.cos(theta_back), z_bot + r_in * np.sin(theta_back) * eps,
            color=c_red_line, lw=1.0, ls=(0, (3, 2.5)), zorder=10)
    
    # 红色圆环内壁后表面阴影
    xin_b = r_in * np.cos(theta_back)
    yin_b_bot = z_bot + r_in * np.sin(theta_back) * eps
    yin_b_top = z_top + r_in * np.sin(theta_back) * eps
    poly_in = np.vstack([
        np.column_stack([xin_b, yin_b_bot]),
        np.column_stack([xin_b[::-1], yin_b_top[::-1]])
    ])
    ax.add_patch(Polygon(poly_in, closed=True, facecolor=c_red_fill, alpha=0.22, edgecolor='none', zorder=11))
    
    # 红色圆环外侧前表面
    xout_f = r_out * np.cos(theta_front)
    yout_f_bot = z_bot + r_out * np.sin(theta_front) * eps
    yout_f_top = z_top + r_out * np.sin(theta_front) * eps
    poly_out = np.vstack([
        np.column_stack([xout_f, yout_f_bot]),
        np.column_stack([xout_f[::-1], yout_f_top[::-1]])
    ])
    ax.add_patch(Polygon(poly_out, closed=True, facecolor=c_red_fill, alpha=0.38, edgecolor='none', zorder=12))
    ax.plot(xout_f, yout_f_bot, color=c_red_line, lw=1.5, ls='-', zorder=13)
    
    xin_f = r_in * np.cos(theta_front)
    yin_f_bot = z_bot + r_in * np.sin(theta_front) * eps
    ax.plot(xin_f, yin_f_bot, color=c_red_line, lw=0.9, ls=(0, (3, 2.5)), zorder=10)
    
    # 轮廓垂直素线
    ax.plot([-r_out, -r_out], [z_bot, z_top], color=c_red_line, lw=1.5, ls='-', zorder=14)
    ax.plot([r_out, r_out], [z_bot, z_top], color=c_red_line, lw=1.5, ls='-', zorder=14)
    ax.plot([-r_in, -r_in], [z_bot, z_top], color=c_red_line, lw=1.1, ls='-', zorder=14)
    ax.plot([r_in, r_in], [z_bot, z_top], color=c_red_line, lw=1.1, ls='-', zorder=14)
    
    # 红色圆环上端面 (100% 连续实线)
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
    patch_annulus = PathPatch(annulus_path, facecolor=c_red_fill, alpha=0.60, edgecolor='none', zorder=15)
    ax.add_patch(patch_annulus)
    
    ax.plot(x_ann_out, y_ann_out, color=c_red_line, lw=1.6, ls='-', zorder=16)
    ax.plot(x_ann_in, y_ann_in, color=c_red_line, lw=1.3, ls='-', zorder=16)
    
    # -------------------------------------------------------------
    # 5. 圆柱最外侧边界素线 & 顶面 (100% 连续实线)
    # -------------------------------------------------------------
    ax.plot([-R, -R], [0, H], color=c_edge, lw=2.2, ls='-', zorder=6)
    ax.plot([R, R], [0, H], color=c_edge, lw=2.2, ls='-', zorder=6)
    
    for rg in r_grids:
        ax.plot(rg * np.cos(theta_full), H + rg * np.sin(theta_full) * eps,
                color=c_grid_solid, lw=0.9, ls='-', zorder=7)
    ax.plot(R * np.cos(theta_full), H + R * np.sin(theta_full) * eps,
            color=c_edge, lw=2.2, ls='-', zorder=8)
    
    # -------------------------------------------------------------
    # 6. 立体坐标轴 (LaTeX 专业数学格式: 严谨小写斜体 $z$ 与 $r$)
    # -------------------------------------------------------------
    # z 轴: 贯穿中心对称轴向上延伸
    z_start = -0.75
    z_end = H + 1.30
    draw_beveled_3d_arrow(ax, (0, z_start), (0, z_end), head_len=0.70, head_w=0.20, lw=2.0, zorder=20)
    ax.text(0, z_end + 0.32, r'$z$', fontsize=22, ha='center', va='bottom', color='#0f172a', zorder=25)
    
    # r 轴绘制
    if axis_mode == 'perspective_ray':
        # 沿底面椭圆透视平面向前下方延伸，空间透视感最强
        phi_rad = np.radians(-24)
        r_axis_len = R + 1.35
        x_r_end = r_axis_len * np.cos(phi_rad)
        y_r_end = r_axis_len * np.sin(phi_rad) * eps
        draw_beveled_3d_arrow(ax, (0, 0), (x_r_end, y_r_end), head_len=0.70, head_w=0.20, lw=2.0, zorder=20)
        ax.text(x_r_end + 0.28, y_r_end - 0.05, r'$r$', fontsize=22, ha='left', va='center', color='#0f172a', zorder=25)
        ax.set_xlim(-R - 0.7, r_axis_len + 0.9)
    else:
        # 正横向 3D 棱面轴
        r_end = R + 1.40
        draw_beveled_3d_arrow(ax, (0, 0), (r_end, 0), head_len=0.70, head_w=0.20, lw=2.0, zorder=20)
        ax.text(r_end + 0.32, 0, r'$r$', fontsize=22, ha='left', va='center', color='#0f172a', zorder=25)
        ax.set_xlim(-R - 0.7, r_end + 0.9)
    
    # 3D 空间坐标原点定位锚 (白色金属质感圆核 + 纯黑外圈)
    ax.scatter([0], [0], s=28, facecolor='#ffffff', edgecolor='#0f172a', lw=1.8, zorder=24)
    
    ax.set_ylim(z_start - 0.5, z_end + 0.9)

def main():
    eda_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    archive_dir = os.path.join(eda_dir, "Archive", "images")
    os.makedirs(archive_dir, exist_ok=True)
    
    # 1. 方案 A (推荐定稿版): 透视立体径向轴 + 柱坐标底面扇面 (归档子图)
    fig_a = plt.figure(figsize=(4.6, 10.2), dpi=300)
    ax_a = fig_a.add_axes([0.08, 0.05, 0.84, 0.90])
    ax_a.set_aspect('equal')
    ax_a.axis('off')
    draw_fvm_macro_cylinder(ax_a, axis_mode='perspective_ray')
    
    out_main = os.path.join(archive_dir, "fvm_macro_cylinder.png")
    plt.savefig(out_main, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"[OK] 导出透视立体推荐版 (归档): {out_main}")
    
    # 2. 方案 B (备选经典版): 横向 3D 棱面立体轴 (归档子图)
    fig_b = plt.figure(figsize=(4.6, 10.2), dpi=300)
    ax_b = fig_b.add_axes([0.08, 0.05, 0.84, 0.90])
    ax_b.set_aspect('equal')
    ax_b.axis('off')
    draw_fvm_macro_cylinder(ax_b, axis_mode='transverse')
    
    out_trans = os.path.join(archive_dir, "fvm_macro_cylinder_transverse.png")
    plt.savefig(out_trans, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"[OK] 导出横向棱面备选版 (归档): {out_trans}")

if __name__ == '__main__':
    main()
