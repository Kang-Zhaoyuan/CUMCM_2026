# -*- coding: utf-8 -*-
"""
动边界收缩机制与网格划分示意图绘制脚本 (Task 3 冻结定稿)
========================================================================
图件名称: moving_boundary_mesh_shrinkage.png
对应文件: eda_figures/moving_boundary_mesh_shrinkage.png
功能说明:
- 左子图: 宏观收缩圆柱与环形微元几何域 (双实线高对比 Style C, 无多余内部微箭头)
- 局部放大框: 严格居中包裹物料环边缘 (x2=764.0)，与较小圆柱内母线保持安全净空
- 透射虚线: 黑色等间距细虚线，由局部微元框投射至右侧微观卡片
- 右子图: 微观 3D 厚圆环收缩拓扑保持示意图
  * 药材厚度严格守恒 (h_s = h_0)
  * 网格拓扑 3x3x3 分割完全保持
  * 粗实线 (初始状态) vs 细实线 (收缩状态)
  * 极简柱坐标系 (+z, +r)
  * 时间演变标注 t 与 t + \Delta t，辅以共线微型演化箭头 (倾角 theta = arctan(0.178))
"""

import os
import sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, PathPatch, Rectangle, FancyArrowPatch
from matplotlib.path import Path
from PIL import Image

def get_paths():
    cur_dir = os.path.dirname(os.path.abspath(__file__))
    eda_dir = os.path.abspath(os.path.join(cur_dir, '..'))
    archive_img_dir = os.path.join(eda_dir, 'Archive', 'images')
    output_png = os.path.join(eda_dir, 'moving_boundary_mesh_shrinkage.png')
    return cur_dir, eda_dir, archive_img_dir, output_png

def find_or_generate_macro_cylinder(eda_dir, archive_img_dir):
    """查找或动态生成宏观圆柱收缩子图 (Style C)"""
    candidate_paths = [
        os.path.join(archive_img_dir, 'macro_cylinder_shrinkage_style_c.png'),
        os.path.join(archive_img_dir, 'task3_candidates', 'macro_cylinder_shrinkage_style_c.png'),
        os.path.join(eda_dir, 'task3_candidates', 'macro_cylinder_shrinkage_style_c.png'),
    ]
    for p in candidate_paths:
        if os.path.exists(p):
            return p
    
    # 若均不存在，动态纯 Python 渲染生成
    gen_path = os.path.join(archive_img_dir, 'macro_cylinder_shrinkage_style_c.png')
    os.makedirs(os.path.dirname(gen_path), exist_ok=True)
    draw_and_save_macro_cylinder_c(gen_path)
    return gen_path

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
    poly_in = np.vstack([np.column_stack([xin_b, yin_b_bot]), np.column_stack([xin_b[::-1], yin_b_top[::-1]])])
    ax.add_patch(Polygon(poly_in, closed=True, facecolor=c_fill, alpha=alpha_fill * 0.45, edgecolor='none', zorder=zorder_base+1))

    xout_f = r_out * np.cos(theta_front)
    yout_f_bot = z_bot + r_out * np.sin(theta_front) * eps
    yout_f_top = z_top + r_out * np.sin(theta_front) * eps
    poly_out = np.vstack([np.column_stack([xout_f, yout_f_bot]), np.column_stack([xout_f[::-1], yout_f_top[::-1]])])
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

