# -*- coding: utf-8 -*-
"""
Plot Figure: Moving Boundary Shrinkage Mechanism & Landau Coordinate Transformation FVM Diagram
(for CUMCM 2026 Problem A - Question 4)
Style closely mimics eda_figures/fvm_multiscale_macro_micro.png:
- Left: Time-varying physical domain Omega(t) with contracting cylinder and moving boundary vectors
- Center: Landau coordinate transformation mapping and projection rays
- Right (Sharp black rectangular card): Stationary computational domain Xi, FVM metric scaling, and conservative ODE
"""

from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Polygon, FancyArrowPatch
import matplotlib.patheffects as pe

# TeX Computer Modern font settings & Chinese fonts
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'DejaVu Sans']
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['mathtext.fontset'] = 'cm'

SCRIPT_DIR = Path(__file__).resolve().parent
OUT_DIR_LOCAL = SCRIPT_DIR.parent
OUT_DIR_ARTIFACT = Path(r'C:\Users\kqdx\.gemini\antigravity\brain\ce5f745e-eae3-4eca-9e3f-87c5c965cace')

OUT_DIR_LOCAL.mkdir(parents=True, exist_ok=True)
OUT_DIR_ARTIFACT.mkdir(parents=True, exist_ok=True)


def draw_cylinder_3d(ax, xc, y_bot, H, R, eps=0.20,
                     color_edge='#0F172A', color_fill='#F8FAFC',
                     lw=2.0, is_dashed=False, show_mesh=False,
                     num_radial=5, num_layers=6, alpha=1.0, zorder=10):
    """
    Draw an isometric vertical cylinder with elliptical top and bottom faces.
    """
    y_top = y_bot + H
    th_full = np.linspace(0, 2 * np.pi, 200)
    th_front = np.linspace(np.pi, 2 * np.pi, 100)
    th_back = np.linspace(0, np.pi, 100)

    # Shaded body (side surface)
    poly_pts = []
    poly_pts.append((xc - R, y_bot))
    for th in np.linspace(np.pi, 2 * np.pi, 50):
        poly_pts.append((xc + R * np.cos(th), y_bot + eps * R * np.sin(th)))
    poly_pts.append((xc + R, y_top))
    for th in np.linspace(2 * np.pi, np.pi, 50):
        poly_pts.append((xc + R * np.cos(th), y_top + eps * R * np.sin(th)))
    
    if not is_dashed:
        ax.add_patch(Polygon(poly_pts, closed=True, facecolor=color_fill, edgecolor='none', alpha=alpha, zorder=zorder))
        top_pts = [(xc + R * np.cos(th), y_top + eps * R * np.sin(th)) for th in th_full]
        ax.add_patch(Polygon(top_pts, closed=True, facecolor='#EDF2F7', edgecolor='none', alpha=alpha, zorder=zorder+1))

    if show_mesh and not is_dashed:
        s_vals = np.linspace(0, 1, num_radial + 1)[1:-1]
        r_grids = R * (1 - (1 - s_vals)**2)
        for rg in r_grids:
            ax.plot(xc + rg * np.cos(th_full), y_top + eps * rg * np.sin(th_full),
                    color='#94A3B8', lw=1.0, ls='-', zorder=zorder+2)
        
        q_vals = np.linspace(0, 1, num_layers + 1)[1:-1]
        z_grids = y_bot + H * (1 - (1 - q_vals)**2)
        for zg in z_grids:
            ax.plot(xc + R * np.cos(th_front), zg + eps * R * np.sin(th_front),
                    color='#94A3B8', lw=0.9, ls='-', zorder=zorder+2)
            ax.plot(xc + R * np.cos(th_back), zg + eps * R * np.sin(th_back),
                    color='#CBD5E1', lw=0.7, ls=(0, (4, 4)), zorder=zorder+2)
        
        for th_m in [7*np.pi/6, 4*np.pi/3, 3*np.pi/2, 5*np.pi/3, 11*np.pi/6]:
            xm = xc + R * np.cos(th_m)
            ym_bot = y_bot + eps * R * np.sin(th_m)
            ym_top = y_top + eps * R * np.sin(th_m)
            ax.plot([xm, xm], [ym_bot, ym_top], color='#94A3B8', lw=0.8, ls='-', zorder=zorder+2)

    ls = (0, (6, 5)) if is_dashed else '-'
    ax.plot([xc - R, xc - R], [y_bot, y_top], color=color_edge, lw=lw, ls=ls, zorder=zorder+3)
    ax.plot([xc + R, xc + R], [y_bot, y_top], color=color_edge, lw=lw, ls=ls, zorder=zorder+3)
    
    ax.plot(xc + R * np.cos(th_full), y_top + eps * R * np.sin(th_full),
            color=color_edge, lw=lw, ls=ls, zorder=zorder+3)
    
    ax.plot(xc + R * np.cos(th_front), y_bot + eps * R * np.sin(th_front),
            color=color_edge, lw=lw, ls=ls, zorder=zorder+3)
    ax.plot(xc + R * np.cos(th_back), y_bot + eps * R * np.sin(th_back),
            color=color_edge if is_dashed else '#CBD5E1',
            lw=lw if is_dashed else 1.2,
            ls=(0, (6, 5)), zorder=zorder+3)


