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
    print('>>> 正在绘制 图2：烘房升温速率与水分浓度变化率时序特征...')
    df1 = pd.read_excel(PATH_ATTACHMENT1)
    
    dt_min = df1['时间'].diff() / 60.0  # 1 min
    dT_dt = df1['温度'].diff() / dt_min  # ℃ / min
    dC_dt = df1['水分浓度'].diff() / dt_min * 1000  # g/(kg·min)
    t_h = df1['时间'] / 3600.0

    fig, (ax_rate1, ax_rate2) = plt.subplots(2, 1, figsize=(10.5, 7.2), sharex=True)

    # 升温速率
    dT_series = pd.Series(dT_dt[1:].values)
    dT_smooth = dT_series.rolling(window=7, center=True).mean()
    ax_rate1.plot(t_h[1:], dT_dt[1:], color='#E74C3C', lw=1.0, marker='o', markersize=2.5, alpha=0.35,
                  label=r'差分值')
    ax_rate1.plot(t_h[1:], dT_smooth, color='#922B21', lw=2.4,
                  label=r'滑动平均')
    ax_rate1.axhline(0, color='gray', linestyle=':', lw=1.2)
    ax_rate1.set_ylabel(r'$\frac{\mathrm{d}T_{\mathrm{env}}}{\mathrm{d}t}\ (^\circ\mathrm{C}/\mathrm{min})$', fontsize=12, fontweight='bold')
    ax_rate1.grid(True, linestyle='--', alpha=0.5)
    ax_rate1.legend(loc='upper right', fontsize=10.5, framealpha=0.92)
    ax_rate1.set_title(r'烘房温度与水分浓度变化率', fontsize=13, fontweight='bold')

    # 增湿速率
    dC_series = pd.Series(dC_dt[1:].values)
    dC_smooth = dC_series.rolling(window=7, center=True).mean()
    ax_rate2.plot(t_h[1:], dC_dt[1:], color='#2980B9', lw=1.0, marker='s', markersize=2.5, alpha=0.35,
                  label=r'差分值')
    ax_rate2.plot(t_h[1:], dC_smooth, color='#1B4F72', lw=2.4,
                  label=r'滑动平均')
    ax_rate2.axhline(0, color='gray', linestyle=':', lw=1.2)
    ax_rate2.set_xlabel(r'时间 $t\ (\mathrm{h})$', fontsize=12, fontweight='bold')
    ax_rate2.set_ylabel(r'$\frac{\mathrm{d}C_{\mathrm{env}}}{\mathrm{d}t}\ (\mathrm{g}/(\mathrm{kg}\cdot\mathrm{min}))$', fontsize=12, fontweight='bold')
    ax_rate2.grid(True, linestyle='--', alpha=0.5)
    ax_rate2.legend(loc='upper right', fontsize=10.5, framealpha=0.92)

    save_current_figure(fig, 'fig2_chamber_change_rates.png')

if __name__ == '__main__':
    main()