def draw_and_save_macro_cylinder_c(save_path):
    R0 = 2.0
    shrink_ratio = 0.80
    H = 10.5
    eps = 0.20
    r_ring0 = 1.35
    dr0 = 0.18
    z_ring = 4.8
    dz = 0.22
    num_radial = 5
    num_layers = 7
    num_meridians = 8

    fig_s = plt.figure(figsize=(4.8, 10.2), dpi=300)
    ax = fig_s.add_axes([0.08, 0.05, 0.84, 0.90])
    ax.set_aspect('equal')
    ax.axis('off')

    Rs = R0 * shrink_ratio
    r_ring_s = r_ring0 * shrink_ratio
    dr_s = dr0 * shrink_ratio

    r_grids0 = np.linspace(R0 / num_radial, R0 * (num_radial - 1) / num_radial, num_radial - 1)
    z_grids = np.linspace(H / num_layers, H * (num_layers - 1) / num_layers, num_layers - 1)

    theta_full = np.linspace(0, 2 * np.pi, 300)
    theta_front = np.linspace(np.pi, 2 * np.pi, 150)
    theta_back = np.linspace(0, np.pi, 150)

    c_edge_out = '#0F172A'
    c_edge_shrunk = '#0F172A'
    c_grid_solid = '#94A3B8'
    c_grid_dash = '#CBD5E1'

    for rg in r_grids0:
        ax.plot(rg * np.cos(theta_back), rg * np.sin(theta_back) * eps, color=c_grid_dash, lw=0.75, ls=(0, (3.5, 3)), zorder=2)
        ax.plot(rg * np.cos(theta_front), rg * np.sin(theta_front) * eps, color=c_grid_solid, lw=0.85, ls='-', zorder=2)

    ax.plot(R0 * np.cos(theta_back), R0 * np.sin(theta_back) * eps, color=c_edge_out, lw=1.6, ls=(0, (4, 3)), zorder=3)
    ax.plot(R0 * np.cos(theta_front), R0 * np.sin(theta_front) * eps, color=c_edge_out, lw=2.0, ls='-', zorder=5)

    ax.plot(Rs * np.cos(theta_front), Rs * np.sin(theta_front) * eps, color=c_edge_shrunk, lw=1.8, ls='-', zorder=6)

    poly_shrunk_front = np.vstack([
        np.column_stack([Rs * np.cos(theta_front), Rs * np.sin(theta_front) * eps]),
        np.column_stack([Rs * np.cos(theta_front[::-1]), H + Rs * np.sin(theta_front[::-1]) * eps])
    ])
    ax.add_patch(Polygon(poly_shrunk_front, closed=True, facecolor='#E2E8F0', alpha=0.55, edgecolor='none', zorder=4))

    poly_shrunk_top = np.column_stack([Rs * np.cos(theta_full), H + Rs * np.sin(theta_full) * eps])
    ax.add_patch(Polygon(poly_shrunk_top, closed=True, facecolor='#E2E8F0', alpha=0.85, edgecolor='none', zorder=7))
    ax.plot(Rs * np.cos(theta_full), H + Rs * np.sin(theta_full) * eps, color=c_edge_shrunk, lw=1.8, ls='-', zorder=8)

    ax.plot([-Rs, -Rs], [0, H], color=c_edge_shrunk, lw=2.0, ls='-', zorder=7)
    ax.plot([Rs, Rs], [0, H], color=c_edge_shrunk, lw=2.0, ls='-', zorder=7)

    for zg in z_grids:
        if abs(zg - z_ring) < dz * 1.3:
            continue
        ax.plot(R0 * np.cos(theta_back), zg + R0 * np.sin(theta_back) * eps, color=c_grid_dash, lw=0.75, ls=(0, (3.5, 3)), zorder=2)
        ax.plot(R0 * np.cos(theta_front), zg + R0 * np.sin(theta_front) * eps, color=c_grid_solid, lw=0.85, ls='-', zorder=2)
        ax.plot(Rs * np.cos(theta_front), zg + Rs * np.sin(theta_front) * eps, color='#94A3B8', lw=0.9, ls='-', zorder=5)

    phi_meridians = np.linspace(np.pi, 2 * np.pi, num_meridians + 2)[1:-1]
    for phi in phi_meridians:
        xm0 = R0 * np.cos(phi)
        ym0_bot = R0 * np.sin(phi) * eps
        ym0_top = H + R0 * np.sin(phi) * eps
        ax.plot([xm0, xm0], [ym0_bot, ym0_top], color=c_grid_solid, lw=0.75, zorder=2)

    # Style C: 双实线高对比 (初始正红 + 收缩深酒红，无任何内部多余箭头)
    draw_ring_3d(ax, r_ring0, dr0, z_ring, dz, eps=eps,
                 c_line='#DC2626', c_fill='#F87171', alpha_fill=0.40, is_dashed=False, zorder_base=10)
    draw_ring_3d(ax, r_ring_s, dr_s, z_ring, dz, eps=eps,
                 c_line='#7F1D1D', c_fill='#991B1B', alpha_fill=0.80, is_dashed=False, zorder_base=16)

    ax.plot([-R0, -R0], [0, H], color=c_edge_out, lw=2.0, ls='-', zorder=6)
    ax.plot([R0, R0], [0, H], color=c_edge_out, lw=2.0, ls='-', zorder=6)

    for rg in r_grids0:
        if abs(rg - Rs) < 1e-4:
            continue
        ax.plot(rg * np.cos(theta_full), H + rg * np.sin(theta_full) * eps, color=c_grid_solid, lw=0.85, ls='-', zorder=7)
    ax.plot(R0 * np.cos(theta_full), H + R0 * np.sin(theta_full) * eps, color=c_edge_out, lw=2.0, ls='-', zorder=8)

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

    fig_s.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close(fig_s)