def main():
    print('>>> 正在绘制 Task 3.0: 问题四动边界收缩机制与 Landau 移动网格变换机理全幅图 (精准排版版)...')
    
    fig = plt.figure(figsize=(19.0, 11.2), dpi=300)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')
    
    ax.add_patch(Rectangle((0, 0), 100, 100, facecolor='#FFFFFF', edgecolor='none', zorder=0))

    # =========================================================================
    # 1. 左侧面板：时变物理域 Omega(t) 动边界收缩与物理网格压缩
    # =========================================================================
    xc_left = 17.5
    y_bot_l = 19.0
    H_l = 56.0
    R0 = 10.8
    Rt = 6.48  # s(t) = 0.60
    eps = 0.20

    # (1) 初始时刻 t=0 红色虚线外轮廓
    draw_cylinder_3d(ax, xc_left, y_bot_l, H_l, R0, eps=eps,
                     color_edge='#C0392B', color_fill='none',
                     lw=2.0, is_dashed=True, zorder=5)

    # (2) 收缩脱水区填充 (粉红色半透明带)
    th_ring = np.linspace(0, 2*np.pi, 150)
    poly_ring = []
    for th in th_ring:
        poly_ring.append((xc_left + R0 * np.cos(th), (y_bot_l + H_l) + eps * R0 * np.sin(th)))
    for th in th_ring[::-1]:
        poly_ring.append((xc_left + Rt * np.cos(th), (y_bot_l + H_l) + eps * Rt * np.sin(th)))
    ax.add_patch(Polygon(poly_ring, closed=True, facecolor='#FEE2E2', alpha=0.55, edgecolor='none', zorder=6))

    side_strip_r = [
        (xc_left + Rt, y_bot_l),
        (xc_left + R0, y_bot_l),
        (xc_left + R0, y_bot_l + H_l),
        (xc_left + Rt, y_bot_l + H_l)
    ]
    ax.add_patch(Polygon(side_strip_r, closed=True, facecolor='#FEE2E2', alpha=0.40, edgecolor='none', zorder=6))

    side_strip_l = [
        (xc_left - R0, y_bot_l),
        (xc_left - Rt, y_bot_l),
        (xc_left - Rt, y_bot_l + H_l),
        (xc_left - R0, y_bot_l + H_l)
    ]
    ax.add_patch(Polygon(side_strip_l, closed=True, facecolor='#FEE2E2', alpha=0.40, edgecolor='none', zorder=6))

    # (3) 当前时刻 t>0 实质收缩圆柱与压缩网格
    draw_cylinder_3d(ax, xc_left, y_bot_l, H_l, Rt, eps=eps,
                     color_edge='#0F172A', color_fill='#F8FAFC',
                     lw=2.2, is_dashed=False, show_mesh=True,
                     num_radial=5, num_layers=6, zorder=8)

    # (4) 坐标轴
    ax.plot([xc_left, xc_left], [y_bot_l - 5.0, y_bot_l + H_l + 8.5],
            color='#0F172A', lw=2.2, zorder=20)
    arrow_z = FancyArrowPatch((xc_left, y_bot_l + H_l + 5.5), (xc_left, y_bot_l + H_l + 9.5),
                              arrowstyle='-|>,head_length=8,head_width=5',
                              color='#0F172A', lw=2.2, zorder=21)
    ax.add_patch(arrow_z)
    ax.text(xc_left, y_bot_l + H_l + 10.8, r'$z$',
            fontsize=18, fontweight='bold', ha='center', va='bottom', color='#0F172A', zorder=25)

    ax.plot([xc_left, xc_left + R0 + 5.5], [y_bot_l, y_bot_l],
            color='#0F172A', lw=2.0, zorder=20)
    arrow_r = FancyArrowPatch((xc_left + R0 + 3.0, y_bot_l), (xc_left + R0 + 6.0, y_bot_l),
                              arrowstyle='-|>,head_length=8,head_width=5',
                              color='#0F172A', lw=2.0, zorder=21)
    ax.add_patch(arrow_r)
    ax.text(xc_left + R0 + 7.2, y_bot_l, r'$r$',
            fontsize=18, fontweight='bold', ha='left', va='center', color='#0F172A', zorder=25)

    ax.plot(xc_left, y_bot_l, 'o', color='#C0392B', markersize=5.5, zorder=25)
    ax.text(xc_left - 1.2, y_bot_l - 1.8, r'$\mathrm{O}$',
            fontsize=15, fontweight='bold', ha='right', va='top', color='#0F172A', zorder=25)

    # (5) 顶面尺寸标注线 (R0 与 R(t))
    y_dim_top = y_bot_l + H_l + 4.5
    ax.plot([xc_left, xc_left + R0], [y_dim_top, y_dim_top], color='#C0392B', lw=1.5, ls='-', zorder=25)
    ax.plot([xc_left, xc_left], [y_dim_top - 1.2, y_dim_top + 1.2], color='#C0392B', lw=1.5, zorder=25)
    ax.plot([xc_left + R0, xc_left + R0], [y_dim_top - 1.2, y_dim_top + 1.2], color='#C0392B', lw=1.5, zorder=25)
    ax.text(xc_left + R0 / 2.0, y_dim_top + 1.0, r'$R_0 = 2.00\ \mathrm{cm}\ (t=0)$',
            fontsize=12, fontweight='bold', color='#C0392B', ha='center', va='bottom', zorder=25)

    y_dim_bot = y_bot_l - 3.8
    ax.plot([xc_left, xc_left + Rt], [y_dim_bot, y_dim_bot], color='#0F172A', lw=1.5, ls='-', zorder=25)
    ax.plot([xc_left, xc_left], [y_dim_bot - 1.0, y_dim_bot + 1.0], color='#0F172A', lw=1.5, zorder=25)
    ax.plot([xc_left + Rt, xc_left + Rt], [y_dim_bot - 1.0, y_dim_bot + 1.0], color='#0F172A', lw=1.5, zorder=25)
    ax.text(xc_left + Rt / 2.0, y_dim_bot - 1.2, r'$R(t) = 1.198\ \mathrm{cm}\ (t=72\ \mathrm{h})$',
            fontsize=11.5, fontweight='bold', color='#0F172A', ha='center', va='top', zorder=25)

    # (6) 动边界向内收缩速度矢量 (标注在左侧与收缩带内，确保右侧透射光线完全无遮挡)
    # 左侧向内收缩箭头 (由 -R0 指向 -Rt，即向右收缩)
    y_arrows_l = [y_bot_l + 18.0, y_bot_l + 34.0, y_bot_l + 50.0]
    for ya in y_arrows_l:
        arr_in_l = FancyArrowPatch((xc_left - R0 + 0.2, ya), (xc_left - Rt - 0.3, ya),
                                   arrowstyle='-|>,head_length=6,head_width=4',
                                   color='#C0392B', lw=2.2, zorder=25)
        ax.add_patch(arr_in_l)

    # 收缩速度文字放置在左侧外部开阔无干扰区域
    ax.plot([xc_left - (R0 + Rt)/2.0, xc_left - R0 - 1.8],
            [y_bot_l + 34.0, y_bot_l + 38.0], color='#C0392B', lw=1.2, zorder=25)
    ax.text(xc_left - R0 - 2.4, y_bot_l + 39.5,
            r'$\mathbf{v}_{\mathrm{b}} = \frac{\mathrm{d}R}{\mathrm{d}t} < 0$',
            fontsize=13, fontweight='bold', color='#C0392B', ha='right', va='center', zorder=25)
    ax.text(xc_left - R0 - 2.4, y_bot_l + 36.0,
            '(动边界径向向内收缩)',
            fontsize=10.0, color='#C0392B', ha='right', va='center', zorder=25)

    # (7) 取景局部框 (在右侧收缩外边界处高亮控制体切片，位于垂直正中央)
    box_w = 4.2
    box_h = 7.5
    box_x = xc_left + Rt - 1.8
    box_y = y_bot_l + 28.0 - box_h / 2.0
    
    ax.add_patch(Rectangle((box_x + 0.4, box_y + 0.4), box_w - 0.8, box_h - 0.8,
                           facecolor='#FEE2E2', edgecolor='#C0392B', lw=2.2, zorder=26))
    ax.add_patch(Rectangle((box_x, box_y), box_w, box_h,
                           facecolor='none', edgecolor='#0F172A', lw=2.4, zorder=30))

    # (8) 左侧标题与难点说明
    ax.text(xc_left, 95.0, r'(a) 时变物理域 $\Omega(t)$ 与动边界收缩',
            fontsize=16, fontweight='bold', color='#0F172A', ha='center', va='top', zorder=25)
    ax.text(xc_left, 91.5, r'$\Omega(t) = \{ (r, z) \mid 0 \leq r \leq R(t),\ 0 \leq z \leq \frac{L}{2} \}$',
            fontsize=13, color='#334155', ha='center', va='top', zorder=25)
    
    badge_w, badge_h = 28.0, 6.8
    badge_x = xc_left - badge_w / 2.0
    badge_y = 5.0
    ax.add_patch(Rectangle((badge_x, badge_y), badge_w, badge_h,
                           facecolor='#F8FAFC', edgecolor='#CBD5E1', lw=1.2, zorder=5))
    ax.text(xc_left, badge_y + badge_h - 1.4,
            '动边界计算难点 (Moving Boundary Challenge)',
            fontsize=11.5, fontweight='bold', color='#C0392B', ha='center', va='top', zorder=25)
    ax.text(xc_left, badge_y + 1.4,
            '边界 $r=R(t)$ 连续收缩 · 欧拉网格面临严重界面截断与插值耗散',
            fontsize=9.8, color='#475569', ha='center', va='bottom', zorder=25)

    # =========================================================================
    # 2. 中间枢纽：Landau 归一化映射与透射虚线 (Volcano-style Dashed Rays)
    # =========================================================================
    card_x = 45.0
    card_y = 5.0
    card_w = 52.5
    card_h = 89.5

    # 双虚线透射连接线 (连到右侧大卡片的上下拐角)
    line_top_src = (box_x + box_w, box_y + box_h)
    line_top_tgt = (card_x, card_y + card_h)

    line_bot_src = (box_x + box_w, box_y)
    line_bot_tgt = (card_x, card_y)

    ax.plot([line_top_src[0], line_top_tgt[0]], [line_top_src[1], line_top_tgt[1]],
            color='#0F172A', linestyle=(0, (6, 5)), lw=1.8, zorder=15)
    ax.plot([line_bot_src[0], line_bot_tgt[0]], [line_bot_src[1], line_bot_tgt[1]],
            color='#0F172A', linestyle=(0, (6, 5)), lw=1.8, zorder=15)

    # 中间数学映射说明卡片 (纯白底，sharp black border)
    map_cx = (box_x + box_w + card_x) / 2.0
    map_cy = 47.0
    map_bw = 14.0
    map_bh = 19.0
    ax.add_patch(Rectangle((map_cx - map_bw/2.0, map_cy - map_bh/2.0), map_bw, map_bh,
                           facecolor='#FFFFFF', edgecolor='#0F172A', lw=2.0, zorder=35))

    ax.text(map_cx, map_cy + map_bh/2.0 - 1.6, 'Landau 坐标归一化',
            fontsize=12.5, fontweight='bold', color='#0F172A', ha='center', va='top', zorder=40)
    ax.text(map_cx, map_cy + map_bh/2.0 - 4.8, r'$\xi = \frac{r}{R(t)} \in [0, 1]$',
            fontsize=14.0, fontweight='bold', color='#C0392B', ha='center', va='top', zorder=40)
    ax.text(map_cx, map_cy + map_bh/2.0 - 8.6, r'$s(t) = \frac{R(t)}{R_0}$',
            fontsize=12.0, color='#0F172A', ha='center', va='top', zorder=40)

    ax.plot([map_cx - map_bw/2.0 + 1.2, map_cx + map_bw/2.0 - 1.2],
            [map_cy - 0.8, map_cy - 0.8], color='#E2E8F0', lw=1.0, zorder=36)

    ax.text(map_cx, map_cy - 2.5, r'$r=0 \Longleftrightarrow \xi = 0$',
            fontsize=11.0, color='#334155', ha='center', va='top', zorder=40)
    ax.text(map_cx, map_cy - 5.0, r'$r=R(t) \Longleftrightarrow \xi \equiv 1$',
            fontsize=11.5, fontweight='bold', color='#C0392B', ha='center', va='top', zorder=40)
    ax.text(map_cx, map_cy - 7.5, '(动边界固化为静止边界)',
            fontsize=9.2, color='#64748B', ha='center', va='top', zorder=40)

    # =========================================================================
    # 3. 右侧面板：固化计算参考域 Xi 与有限体积动态度规缩放 (大卡片)
    # =========================================================================
    ax.add_patch(Rectangle((card_x, card_y), card_w, card_h,
                           facecolor='#FFFFFF', edgecolor='#0F172A', lw=2.5, zorder=40))

    # (1) 卡片总标题
    ax.text(card_x + card_w / 2.0, card_y + card_h - 2.8,
            r'(b) 固化计算参考域 $\Xi$ 与有限体积动态度规缩放法则',
            fontsize=16, fontweight='bold', color='#0F172A', ha='center', va='top', zorder=45)
    ax.text(card_x + card_w / 2.0, card_y + card_h - 6.2,
            r'$\Xi = \{(\xi, z) \mid 0 \leq \xi \leq 1,\ 0 \leq z \leq \frac{L}{2}\} \quad$ [计算网格完全静止，时间导数 $\dot{\xi}_i \equiv 0$]',
            fontsize=12.5, color='#334155', ha='center', va='top', zorder=45)

    # (2) 3D 控制体微观几何展示与四大几何度规缩放
    cv_x0 = card_x + 22.0
    cv_y0 = card_y + 42.0
    
    w_cv = 9.0
    h_cv = 18.0
    d_cv = 7.5
    
    # 控制体正面 (Outer Lateral Surface: at xi = 1)
    cv_front = [
        (cv_x0 + d_cv, cv_y0),
        (cv_x0 + d_cv + w_cv, cv_y0 + 2.5),
        (cv_x0 + d_cv + w_cv, cv_y0 + 2.5 + h_cv),
        (cv_x0 + d_cv, cv_y0 + h_cv)
    ]
    ax.add_patch(Polygon(cv_front, closed=True, facecolor='#FFFFFF', edgecolor='#0F172A', lw=2.6, zorder=52))
    
    # 控制体顶面 (Top Axial Face: A_z)
    cv_top = [
        (cv_x0, cv_y0 + h_cv + 3.8),
        (cv_x0 + w_cv * 0.85, cv_y0 + h_cv + 5.8),
        (cv_x0 + d_cv + w_cv, cv_y0 + 2.5 + h_cv),
        (cv_x0 + d_cv, cv_y0 + h_cv)
    ]
    ax.add_patch(Polygon(cv_top, closed=True, facecolor='#F1F5F9', edgecolor='#0F172A', lw=2.2, zorder=51))

    # 控制体左内侧面 (Radial Face: A_r)
    cv_left = [
        (cv_x0, cv_y0 + 3.8),
        (cv_x0 + d_cv, cv_y0),
        (cv_x0 + d_cv, cv_y0 + h_cv),
        (cv_x0, cv_y0 + h_cv + 3.8)
    ]
    ax.add_patch(Polygon(cv_left, closed=True, facecolor='#E2E8F0', edgecolor='#0F172A', lw=2.2, zorder=51))

    # 外表面蒸发水分通量红箭头 J_evap
    arrow_flux = FancyArrowPatch((cv_x0 + d_cv + w_cv, cv_y0 + h_cv/2.0 + 1.2),
                                 (cv_x0 + d_cv + w_cv + 5.2, cv_y0 + h_cv/2.0 + 1.2),
                                 arrowstyle='-|>,head_length=8,head_width=5.0',
                                 color='#C0392B', lw=2.5, zorder=60)
    ax.add_patch(arrow_flux)
    ax.text(cv_x0 + d_cv + w_cv + 5.8, cv_y0 + h_cv/2.0 + 1.2,
            r'$J_{\mathrm{evap}} = h_m (C_s - C_\infty)$',
            fontsize=12.0, fontweight='bold', color='#C0392B', ha='left', va='center', zorder=60)

    # 边界 xi = 1 竖向参考粗线与标注
    ax.plot([cv_x0 + d_cv + w_cv, cv_x0 + d_cv + w_cv],
            [cv_y0 + 2.5, cv_y0 + 2.5 + h_cv], color='#0F172A', lw=3.2, zorder=53)
    ax.text(cv_x0 + d_cv + w_cv + 0.8, cv_y0 + 2.5 + h_cv + 1.8,
            r'$\xi \equiv 1$ (固定静止外边界)',
            fontsize=11.5, fontweight='bold', color='#0F172A', ha='left', va='bottom', zorder=55)

    # 4大度规缩放核心标注 (精心布局于四个方向，绝对无重叠碰撞)
    
    # [1] 侧外表面积 (右下方，完全在卡片内)
    ax.plot([cv_x0 + d_cv + w_cv*0.75, cv_x0 + d_cv + w_cv*0.75 + 4.2],
            [cv_y0 + 3.0, cv_y0 - 3.2], color='#C0392B', lw=1.3, zorder=55)
    ax.text(cv_x0 + d_cv + w_cv*0.75 + 4.8, cv_y0 - 3.2,
            r'$\mathbf{\Delta S_{\mathrm{side}}(t) = s(t) \cdot \Delta S_{\mathrm{side}}^0}$' + '\n' +
            r'($\xi \equiv 1$ 传质接触面积随 $s$ 线性收缩)' + '\n' +
            r'【代码: $\mathrm{surface} \propto s(t)$】',
            fontsize=10.5, fontweight='bold', color='#C0392B', ha='left', va='center', zorder=55)

    # [2] 控制体体积缩放 (正上方偏左，与 xi=1 错开)
    ax.plot([cv_x0 + d_cv*0.55, cv_x0 + d_cv*0.55],
            [cv_y0 + h_cv + 2.0, cv_y0 + h_cv + 8.5], color='#0F172A', lw=1.3, zorder=55)
    ax.text(cv_x0 + d_cv*0.55, cv_y0 + h_cv + 9.2,
            r'$\mathbf{\Delta V_{i,j}(t) = s(t)^2 \cdot \Delta V_{i,j}^0}$' + '\n' +
            r'(微元截面随 $s^2$ 收缩，轴向长度不变)' + '\n' +
            r'【代码: $V \propto s(t)^2$】',
            fontsize=10.5, fontweight='bold', color='#0F172A', ha='center', va='bottom', zorder=55)

    # [3] 径向热质传导度 (严格几何不变性！位于左侧偏下，完全在卡片内)
    ax.plot([cv_x0 + d_cv*0.4, cv_x0 - 2.5],
            [cv_y0 + h_cv*0.42, cv_y0 + h_cv*0.42], color='#C0392B', lw=1.3, zorder=55)
    ax.text(cv_x0 - 3.0, cv_y0 + h_cv*0.42,
            r'$\mathbf{G_{r}(t) = \frac{A_r}{\Delta r} = \frac{2\pi (s \bar{r}_0) \Delta z}{s \Delta r_0} \equiv G_{r}^0}$' + '\n' +
            '【几何精确相消 · 径向传导度时间无关】',
            fontsize=10.5, fontweight='bold', color='#C0392B', ha='right', va='center', zorder=55)

    # [4] 轴向热质传导度 (位于左侧偏上，完全在卡片内)
    ax.plot([cv_x0 + w_cv*0.25, cv_x0 - 2.5],
            [cv_y0 + h_cv + 3.0, cv_y0 + h_cv + 6.8], color='#0F172A', lw=1.3, zorder=55)
    ax.text(cv_x0 - 3.0, cv_y0 + h_cv + 6.8,
            r'$\mathbf{G_{z}(t) = \frac{A_z}{\Delta z} = s(t)^2 \cdot G_{z}^0}$' + '\n' +
            r'(轴向传导通量随截面积 $s^2$ 收缩)' + '\n' +
            r'【代码: $G_z \propto s(t)^2$】',
            fontsize=10.5, fontweight='bold', color='#0F172A', ha='right', va='center', zorder=55)

    # (3) 卡片底部：严格保守型 FVM 离散方程与三大科学机理优势
    box_eq_x = card_x + 2.5
    box_eq_y = card_y + 2.2
    box_eq_w = card_w - 5.0
    box_eq_h = 24.5

    ax.add_patch(Rectangle((box_eq_x, box_eq_y), box_eq_w, box_eq_h,
                           facecolor='#F8FAFC', edgecolor='#CBD5E1', lw=1.5, zorder=45))

    ax.text(box_eq_x + box_eq_w / 2.0, box_eq_y + box_eq_h - 1.6,
            '底层有限体积法半离散保守型常微分方程组 (Conservative FVM System)',
            fontsize=13.0, fontweight='bold', color='#0F172A', ha='center', va='top', zorder=46)

    ode_str = r'$\frac{\mathrm{d}C_p}{\mathrm{d}t} = \frac{1}{s(t)^2 V_{p,0}} \left[ \sum_{q \in N_r(p)} G_{r}^0 D_{pq}(C_q - C_p) + s(t)^2 \sum_{q \in N_z(p)} G_{z}^0 D_{pq}(C_q - C_p) + s(t) h_m S_{p,\mathrm{side}}^0 (C_\infty - C_p) \right]$'
    ax.text(box_eq_x + box_eq_w / 2.0, box_eq_y + box_eq_h - 5.8,
            ode_str, fontsize=13.0, color='#0F172A', ha='center', va='top', zorder=46)

    # 三大优势独立卡片 (3 个并排浅色子框，杜绝文字挤叠)
    tag_w = (box_eq_w - 4.0) / 3.0
    tag_h = 9.8
    tag_y = box_eq_y + 1.8
    
    adv_data = [
        ('网格完全静止', r'$\dot{\xi}_i \equiv 0$', '消除了 ALE 动网格对流漂移项\n彻底杜绝数值伪扩散与高阶波动'),
        ('零场重构误差', r'\text{No Remeshing}', '避免动边界每步重新剖分网格\n消除投影插值带来的虚假耗散'),
        ('瞬时严格守恒', r'\text{Exact Conservation}', '有限体积空间代数积分完全封闭\n质量与能量全时程机器精度守恒')
    ]

    for idx, (t1, t2, desc) in enumerate(adv_data):
        tx = box_eq_x + 1.0 + idx * (tag_w + 1.0)
        ax.add_patch(Rectangle((tx, tag_y), tag_w, tag_h,
                               facecolor='#FFFFFF', edgecolor='#E2E8F0', lw=1.0, zorder=46))
        ax.text(tx + tag_w/2.0, tag_y + tag_h - 1.2, f'({idx+1}) ' + t1,
                fontsize=11.0, fontweight='bold', color='#C0392B' if idx==2 else '#0F172A',
                ha='center', va='top', zorder=47)
        ax.text(tx + tag_w/2.0, tag_y + tag_h - 4.2, desc,
                fontsize=9.2, color='#475569', ha='center', va='top', zorder=47)

    # -------------------------------------------------------------------------
    # 保存生成图件
    # -------------------------------------------------------------------------
    out_png_local = OUT_DIR_LOCAL / 'moving_boundary_landau_fvm.png'
    out_png_artifact = OUT_DIR_ARTIFACT / 'moving_boundary_landau_fvm.png'

    fig.savefig(str(out_png_local), dpi=300, bbox_inches='tight')
    if out_png_artifact.parent.exists():
        fig.savefig(str(out_png_artifact), dpi=300, bbox_inches='tight')
    plt.close(fig)

    print(f'[√] 成功生成高清图件: {out_png_local}')


if __name__ == '__main__':
    main()
