# -*- coding: utf-8 -*-
"""
烘房温度与水分浓度时序变化图（Fig.1 与 Fig.3 整合重构版）
- 继承 Fig.3 核心表达范式：实测离散散点 (Scatter) + PCHIP 连续插值曲线 (Line)
- 严格遵循三主题色规范：学术红 (#C0392B)、纯粹黑 (#0F172A)、辅助极淡灰 (#E2E8F0)
- 汉字最简化：去除一切冗余定语、状语修饰与箭头文字，符合国际科技期刊规范
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.interpolate import pchip_interpolate

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

from pathlib import Path

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

PATH_ATTACHMENT1 = ATTACHMENT_DIR / '附件1.xlsx'

def main():
    print('>>> 正在绘制 整合版图1：烘房温度与水分浓度变化曲线 (含 PCHIP 插值对比)...')
    df1 = pd.read_excel(PATH_ATTACHMENT1)

    t_raw = df1['时间'].values              # 秒 (0 ~ 14400 s)
    T_raw = df1['温度'].values              # °C
    C_raw = df1['水分浓度'].values          # kg/kg
    t_h_raw = t_raw / 3600.0               # 小时 (0 ~ 4.0 h)

    # 1 秒密度的连续时间轴与 PCHIP 保形单调插值
    t_dense = np.linspace(0, 14400, 14401)
    t_h_dense = t_dense / 3600.0
    T_pchip = pchip_interpolate(t_raw, T_raw, t_dense)
    C_pchip = pchip_interpolate(t_raw, C_raw, t_dense)

    # 画布与主轴配置 (双轴 Twinx，严格限定主题色：红、黑、淡灰)
    fig, ax1 = plt.subplots(figsize=(9.2, 5.0))

    color_red = '#C0392B'    # 主色1：学术深红（温度专属）
    color_black = '#0F172A'  # 主色2：纯粹黑灰（水分与坐标轴专属）
    color_grid = '#E2E8F0'   # 辅助色：极淡灰（仅用于网格）

    # ------------------ 左轴：温度 T_env ------------------
    ax1.set_xlabel(r'时间 $t\ (\mathrm{h})$', fontsize=11.5, fontweight='bold', color=color_black)
    ax1.set_ylabel(r'温度 $T_{\mathrm{env}}\ (^\circ\mathrm{C})$', color=color_black, fontsize=11.5, fontweight='bold')
    
    # 温度实测散点（适当步长抽样，保留通透质感，散点不过密）
    step = 4  # 每隔 4 个实测点绘制一个 marker
    s1 = ax1.scatter(t_h_raw[::step], T_raw[::step], color=color_red, s=18, marker='o',
                     facecolors='none', edgecolors=color_red, linewidths=1.2, zorder=5, label=r'$T_{\mathrm{env}}$ (实测)')
    # 温度 PCHIP 连续插值实线
    l1 = ax1.plot(t_h_dense, T_pchip, color=color_red, lw=2.0, linestyle='-', zorder=4, label=r'$T_{\mathrm{env}}$ (PCHIP)')

    ax1.tick_params(axis='x', labelcolor=color_black, labelsize=10.5)
    ax1.tick_params(axis='y', labelcolor=color_black, labelsize=10.5)
    ax1.set_xlim(-0.08, 4.08)
    ax1.set_ylim(25.0, 55.0)
    ax1.set_yticks(np.linspace(25.0, 55.0, 7))
    ax1.grid(True, linestyle=':', color=color_grid, alpha=0.9, lw=1.0)

    # ------------------ 右轴：水分浓度 C_env ------------------
    ax2 = ax1.twinx()
    ax2.set_ylabel(r'水分浓度 $C_{\mathrm{env}}\ (\mathrm{kg/kg})$', color=color_black, fontsize=11.5, fontweight='bold')

    # 水分实测散点
    s2 = ax2.scatter(t_h_raw[::step], C_raw[::step], color=color_black, s=18, marker='s',
                     facecolors='none', edgecolors=color_black, linewidths=1.2, zorder=5, label=r'$C_{\mathrm{env}}$ (实测)')
    # 水分 PCHIP 连续插值实线 (按要求改为实线)
    l2 = ax2.plot(t_h_dense, C_pchip, color=color_black, lw=1.8, linestyle='-', zorder=4, label=r'$C_{\mathrm{env}}$ (PCHIP)')

    ax2.tick_params(axis='y', labelcolor=color_black, labelsize=10.5)
    ax2.set_ylim(0.010, 0.070)
    ax2.set_yticks(np.linspace(0.010, 0.070, 7))

    # ------------------ 合并图例 (左上角，严格学术直角方框) ------------------
    handles = [s1, l1[0], s2, l2[0]]
    labels = [h.get_label() for h in handles]
    leg = ax1.legend(handles, labels, loc='upper left', fancybox=False, framealpha=0.95,
                     edgecolor=color_black, facecolor='white', fontsize=10.0, ncol=2)
    leg.get_frame().set_linewidth(0.8)

    # 标题：去除冗长定语状语，纯粹客观
    plt.title(r'烘房温度与水分浓度变化曲线', fontsize=13.0, fontweight='bold', pad=12, color=color_black)

    save_current_figure(fig, 'fig1_chamber_temp_humidity.png')

if __name__ == '__main__':
    main()