def generate_right_micro_subfigure(raw_png_path, temp_out_path):
    """从 3D 原生线稿生成带有坐标轴、时间标注与共线微型箭头的右子图"""
    img = Image.open(raw_png_path)
    arr = np.array(img.convert('L'))
    non_white = arr < 250
    y_idx, x_idx = np.where(non_white)
    cx = int((np.min(x_idx) + np.max(x_idx)) / 2)
    cy = int((np.min(y_idx) + np.max(y_idx)) / 2)
    span = max(np.max(x_idx) - np.min(x_idx), np.max(y_idx) - np.min(y_idx))
    pad = int(span * 0.44)
    R_crop = int(span / 2 + pad)

    crop_box = (cx - R_crop, cy - R_crop, cx + R_crop, cy + R_crop)
    base_img = img.crop(crop_box).transpose(Image.FLIP_LEFT_RIGHT)
    cw, ch = base_img.size

    plt.rcParams['mathtext.fontset'] = 'cm'
    plt.rcParams['font.serif'] = ['Times New Roman', 'DejaVu Serif']
    plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'DejaVu Sans']

    m = 0.178
    th = np.arctan(m)
    u = np.array([np.cos(th), np.sin(th)])
    v = np.array([-u[1], u[0]])

    fig, ax = plt.subplots(figsize=(10, 10), dpi=300)
    ax.imshow(base_img, extent=[0, cw, ch, 0])
    ax.set_xlim(0, cw)
    ax.set_ylim(ch, 0)
    ax.axis('off')

    # 1. 柱坐标系 (+z, +r)
    orig_x = cw * 0.10
    orig_y = ch * 0.68
    axis_len = cw * 0.090

    z_top = np.array([orig_x, orig_y - axis_len * 1.15])
    r_tip = np.array([orig_x + axis_len * u[0], orig_y + axis_len * u[1]])
    p_orig = np.array([orig_x, orig_y])

    lw_axis = 2.2
    ax.plot([p_orig[0], z_top[0]], [p_orig[1], z_top[1]], color='#111111', lw=lw_axis, solid_capstyle='butt', zorder=20)
    ax.plot([p_orig[0], r_tip[0]], [p_orig[1], r_tip[1]], color='#111111', lw=lw_axis, solid_capstyle='butt', zorder=20)
    ax.plot(orig_x, orig_y, 'o', color='#111111', markersize=2.2, zorder=25)

    hl = 14.0
    hw = 6.5
    fontsize = 17

    # +z 箭头
    ax.plot([z_top[0] - hw, z_top[0], z_top[0] + hw],
            [z_top[1] + hl, z_top[1], z_top[1] + hl],
            color='#111111', lw=lw_axis, solid_joinstyle='miter', solid_capstyle='round', zorder=22)
    ax.text(z_top[0], z_top[1] - 16, r'$+z$', fontsize=fontsize, fontweight='bold', color='#111111', ha='center', va='bottom')

    # +r 箭头
    p_w1 = r_tip - hl * u + hw * v
    p_w2 = r_tip - hl * u - hw * v
    ax.plot([p_w1[0], r_tip[0], p_w2[0]],
            [p_w1[1], r_tip[1], p_w2[1]],
            color='#111111', lw=lw_axis, solid_joinstyle='miter', solid_capstyle='round', zorder=22)
    ax.text(r_tip[0] + 16, r_tip[1] + 4, r'$+r$', fontsize=fontsize, fontweight='bold', color='#111111', ha='left', va='center')

    # 2. 时间标注与共线微型演化箭头
    dy = 45.0
    p1 = np.array([444.0, 950.0 + dy])
    p2 = np.array([910.0, 1040.0 + dy])

    ax.text(p1[0], p1[1], r'$t + \Delta t$', fontsize=fontsize, color='#111111', ha='center', va='center', zorder=30)
    ax.text(p2[0], p2[1], r'$t$', fontsize=fontsize, color='#111111', ha='center', va='center', zorder=30)

    dp = p2 - p1
    dist_p = np.linalg.norm(dp)
    up = dp / dist_p

    t_param = (696.0 - p1[0]) / dp[0]
    p_arrow_center = p1 + t_param * dp

    arrow_len = 150.0
    half_L = arrow_len / 2.0
    p_start = p_arrow_center + half_L * up # 尾部位于右侧 t
    p_end = p_arrow_center - half_L * up   # 头部指向左侧 t + Delta t

    arr_fine = FancyArrowPatch(p_start, p_end,
                                connectionstyle='arc3,rad=0',
                                arrowstyle='-|>,head_length=6.5,head_width=3.8',
                                color='#111111', lw=1.35, zorder=30)
    ax.add_patch(arr_fine)

    fig.savefig(temp_out_path, dpi=300, bbox_inches='tight', pad_inches=0.05)
    plt.close(fig)

    c_img = Image.open(temp_out_path)
    c_arr = np.array(c_img.convert('L'))
    ys, xs = np.where(c_arr < 250)
    pad_x = int((xs.max() - xs.min()) * 0.06)
    pad_y = int((ys.max() - ys.min()) * 0.08)
    final_cropped = c_img.crop((xs.min() - pad_x, ys.min() - pad_y, xs.max() + pad_x, ys.max() + pad_y))
    final_cropped.save(temp_out_path)

