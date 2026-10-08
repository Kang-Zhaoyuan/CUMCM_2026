# -*- coding: utf-8 -*-
"""
药材半径与相对体积收缩演化及横截面几何形变图（Fig.5 与 Fig.6 整合定稿版）
- 依据 Task 2.2 核心物理机理要求：
  1. 保留具有直接 FVM 控制体网格更新物理本质的“相对体积 V/V0”
  2. 删去全图大标题，由论文 Caption 承载，界面更紧凑
  3. 删去 (b) 图中一切冗余的“ (R = ... cm)”，仅保留纯粹的时间标记
  4. (a) 图图例彻底精简为单一一项 $R$ 与 $V/V_0$，信息零损失
  5. 精细微调双轴比例尺（左右各 7 档对齐），终态高度错开 > 20%，伴随平行绝不重合
"""

import os
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.interpolate import pchip_interpolate
from matplotlib.lines import Line2D

# 全局绘图风格与 STIX 数学公式字体配置
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'SimSun', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['mathtext.fontset'] = 'stix'
plt.rcParams['mathtext.rm'] = 'STIXGeneral'
plt.rcParams['mathtext.it'] = 'STIXGeneral:italic'
plt.rcParams['mathtext.bf'] = 'STIXGeneral:bold'

plt.rcParams['xtick.direction'] = 'in'
plt.rcParams['ytick.direction'] = 'in'
plt.rcParams['xtick.major.size'] = 4.5
plt.rcParams['ytick.major.size'] = 4.5
plt.rcParams['lines.linewidth'] = 2.0

SCRIPT_DIR = Path(__file__).resolve().parent
OUT_DIR_LOCAL = SCRIPT_DIR.parent
PROJECT_ROOT = OUT_DIR_LOCAL.parent
ATTACHMENT_DIR = PROJECT_ROOT / 'CUMCM2026Problems' / 'A题' / '附件'
OUT_DIR_ARTIFACT = Path(r'C:\Users\kqdx\.gemini\antigravity\brain\ce5f745e-eae3-4eca-9e3f-87c5c965cace')

OUT_DIR_LOCAL.mkdir(parents=True, exist_ok=True)
OUT_DIR_ARTIFACT.mkdir(parents=True, exist_ok=True)

def save_current_figure(fig, filename):
    p1 = OUT_DIR_LOCAL / filename
    p2 = OUT_DIR_ARTIFACT / filename
    fig.savefig(str(p1), dpi=300, bbox_inches='tight')
    if p2.parent.exists():
        fig.savefig(str(p2), dpi=300, bbox_inches='tight')
    plt.close(fig)
    print(f'[√] 已保存高分辨率图件: {p1}')


PATH_ATTACHMENT2 = ATTACHMENT_DIR / '附件2.xlsx'

