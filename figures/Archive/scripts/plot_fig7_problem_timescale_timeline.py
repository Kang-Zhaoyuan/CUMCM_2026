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

def main():
    print('>>> 正在绘制 图7：四问求解时间尺度对比甘特图...')
    fig, ax_timeline = plt.subplots(figsize=(11.5, 5.0))

    bars = [
        ('问题 1', 0, 0.5, '#E74C3C', r'$0.5\ \mathrm{h}$: 恒定物性'),
        ('问题 2', 0, 3.0, '#E67E22', r'$3.0\ \mathrm{h}$: 变物性耦合'),
        ('附件 1', 0, 4.0, '#3498DB', r'$4.0\ \mathrm{h}$: 烘房实测数据'),
        ('问题 3', 0, 48.0, '#27AE60', r'$\approx 48\ \mathrm{h}$: 全程烘干 ($\max C \leq 0.15$)'),
        ('附件 2', 0, 72.0, '#8E44AD', r'$72.0\ \mathrm{h}$: 半径实测数据')
    ]

    y_pos = np.arange(len(bars))
    for i, (name, start, end, color, desc) in enumerate(bars):
        ax_timeline.barh(i, end - start, left=start, height=0.55, color=color, alpha=0.85, edgecolor='black')
        ax_timeline.text(end + 1.2, i, desc, va='center', fontsize=10.5, fontweight='bold', color=color)

    ax_timeline.set_yticks(y_pos)
    ax_timeline.set_yticklabels([b[0] for b in bars], fontsize=11.5, fontweight='bold')
    ax_timeline.set_xlabel(r'时间 $t\ (\mathrm{h})$', fontsize=12, fontweight='bold')
    ax_timeline.set_xlim(0, 90)
    ax_timeline.set_title(r'求解时间范围与附件数据跨度对比', fontsize=13.5, fontweight='bold', pad=12)
    ax_timeline.grid(True, axis='x', linestyle='--', alpha=0.6)

    save_current_figure(fig, 'fig7_problem_timescale_timeline.png')

if __name__ == '__main__':
    main()