def composite_moving_boundary_figure(left_img_path, right_img_path, output_path, box_x2=764.0):
    """合成宏微观多尺度动边界收缩图件 (300 DPI)"""
    im_left = Image.open(left_img_path).convert('RGBA')
    im_right = Image.open(right_img_path).convert('RGBA')

    W_l, H_l = im_left.size
    W_r, H_r = im_right.size

    target_H_l = 2300.0
    scale_l = target_H_l / float(H_l)
    disp_W_l = W_l * scale_l

    target_H_r = 1750.0
    scale_r = target_H_r / float(H_r)
    disp_W_r = W_r * scale_r
    disp_H_r = target_H_r

    gap = 230.0
    margin_left = 80.0
    margin_right = 80.0
    margin_top = 80.0
    margin_bottom = 80.0

    canvas_H = margin_top + target_H_l + margin_bottom
    canvas_W = margin_left + disp_W_l + gap + disp_W_r + margin_right

    fig = plt.figure(figsize=(canvas_W / 300.0, canvas_H / 300.0), dpi=300)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, canvas_W)
    ax.set_ylim(canvas_H, 0)
    ax.axis('off')

    # 1. 放置左侧宏观圆柱
    x_l0 = margin_left
    y_l0 = margin_top
    ax.imshow(im_left, extent=[x_l0, x_l0 + disp_W_l, y_l0 + target_H_l, y_l0], zorder=10)

    # 2. 左侧局部取景框 (严格包裹红色物料环 x=753，并与内母线保持净空)
    box_w_raw = 160.0
    box_h_raw = 160.0
    src_x2_raw = box_x2
    src_x1_raw = src_x2_raw - box_w_raw
    src_y1_raw = 1324.0
    src_y2_raw = src_y1_raw + box_h_raw

    src_x1 = x_l0 + src_x1_raw * scale_l
    src_x2 = x_l0 + src_x2_raw * scale_l
    src_y1 = y_l0 + src_y1_raw * scale_l
    src_y2 = y_l0 + src_y2_raw * scale_l
    src_w = src_x2 - src_x1
    src_h = src_y2 - src_y1
    src_cy = (src_y1 + src_y2) / 2.0

    ax.add_patch(Rectangle(
        (src_x1, src_y1), src_w, src_h,
        fill=False, edgecolor='#000000',
        linestyle='-', linewidth=2.2, zorder=15
    ))

    # 3. 右侧卡片区域布局
    x_r0 = margin_left + disp_W_l + gap
    card_pad = 28.0
    y_r0 = src_cy - disp_H_r / 2.0

    card_x = x_r0 - card_pad
    card_y = y_r0 - card_pad
    card_w = disp_W_r + 2 * card_pad
    card_h = disp_H_r + 2 * card_pad

    # 4. 放大引导虚线
    line_top_src = (src_x2, src_y1)
    line_top_tgt = (card_x, card_y)
    line_bot_src = (src_x2, src_y2)
    line_bot_tgt = (card_x, card_y + card_h)

    ax.plot([line_top_src[0], line_top_tgt[0]],
            [line_top_src[1], line_top_tgt[1]],
            color='#000000', linestyle=(0, (6, 5)), linewidth=1.8, zorder=12)

    ax.plot([line_bot_src[0], line_bot_tgt[0]],
            [line_bot_src[1], line_bot_tgt[1]],
            color='#000000', linestyle=(0, (6, 5)), linewidth=1.8, zorder=12)

    # 5. 右侧卡片背景与黑色锐利边框
    ax.add_patch(Rectangle(
        (card_x, card_y), card_w, card_h,
        facecolor='#ffffff', edgecolor='#000000',
        linewidth=2.4, zorder=14
    ))

    # 6. 放置右侧微观图件
    ax.imshow(im_right, extent=[x_r0, x_r0 + disp_W_r, y_r0 + disp_H_r, y_r0], zorder=16)

    plt.savefig(output_path, dpi=300, facecolor='white', edgecolor='none')
    plt.close()
    print(f"[OK] 成功生成高清定稿图件: {output_path}")

