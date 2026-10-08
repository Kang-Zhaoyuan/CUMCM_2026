# -*- coding: utf-8 -*-
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# 全局绘图风格与 LaTeX 数学公式渲染配置
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

PROJECT_ROOT = r'D:\HIT\数模2026'
ATTACHMENT_DIR = os.path.join(PROJECT_ROOT, 'CUMCM2026Problems', 'A题', '附件')
OUT_DIR_LOCAL = os.path.join(PROJECT_ROOT, 'eda_figures')
OUT_DIR_ARTIFACT = r'C:\Users\kqdx\.gemini\antigravity\brain\984f8f9b-1caf-4e5e-a827-7c48f241b73b'

os.makedirs(OUT_DIR_LOCAL, exist_ok=True)
os.makedirs(OUT_DIR_ARTIFACT, exist_ok=True)

def save_current_figure(fig, filename):
    p1 = os.path.join(OUT_DIR_LOCAL, filename)
    p2 = os.path.join(OUT_DIR_ARTIFACT, filename)
    fig.savefig(p1, dpi=300, bbox_inches='tight')
    if os.path.exists(os.path.dirname(p2)):
        fig.savefig(p2, dpi=300, bbox_inches='tight')
    plt.close(fig)
    print(f'[√] 已保存高分辨率图件: {filename}')

from scipy.interpolate import pchip_interpolate
from mpl_toolkits.axes_grid1.inset_locator import inset_axes, mark_inset

PATH_ATTACHMENT1 = os.path.join(ATTACHMENT_DIR, '附件1.xlsx')

def main():
    print('>>> 正在绘制 图3：离散测量数据与连续插值曲线对比...')
    df1 = pd.read_excel(PATH_ATTACHMENT1)
    
    t_raw = df1['时间'].values
    T_raw = df1['温度'].values
    t_dense = np.linspace(0, 14400, 14401)  # 每秒 1 个点

    T_pchip = pchip_interpolate(t_raw, T_raw, t_dense)

    fig, ax_interp = plt.subplots(figsize=(10.5, 5.8))
    ax_interp.scatter(t_raw / 60.0, T_raw, color='#2C3E50', s=16, zorder=5, label=r'实测数据')
    ax_interp.plot(t_dense / 60.0, T_pchip, color='#E67E22', lw=2.2, label=r'PCHIP 插值')
    ax_interp.set_xlabel(r'时间 $t\ (\mathrm{min})$', fontsize=12, fontweight='bold')
    ax_interp.set_ylabel(r'温度 $T_{\mathrm{env}}\ (^\circ\mathrm{C})$', fontsize=12, fontweight='bold')
    ax_interp.grid(True, linestyle='--', alpha=0.5)
    ax_interp.legend(loc='lower right', framealpha=0.92, fontsize=10.5)
    ax_interp.set_title(r'烘房温度实测数据与 PCHIP 插值对比', fontsize=13, fontweight='bold')

    # 局部放大窗口 (前 20 分钟)
    ax_ins = inset_axes(ax_interp, width='38%', height='40%', loc='center right', borderpad=2.2)
    mask_ins = (t_raw <= 1200)
    mask_dense = (t_dense <= 1200)
    ax_ins.scatter(t_raw[mask_ins] / 60.0, T_raw[mask_ins], color='#2C3E50', s=26, zorder=5)
    ax_ins.plot(t_dense[mask_dense] / 60.0, T_pchip[mask_dense], color='#E67E22', lw=2.2)
    ax_ins.grid(True, linestyle=':', alpha=0.6)
    ax_ins.set_title(r'局部放大', fontsize=10, fontweight='bold')
    mark_inset(ax_interp, ax_ins, loc1=2, loc2=4, fc='none', ec='0.4', lw=1.2)

    save_current_figure(fig, 'fig3_boundary_interpolation_inset.png')

if __name__ == '__main__':
    main()
