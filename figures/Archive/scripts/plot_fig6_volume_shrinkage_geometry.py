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
    try:
        fig.tight_layout()
    except Exception:
        pass
    p1 = os.path.join(OUT_DIR_LOCAL, filename)
    p2 = os.path.join(OUT_DIR_ARTIFACT, filename)
    fig.savefig(p1, dpi=300, bbox_inches='tight')
    if os.path.exists(os.path.dirname(p2)):
        fig.savefig(p2, dpi=300, bbox_inches='tight')
    plt.close(fig)
    print(f'[√] 已保存高分辨率图件: {filename}')

PATH_ATTACHMENT2 = os.path.join(ATTACHMENT_DIR, '附件2.xlsx')

def main():
    print('>>> 正在绘制 图6：径向收缩率、相对体积比例与横截面形变图解...')
    df2 = pd.read_excel(PATH_ATTACHMENT2)
    
    t2_h = df2['时间'] / 3600.0
    r2 = df2['半径'].values

    fig = plt.figure(figsize=(12.5, 5.8))
    ax_rate = fig.add_subplot(1, 2, 1)

    shrinkage_ratio = (2.0 - r2) / 2.0 * 100.0  # %
    volume_ratio = (r2 / 2.0)**2 * 100.0        # %

    ax_rate.plot(t2_h, shrinkage_ratio, color='#C0392B', lw=2.5, label=r'径向收缩率 $\eta(t)$')
    ax_rate.plot(t2_h, volume_ratio, color='#2980B9', lw=2.5, linestyle='--', label=r'相对体积 $V(t)/V_0$')

    ax_rate.set_xlabel(r'时间 $t\ (\mathrm{h})$', fontsize=12, fontweight='bold')
    ax_rate.set_ylabel(r'比例 / $\%$', fontsize=12, fontweight='bold')
    ax_rate.set_title(r'(a) 收缩率与相对体积变化', fontsize=12.5, fontweight='bold')
    ax_rate.set_ylim(-5, 105)
    ax_rate.grid(True, linestyle='--', alpha=0.5)
    ax_rate.legend(loc='upper right', framealpha=0.92, fontsize=10.5)
    
    anno_text = f"最大收缩率: {shrinkage_ratio[-1]:.1f}%\n" + f"终态体积: {volume_ratio[-1]:.1f}%"
    ax_rate.annotate(anno_text,
                     xy=(70, shrinkage_ratio[-1]), xytext=(34, 15),
                     arrowprops=dict(arrowstyle='->', color='#C0392B', lw=1.5), fontsize=10.5, fontweight='bold',
                     bbox=dict(boxstyle='round,pad=0.5', facecolor='#FDEDEC', edgecolor='#C0392B'))

    # 右图：圆柱截面收缩几何图解
    ax_geom = fig.add_subplot(1, 2, 2)
    circle_init = plt.Circle((0, 0), 2.0, color='#3498DB', alpha=0.25, label=r'$t=0\ \mathrm{h}\ (R=2.00\ \mathrm{cm})$')
    circle_border_init = plt.Circle((0, 0), 2.0, fill=False, edgecolor='#2980B9', lw=2.2, linestyle='--')
    circle_mid = plt.Circle((0, 0), 1.477, color='#F39C12', alpha=0.35, label=r'$t=4\ \mathrm{h}\ (R=1.48\ \mathrm{cm})$')
    circle_border_mid = plt.Circle((0, 0), 1.477, fill=False, edgecolor='#D68910', lw=2, linestyle=':')
    circle_end = plt.Circle((0, 0), 1.198, color='#E74C3C', alpha=0.45, label=r'$t=72\ \mathrm{h}\ (R=1.20\ \mathrm{cm})$')
    circle_border_end = plt.Circle((0, 0), 1.198, fill=False, edgecolor='#C0392B', lw=2.2)

    ax_geom.add_patch(circle_init)
    ax_geom.add_patch(circle_border_init)
    ax_geom.add_patch(circle_mid)
    ax_geom.add_patch(circle_border_mid)
    ax_geom.add_patch(circle_end)
    ax_geom.add_patch(circle_border_end)

    ax_geom.set_xlim(-2.5, 2.5)
    ax_geom.set_ylim(-2.5, 2.5)
    ax_geom.set_aspect('equal')
    ax_geom.grid(True, linestyle=':', alpha=0.5)
    ax_geom.set_xlabel(r'$x\ (\mathrm{cm})$', fontsize=12, fontweight='bold')
    ax_geom.set_ylabel(r'$y\ (\mathrm{cm})$', fontsize=12, fontweight='bold')
    ax_geom.set_title(r'(b) 横截面收缩几何对比', fontsize=12.5, fontweight='bold')
    ax_geom.legend(loc='upper right', fontsize=10, framealpha=0.92)

    save_current_figure(fig, 'fig6_volume_shrinkage_geometry.png')

if __name__ == '__main__':
    main()