def main():
    cur_dir, eda_dir, archive_img_dir, output_png = get_paths()
    
    # 1. 获取宏观左图 (Style C)
    left_img = find_or_generate_macro_cylinder(eda_dir, archive_img_dir)

    # 2. 获取右侧微观图件 (优先复用 Archive/images/ 中的定稿子图，若缺失则动态从 raw 3D 线稿生成)
    micro_img_path = os.path.join(archive_img_dir, 'task3_2_2_arrow_collinear_clean.png')
    if not os.path.exists(micro_img_path):
        raw_candidates = [
            os.path.join(archive_img_dir, 'task3_2_3_raw.png'),
            os.path.join(cur_dir, 'task3_2_3_raw.png'),
            r"C:\Users\kqdx\.gemini\antigravity\brain\ce5f745e-eae3-4eca-9e3f-87c5c965cace\scratch\task3_2_3_raw.png"
        ]
        raw_png = None
        for p in raw_candidates:
            if os.path.exists(p):
                raw_png = p
                break
        if raw_png is None:
            raise FileNotFoundError("未找到右侧 3D 线稿 task3_2_3_raw.png。")
        generate_right_micro_subfigure(raw_png, micro_img_path)

    # 3. 执行最终合成
    composite_moving_boundary_figure(left_img, micro_img_path, output_png, box_x2=764.0)

if __name__ == '__main__':
    main()
