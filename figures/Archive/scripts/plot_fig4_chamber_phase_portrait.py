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

PATH_ATTACHMENT1 = os.path.join(ATTACHMENT_DIR, '附件1.xlsx')

def main():
    print('>>> 正在绘制 图4：烘房温-湿状态演化相平面轨迹...')
    df1 = pd.read_excel(PATH_ATTACHMENT1)
    
    fig, ax_phase = plt.subplots(figsize=(9, 6.2))
    t_h = df1['时间'] / 3600.0

    sc = ax_phase.scatter(df1['温度'], df1['水分浓度'], c=t_h, cmap='viridis', s=40, edgecolors='none', alpha=0.9)
    ax_phase.plot(df1['温度'], df1['水分浓度'], color='gray', alpha=0.45, lw=1.2)
    cbar = plt.colorbar(sc, ax=ax_phase)
    cbar.set_label(r'时间 $t\ (\mathrm{h})$', fontsize=11.5, fontweight='bold')

    # 关键节点标注（定制偏移避免重叠）
    anno_offsets = {
        0: (0.5, -0.0012),
        1800: (0.6, -0.0006),
        3600: (0.6, -0.0006),
        7200: (-3.2, -0.0005),
        10800: (0.5, -0.0008),
        14400: (-2.8, 0.0012)
    }
    for kt, (dx, dy) in anno_offsets.items():
        row = df1[df1['时间'] == kt].iloc[0]
        ax_phase.plot(row['温度'], row['水分浓度'], 'ro', markersize=6.5)
        ax_phase.text(row['温度'] + dx, row['水分浓度'] + dy, rf'$t={kt/3600:.1f}\ \mathrm{{h}}$',
                      fontsize=10.5, fontweight='bold', color='#8B0000')

    ax_phase.set_xlabel(r'温度 $T_{\mathrm{env}}\ (^\circ\mathrm{C})$', fontsize=12, fontweight='bold')
    ax_phase.set_ylabel(r'水分浓度 $C_{\mathrm{env}}\ (\mathrm{kg/kg})$', fontsize=12, fontweight='bold')
    ax_phase.set_title(r'烘房温度-水分浓度相轨迹', fontsize=13, fontweight='bold')
    ax_phase.grid(True, linestyle='--', alpha=0.5)
    save_current_figure(fig, 'fig4_chamber_phase_portrait.png')

if __name__ == '__main__':
    main()
