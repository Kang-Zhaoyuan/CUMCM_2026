# -*- coding: utf-8 -*-
"""
================================================================================
2026年高教社杯全国大学生数学建模竞赛 - A题：药材的烘干问题
附件 1 与 附件 2 数据探索性分析 (EDA) 与机理特性全套绘图脚本

功能说明:
1. 读取 附件1.xlsx 与 附件2.xlsx 的实测数据
2. 使用 LaTeX (STIX) 专业数学公式字体排版坐标轴、图例、标题与数据批注
3. 一键生成 7 张高分辨率学术图件（300 DPI），兼顾国赛论文排版美观度
4. 支持独立调用各图绘制函数，便于针对论文版面进行细节微调

输出目录:
- 本地工作区: D:\\HIT\\数模2026\\eda_figures\\
- 对话缓存区: C:\\Users\\kqdx\\.gemini\\antigravity\\brain\\984f8f9b-1caf-4e5e-a827-7c48f241b73b\\
================================================================================
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.interpolate import pchip_interpolate
from scipy.optimize import curve_fit
from mpl_toolkits.axes_grid1.inset_locator import inset_axes, mark_inset

# ==============================================================================
# 全局绘图风格与 LaTeX 数学公式渲染配置
# ==============================================================================
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'SimSun', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False  # 正常显示负号

# 开启 STIX 专业数学字体（与 Times New Roman 和标准 LaTeX 字体高度一致）
plt.rcParams['mathtext.fontset'] = 'stix'
plt.rcParams['mathtext.rm'] = 'STIXGeneral'
plt.rcParams['mathtext.it'] = 'STIXGeneral:italic'
plt.rcParams['mathtext.bf'] = 'STIXGeneral:bold'

# 刻度与图脊线全局美化
plt.rcParams['xtick.direction'] = 'in'
plt.rcParams['ytick.direction'] = 'in'
plt.rcParams['xtick.major.size'] = 4.5
plt.rcParams['ytick.major.size'] = 4.5
plt.rcParams['lines.linewidth'] = 2.0

# 目录路径
PROJECT_ROOT = r'D:\HIT\数模2026'
ATTACHMENT_DIR = os.path.join(PROJECT_ROOT, 'CUMCM2026Problems', 'A题', '附件')
OUT_DIR_LOCAL = os.path.join(PROJECT_ROOT, 'eda_figures')
OUT_DIR_ARTIFACT = r'C:\Users\kqdx\.gemini\antigravity\brain\984f8f9b-1caf-4e5e-a827-7c48f241b73b'

os.makedirs(OUT_DIR_LOCAL, exist_ok=True)
os.makedirs(OUT_DIR_ARTIFACT, exist_ok=True)

PATH_ATTACHMENT1 = os.path.join(ATTACHMENT_DIR, '附件1.xlsx')
PATH_ATTACHMENT2 = os.path.join(ATTACHMENT_DIR, '附件2.xlsx')


def save_current_figure(fig, filename):
    """同时保存图件到本地工作区和展示缓存区"""
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


# ==============================================================================
# 图 1：烘房预热平衡阶段温湿度随时间演化曲线（双 Y 轴图）
# ==============================================================================
def plot_fig1(df1):
    fig, ax1 = plt.subplots(figsize=(10.5, 5.8))
    t_h = df1['时间'] / 3600.0

    color_t = '#C0392B'  # 暖红（温度）
    color_c = '#1B6CA8'  # 科技蓝（湿度）

    # 左轴：温度
    ax1.set_xlabel(r'烘干时间 $t\ (\mathrm{h})$', fontsize=12, fontweight='bold')
    ax1.set_ylabel(r'烘房环境温度 $T_\infty(t)\ (^\circ\mathrm{C})$', color=color_t, fontsize=12, fontweight='bold')
    l1 = ax1.plot(t_h, df1['温度'], color=color_t, lw=2.5, label=r'烘房温度 $T_\infty(t)$')
    ax1.tick_params(axis='y', labelcolor=color_t, labelsize=11)
    ax1.set_ylim(25, 55)
    ax1.grid(True, linestyle='--', alpha=0.5)

    # 阶段阴影划分
    ax1.axvspan(0, 0.5, color='#F39C12', alpha=0.15, label='问题1分析区间 ($0 \leq t \leq 0.5\ \mathrm{h}$)')
    ax1.axvspan(0.5, 3.0, color='#3498DB', alpha=0.08, label='升温平衡过渡期 ($0.5 < t \leq 3.0\ \mathrm{h}$)')
    ax1.axvspan(3.0, 4.0, color='#2ECC71', alpha=0.12, label='稳态恒温恒湿期 ($3.0 < t \leq 4.0\ \mathrm{h}$)')

    # 右轴：水分浓度
    ax2 = ax1.twinx()
    ax2.set_ylabel(r'烘房水分浓度 $C_\infty(t)\ (\mathrm{kg/kg})$', color=color_c, fontsize=12, fontweight='bold')
    l2 = ax2.plot(t_h, df1['水分浓度'], color=color_c, lw=2.5, linestyle='--', label=r'烘房水分浓度 $C_\infty(t)$')
    ax2.tick_params(axis='y', labelcolor=color_c, labelsize=11)
    ax2.set_ylim(0.015, 0.055)

    # 关键数值 LaTeX 标注
    ax1.annotate(r'起始初温: $T_\infty(0) = 28.0^\circ\mathrm{C}$', xy=(0, 28), xytext=(0.15, 33),
                 arrowprops=dict(arrowstyle='->', color=color_t, lw=1.5), fontsize=10.5, color=color_t, fontweight='bold')
    ax1.annotate(r'恒温稳态: $T_\infty \approx 50.0^\circ\mathrm{C}$', xy=(3.6, 50.1), xytext=(2.4, 52.2),
                 arrowprops=dict(arrowstyle='->', color=color_t, lw=1.5), fontsize=10.5, color=color_t, fontweight='bold')
    ax2.annotate(r'初始水分: $C_\infty(0) = 0.0196\ \mathrm{kg/kg}$', xy=(0, 0.01963), xytext=(0.4, 0.023),
                 arrowprops=dict(arrowstyle='->', color=color_c, lw=1.5), fontsize=10.5, color=color_c, fontweight='bold')
    ax2.annotate(r'恒湿稳态: $C_\infty \approx 0.0500\ \mathrm{kg/kg}$', xy=(4.0, 0.04986), xytext=(2.7, 0.044),
                 arrowprops=dict(arrowstyle='->', color=color_c, lw=1.5), fontsize=10.5, color=color_c, fontweight='bold')

    lines = l1 + l2
    labels = [l.get_label() for l in lines]
    ax1.legend(lines, labels, loc='upper left', framealpha=0.92, fontsize=10)
    plt.title(r'附件 1：烘房预热平衡阶段环境温湿度时序演化曲线 ($0 \leq t \leq 4\ \mathrm{h}$)', fontsize=13.5, fontweight='bold', pad=12)
    save_current_figure(fig, 'fig1_chamber_temp_humidity.png')


# ==============================================================================
# 图 2：烘房升温与增湿速率变化图（一阶导数分析）
# ==============================================================================
def plot_fig2(df1):
    dt_min = df1['时间'].diff() / 60.0  # 1 min
    dT_dt = df1['温度'].diff() / dt_min  # ℃ / min
    dC_dt = df1['水分浓度'].diff() / dt_min * 1000  # g/(kg·min)
    t_h = df1['时间'] / 3600.0

    fig, (ax_rate1, ax_rate2) = plt.subplots(2, 1, figsize=(10.5, 7.2), sharex=True)

    # 升温速率
    dT_series = pd.Series(dT_dt[1:].values)
    dT_smooth = dT_series.rolling(window=7, center=True).mean()
    ax_rate1.plot(t_h[1:], dT_dt[1:], color='#E74C3C', lw=1.0, marker='o', markersize=2.5, alpha=0.35,
                  label=r'一阶差分观测值 $\frac{\Delta T_\infty}{\Delta t}$')
    ax_rate1.plot(t_h[1:], dT_smooth, color='#922B21', lw=2.4,
                  label=r'平滑宏观趋势线 (Rolling Mean, 7 min)')
    ax_rate1.axhline(0, color='gray', linestyle=':', lw=1.2)
    ax_rate1.set_ylabel(r'$\frac{\mathrm{d}T_\infty}{\mathrm{d}t}\ (^\circ\mathrm{C}/\mathrm{min})$', fontsize=12, fontweight='bold')
    ax_rate1.grid(True, linestyle='--', alpha=0.5)
    ax_rate1.legend(loc='upper right', fontsize=10.5, framealpha=0.92)
    ax_rate1.set_title(r'附件 1：烘房升温速率与水分浓度变化率时序特征（设备控制动力学）', fontsize=13, fontweight='bold')

    # 增湿速率
    dC_series = pd.Series(dC_dt[1:].values)
    dC_smooth = dC_series.rolling(window=7, center=True).mean()
    ax_rate2.plot(t_h[1:], dC_dt[1:], color='#2980B9', lw=1.0, marker='s', markersize=2.5, alpha=0.35,
                  label=r'一阶差分观测值 $\frac{\Delta C_\infty}{\Delta t}$')
    ax_rate2.plot(t_h[1:], dC_smooth, color='#1B4F72', lw=2.4,
                  label=r'平滑宏观趋势线 (Rolling Mean, 7 min)')
    ax_rate2.axhline(0, color='gray', linestyle=':', lw=1.2)
    ax_rate2.set_xlabel(r'烘干时间 $t\ (\mathrm{h})$', fontsize=12, fontweight='bold')
    ax_rate2.set_ylabel(r'$\frac{\mathrm{d}C_\infty}{\mathrm{d}t}\ (\mathrm{g}/(\mathrm{kg}\cdot\mathrm{min}))$', fontsize=12, fontweight='bold')
    ax_rate2.grid(True, linestyle='--', alpha=0.5)
    ax_rate2.legend(loc='upper right', fontsize=10.5, framealpha=0.92)

    save_current_figure(fig, 'fig2_chamber_change_rates.png')


# ==============================================================================
# 图 3：离散实测数据与连续插值拟合（PDE 连续边界输入）
# ==============================================================================
def plot_fig3(df1):
    t_raw = df1['时间'].values
    T_raw = df1['温度'].values
    t_dense = np.linspace(0, 14400, 14401)  # 每秒 1 个点

    T_pchip = pchip_interpolate(t_raw, T_raw, t_dense)

    fig, ax_interp = plt.subplots(figsize=(10.5, 5.8))
    ax_interp.scatter(t_raw / 60.0, T_raw, color='#2C3E50', s=16, zorder=5, label=r'附件1离散实测数据 ($\Delta t = 60\ \mathrm{s}$)')
    ax_interp.plot(t_dense / 60.0, T_pchip, color='#E67E22', lw=2.2, label=r'PCHIP 单调保形插值连续曲线 ($\Delta t = 1\ \mathrm{s}$)')
    ax_interp.set_xlabel(r'时间 $t\ (\mathrm{min})$', fontsize=12, fontweight='bold')
    ax_interp.set_ylabel(r'烘房环境温度 $T_\infty\ (^\circ\mathrm{C})$', fontsize=12, fontweight='bold')
    ax_interp.grid(True, linestyle='--', alpha=0.5)
    ax_interp.legend(loc='lower right', framealpha=0.92, fontsize=10.5)
    ax_interp.set_title(r'附件 1：离散测量数据与连续插值曲线对比（为 PDE 提供高频平滑边界输入）', fontsize=13, fontweight='bold')

    # 局部放大窗口 (前 20 分钟)
    ax_ins = inset_axes(ax_interp, width='38%', height='40%', loc='center right', borderpad=2.2)
    mask_ins = (t_raw <= 1200)
    mask_dense = (t_dense <= 1200)
    ax_ins.scatter(t_raw[mask_ins] / 60.0, T_raw[mask_ins], color='#2C3E50', s=26, zorder=5)
    ax_ins.plot(t_dense[mask_dense] / 60.0, T_pchip[mask_dense], color='#E67E22', lw=2.2)
    ax_ins.grid(True, linestyle=':', alpha=0.6)
    ax_ins.set_title(r'前 $20\ \mathrm{min}$ 局部放大（单调保形、无振荡）', fontsize=9.5)
    mark_inset(ax_interp, ax_ins, loc1=2, loc2=4, fc='none', ec='0.4', lw=1.2)

    save_current_figure(fig, 'fig3_boundary_interpolation_inset.png')


# ==============================================================================
# 图 4：烘房温-湿状态演化相平面轨迹
# ==============================================================================
def plot_fig4(df1):
    fig, ax_phase = plt.subplots(figsize=(9, 6.2))
    t_h = df1['时间'] / 3600.0

    sc = ax_phase.scatter(df1['温度'], df1['水分浓度'], c=t_h, cmap='viridis', s=40, edgecolors='none', alpha=0.9)
    ax_phase.plot(df1['温度'], df1['水分浓度'], color='gray', alpha=0.45, lw=1.2)
    cbar = plt.colorbar(sc, ax=ax_phase)
    cbar.set_label(r'烘干时间 $t\ (\mathrm{h})$', fontsize=11.5, fontweight='bold')

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

    ax_phase.set_xlabel(r'烘房温度 $T_\infty\ (^\circ\mathrm{C})$', fontsize=12, fontweight='bold')
    ax_phase.set_ylabel(r'烘房水分浓度 $C_\infty\ (\mathrm{kg/kg})$', fontsize=12, fontweight='bold')
    ax_phase.set_title(r'附件 1：烘房温-湿状态演化相平面轨迹（由常温干燥向高温湿平衡演变）', fontsize=13, fontweight='bold')
    ax_phase.grid(True, linestyle='--', alpha=0.5)
    save_current_figure(fig, 'fig4_chamber_phase_portrait.png')


# ==============================================================================
# 图 5：药材半径随时间收缩动力学全景图（72 小时实测与动力学拟合）
# ==============================================================================
def plot_fig5(df2):
    t2_h = df2['时间'] / 3600.0
    r2 = df2['半径'].values

    # 动力学模型: R(t) = R_inf + (R_0 - R_inf) * exp(-(t/tau)^beta)
    def shrinkage_model(t, r_inf, tau, beta):
        return r_inf + (2.0 - r_inf) * np.exp(-(t / tau)**beta)

    popt, _ = curve_fit(shrinkage_model, t2_h, r2, p0=[1.2, 10.0, 1.0])
    r_fit = shrinkage_model(t2_h, *popt)

    fig, ax_shrink = plt.subplots(figsize=(10.5, 6.0))
    ax_shrink.scatter(t2_h, r2, color='#2C3E50', s=26, alpha=0.85,
                      label=r'附件 2 实测数据 ($\Delta t = 0.5\ \mathrm{h}$, 共 $72\ \mathrm{h}$)')
    fit_label = rf'动力学拟合: $R(t) = {popt[0]:.3f} + (2.0 - {popt[0]:.3f})\exp[-(t/{popt[1]:.2f})^{{{popt[2]:.2f}}}]$'
    ax_shrink.plot(t2_h, r_fit, color='#E74C3C', lw=2.4, label=fit_label)

    # 阶段阴影
    ax_shrink.axvspan(0, 12, color='#E74C3C', alpha=0.10, label='快速失水收缩阶段 ($0 \leq t \leq 12\ \mathrm{h}$)')
    ax_shrink.axvspan(12, 40, color='#F39C12', alpha=0.10, label='减速收缩阶段 ($12 < t \leq 40\ \mathrm{h}$)')
    ax_shrink.axvspan(40, 72, color='#27AE60', alpha=0.10, label='形变平衡极限阶段 ($40 < t \leq 72\ \mathrm{h}$)')

    ax_shrink.axhline(1.198, color='purple', linestyle='--', lw=1.5, label=r'极限收缩半径: $R_{\infty} = 1.198\ \mathrm{cm}$')
    ax_shrink.annotate(r'形变达到终态平衡 ($R = 1.198\ \mathrm{cm}$)', xy=(60, 1.198), xytext=(45, 1.45),
                       arrowprops=dict(arrowstyle='->', color='purple', lw=1.5), fontsize=10.5, color='purple', fontweight='bold')

    ax_shrink.set_xlabel(r'烘干时间 $t\ (\mathrm{h})$', fontsize=12, fontweight='bold')
    ax_shrink.set_ylabel(r'药材半径 $R(t)\ (\mathrm{cm})$', fontsize=12, fontweight='bold')
    ax_shrink.set_ylim(1.1, 2.1)
    ax_shrink.grid(True, linestyle='--', alpha=0.5)
    ax_shrink.legend(loc='upper right', framealpha=0.92, fontsize=10)
    ax_shrink.set_title(r'附件 2：药材半径随时间收缩动力学演化历程与阶段特征（72 小时实测）', fontsize=13.5, fontweight='bold', pad=12)

    save_current_figure(fig, 'fig5_radius_shrinkage_dynamics.png')


# ==============================================================================
# 图 6：径向收缩率、相对体积比例与横截面形变图解
# ==============================================================================
def plot_fig6(df2):
    t2_h = df2['时间'] / 3600.0
    r2 = df2['半径'].values

    fig = plt.figure(figsize=(12.5, 5.8))
    ax_rate = fig.add_subplot(1, 2, 1)

    shrinkage_ratio = (2.0 - r2) / 2.0 * 100.0  # %
    volume_ratio = (r2 / 2.0)**2 * 100.0        # %

    ax_rate.plot(t2_h, shrinkage_ratio, color='#C0392B', lw=2.5, label=r'径向收缩率 $\eta_r(t) = \frac{R_0 - R(t)}{R_0}\times 100\%$')
    ax_rate.plot(t2_h, volume_ratio, color='#2980B9', lw=2.5, linestyle='--', label=r'相对体积留存率 $\frac{V(t)}{V_0}\times 100\%$')

    ax_rate.set_xlabel(r'烘干时间 $t\ (\mathrm{h})$', fontsize=12, fontweight='bold')
    ax_rate.set_ylabel(r'比例 / $\%$', fontsize=12, fontweight='bold')
    ax_rate.set_title(r'(a) 药材收缩率与体积留存率演化曲线', fontsize=12.5, fontweight='bold')
    ax_rate.set_ylim(-5, 105)
    ax_rate.grid(True, linestyle='--', alpha=0.5)
    anno_text = f"最大径向收缩率: {shrinkage_ratio[-1]:.1f}%\n最终体积仅剩: {volume_ratio[-1]:.1f}%"
    ax_rate.annotate(anno_text,
                     xy=(70, shrinkage_ratio[-1]), xytext=(34, 15),
                     arrowprops=dict(arrowstyle='->', color='#C0392B', lw=1.5), fontsize=10.5, fontweight='bold',
                     bbox=dict(boxstyle='round,pad=0.5', facecolor='#FDEDEC', edgecolor='#C0392B'))

    # 右图：圆柱截面收缩几何图解
    ax_geom = fig.add_subplot(1, 2, 2)
    circle_init = plt.Circle((0, 0), 2.0, color='#3498DB', alpha=0.25, label=r'初始截面 ($t=0\ \mathrm{h}, R=2.00\ \mathrm{cm}$)')
    circle_border_init = plt.Circle((0, 0), 2.0, fill=False, edgecolor='#2980B9', lw=2.2, linestyle='--')
    circle_mid = plt.Circle((0, 0), 1.477, color='#F39C12', alpha=0.35, label=r'中期截面 ($t=4\ \mathrm{h}, R=1.48\ \mathrm{cm}$)')
    circle_border_mid = plt.Circle((0, 0), 1.477, fill=False, edgecolor='#D68910', lw=2, linestyle=':')
    circle_end = plt.Circle((0, 0), 1.198, color='#E74C3C', alpha=0.45, label=r'终态截面 ($t=72\ \mathrm{h}, R=1.20\ \mathrm{cm}$)')
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
    ax_geom.set_title(r'(b) 药材圆柱横截面形变收缩几何对比', fontsize=12.5, fontweight='bold')
    ax_geom.legend(loc='upper right', fontsize=9.5, framealpha=0.92)

    save_current_figure(fig, 'fig6_volume_shrinkage_geometry.png')


# ==============================================================================
# 图 7：四问求解时间尺度对比甘特图
# ==============================================================================
def plot_fig7():
    fig, ax_timeline = plt.subplots(figsize=(11.5, 5.0))

    bars = [
        ('问题 1 分析区间', 0, 0.5, '#E74C3C', r'$0.5\ \mathrm{h}\ (1800\ \mathrm{s})$: 恒定物性 / 预热初期'),
        ('问题 2 分析区间', 0, 3.0, '#E67E22', r'$3.0\ \mathrm{h}$: 变物性 / 温度-水分非线性耦合'),
        ('附件 1 烘房实测', 0, 4.0, '#3498DB', r'$4.0\ \mathrm{h}\ (14400\ \mathrm{s})$: 升温阶段 $\rightarrow 50^\circ\mathrm{C}, 0.05$ 恒定'),
        ('问题 3 烘干全程', 0, 48.0, '#27AE60', r'全程烘干至 $\max C \leq 0.15\ \mathrm{kg/kg}$ (恒定外界边界)'),
        ('附件 2 半径测量', 0, 72.0, '#8E44AD', r'$72.0\ \mathrm{h}\ (259200\ \mathrm{s})$: 完整 3 天尺寸动态实测')
    ]

    y_pos = np.arange(len(bars))
    for i, (name, start, end, color, desc) in enumerate(bars):
        ax_timeline.barh(i, end - start, left=start, height=0.55, color=color, alpha=0.85, edgecolor='black')
        ax_timeline.text(end + 1.2, i, desc, va='center', fontsize=10, fontweight='bold', color=color)

    ax_timeline.set_yticks(y_pos)
    ax_timeline.set_yticklabels([b[0] for b in bars], fontsize=11.5, fontweight='bold')
    ax_timeline.set_xlabel(r'时间尺度 $t\ (\mathrm{h})$', fontsize=12, fontweight='bold')
    ax_timeline.set_xlim(0, 90)
    ax_timeline.set_title(r'附件数据时间跨度与问题 1~4 求解范围的层层递进关系', fontsize=13.5, fontweight='bold', pad=12)
    ax_timeline.grid(True, axis='x', linestyle='--', alpha=0.6)

    save_current_figure(fig, 'fig7_problem_timescale_timeline.png')


# ==============================================================================
# 主入口
# ==============================================================================
if __name__ == '__main__':
    print('>>> 正在加载数据...')
    df1 = pd.read_excel(PATH_ATTACHMENT1)
    df2 = pd.read_excel(PATH_ATTACHMENT2)

    print('>>> 正在绘制并应用 LaTeX 公式渲染...')
    plot_fig1(df1)
    plot_fig2(df1)
    plot_fig3(df1)
    plot_fig4(df1)
    plot_fig5(df2)
    plot_fig6(df2)
    plot_fig7()
    print('>>> 全部 7 张图表已生成完毕并保存至:', OUT_DIR_LOCAL)