def main():
    print('>>> 正在绘制 整合版图5：药材半径与相对体积的变化及横截面收缩 (Task 2 定稿版)...')
    df2 = pd.read_excel(PATH_ATTACHMENT2)

    t_raw = df2['时间'].values              # 秒 (0 ~ 259200 s, 72 h)
    r_raw = df2['半径'].values              # cm (2.000 ~ 1.198 cm)
    t_h_raw = t_raw / 3600.0               # 小时

    # 相对体积留存率 V(t)/V_0 (%) = (R(t)/R_0)^2 * 100
    v_raw = (r_raw / 2.000)**2 * 100.0

    # 连续高密度时间网格与 PCHIP 保形单调插值
    t_dense = np.linspace(0, 259200, 2593)
    t_h_dense = t_dense / 3600.0
    r_pchip = pchip_interpolate(t_raw, r_raw, t_dense)
    v_pchip = (r_pchip / 2.000)**2 * 100.0

    color_red = '#C0392B'    # 主色1：学术深红（半径专属）
    color_black = '#0F172A'  # 主色2：深石板黑（相对体积与几何框架专属）
    color_grid = '#E2E8F0'   # 辅助色：极淡灰（仅用于网格）

    # 1 x 2 经典学术横向双子图 (不再添加 suptitle)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12.5, 5.0), gridspec_kw={'wspace': 0.30})

    # ==================== (a) 半径与相对体积演化曲线 (解耦双轴) ====================
    # 左轴：药材半径 R (cm)，运行在偏下方区间
    ax1.set_xlabel(r'时间 $t\ (\mathrm{h})$', fontsize=11.5, fontweight='bold', color=color_black)
    ax1.set_ylabel(r'半径 $R\ (\mathrm{cm})$', color=color_black, fontsize=11.5, fontweight='bold')

    step = 4  # 散点步长采样
    s1 = ax1.scatter(t_h_raw[::step], r_raw[::step], color=color_red, s=20, marker='o',
                     facecolors='none', edgecolors=color_red, linewidths=1.2, zorder=5)
    l1 = ax1.plot(t_h_dense, r_pchip, color=color_red, lw=2.0, linestyle='-', zorder=4)

    ax1.tick_params(axis='x', labelcolor=color_black, labelsize=10.5)
    ax1.tick_params(axis='y', labelcolor=color_black, labelsize=10.5)
    ax1.set_xlim(-1.5, 73.5)
    ax1.set_ylim(1.10, 2.30)
    ax1.set_yticks(np.linspace(1.10, 2.30, 7))
    ax1.grid(True, linestyle=':', color=color_grid, alpha=0.9, lw=1.0)

    # 右轴：相对体积留存率 V/V_0 (%)，运行在偏上方区间
    ax1_r = ax1.twinx()
    ax1_r.set_ylabel(r'相对体积 $V/V_0\ (\%)$', color=color_black, fontsize=11.5, fontweight='bold')

    s2 = ax1_r.scatter(t_h_raw[::step], v_raw[::step], color=color_black, s=18, marker='s',
                       facecolors='none', edgecolors=color_black, linewidths=1.2, zorder=5)
    l2 = ax1_r.plot(t_h_dense, v_pchip, color=color_black, lw=1.8, linestyle='-', zorder=4)

    ax1_r.tick_params(axis='y', labelcolor=color_black, labelsize=10.5)
    ax1_r.set_ylim(0.0, 120.0)
    ax1_r.set_yticks(np.linspace(0.0, 120.0, 7))

    # 合并图例：彻底精简，单行仅标物理量符号，信息零损失
    h_R = Line2D([0], [0], color=color_red, lw=2.0, marker='o', markerfacecolor='none',
                 markeredgecolor=color_red, markeredgewidth=1.2, markersize=5, label=r'$R$')
    h_V = Line2D([0], [0], color=color_black, lw=1.8, marker='s', markerfacecolor='none',
                 markeredgecolor=color_black, markeredgewidth=1.2, markersize=5, label=r'$V/V_0$')

    handles1 = [h_R, h_V]
    labels1 = [h.get_label() for h in handles1]
    leg1 = ax1.legend(handles1, labels1, loc='upper right', fancybox=False, framealpha=0.95,
                      edgecolor=color_black, facecolor='white', fontsize=10.5, ncol=1)
    leg1.get_frame().set_linewidth(0.8)
    ax1.set_title(r'(a) 药材半径与相对体积的变化', fontsize=12.0, fontweight='bold', pad=10, color=color_black)

    # ==================== (b) 横截面收缩 ====================
    # 彻底删去一切“ (R = ... cm)”字符，仅保留纯粹时间标注
    c0_fill = plt.Circle((0, 0), 2.000, color='#64748B', alpha=0.08, zorder=1)
    c0_edge = plt.Circle((0, 0), 2.000, fill=False, edgecolor=color_black, lw=1.8, linestyle='-', zorder=2,
                         label=r'$t=0\ \mathrm{h}$')

    c4_edge = plt.Circle((0, 0), 1.477, fill=False, edgecolor=color_black, lw=1.4, linestyle='--', zorder=3,
                         label=r'$t=4\ \mathrm{h}$')

    c72_fill = plt.Circle((0, 0), 1.198, color=color_red, alpha=0.10, zorder=4)
    c72_edge = plt.Circle((0, 0), 1.198, fill=False, edgecolor=color_red, lw=1.8, linestyle='-', zorder=5,
                          label=r'$t=72\ \mathrm{h}$')

    ax2.add_patch(c0_fill)
    ax2.add_patch(c0_edge)
    ax2.add_patch(c4_edge)
    ax2.add_patch(c72_fill)
    ax2.add_patch(c72_edge)

    # 坐标中心点与径向辅助基准线
    ax2.scatter(0, 0, color=color_black, s=16, zorder=6)
    ax2.plot([0, 2.0], [0, 0], color=color_black, linestyle=':', lw=1.0, zorder=3)
    ax2.plot([0, 0], [2.0, 0], color=color_black, linestyle=':', lw=1.0, zorder=3)

    ax2.set_xlim(-2.8, 2.8)
    ax2.set_ylim(-2.8, 2.8)
    ax2.set_aspect('equal')
    ax2.set_xticks([-2, -1, 0, 1, 2])
    ax2.set_yticks([-2, -1, 0, 1, 2])
    ax2.tick_params(axis='both', labelcolor=color_black, labelsize=10.5)
    ax2.grid(True, linestyle=':', color=color_grid, alpha=0.9, lw=1.0)
    ax2.set_xlabel(r'$x\ (\mathrm{cm})$', fontsize=11.5, fontweight='bold', color=color_black)
    ax2.set_ylabel(r'$y\ (\mathrm{cm})$', fontsize=11.5, fontweight='bold', color=color_black)

    # 截面图例 (学术直角方框，纯粹时间标注)
    leg2 = ax2.legend(loc='upper right', fancybox=False, framealpha=0.95,
                      edgecolor=color_black, facecolor='white', fontsize=10.0)
    leg2.get_frame().set_linewidth(0.8)
    ax2.set_title(r'(b) 横截面收缩', fontsize=12.0, fontweight='bold', pad=10, color=color_black)

    save_current_figure(fig, 'fig5_radius_shrinkage_dynamics.png')

if __name__ == '__main__':
    main()
