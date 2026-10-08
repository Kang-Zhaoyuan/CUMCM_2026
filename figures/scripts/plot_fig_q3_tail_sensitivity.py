# -*- coding: utf-8 -*-
"""
问题 3 环境延拓点数敏感性分析折线图（CUPT 极简经典学术风 - 冻结定稿版）
=============================================================================
核心视觉设计规范（严格遵循 CUPT 物理竞赛学术图件标准与项目规范）：
1. 四边全框封闭 + 四边朝内刻度（direction='in', top=True, right=True），纯白底色无网格线；
2. 粗实黑线（lw=2.4）搭配大尺寸白心黑边圆点标记（o, ms=9.5, mfc='white', mew=2.2）；
3. 灰色虚线基准线（t* = 57.44 h）搭配浅灰偏差包络阴影（#E5E7EB, alpha=0.85）；
4. N=20 处竖直虚线标注“正式方案 ($N=20$)”，文字置顶微遮蔽，视觉指引清晰；
5. 右侧保留高精暗红误差棒（Delta t = 3.2 min, +-0.09%），直观展示微小扰动收敛性；
6. 严格剔除散点上的非必要数字，保留最纯粹坐标与物理刻度；
7. 纯正高清位图输出：专为 LaTeX 论文与报告统一生成 300 DPI 超清 PNG 格式，并自动同步至 figures/ 目录。

数据来源：
- final/对照实验结果/问题3/result3_nr120_nz120_tail{1,5,10,20,60}_*.log
=============================================================================
"""

import os
import json
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt

# -------------------------------------------------------------
# 1. 字体与画布基础配置 (SongTi / SimSun + STIX 经典学术体)
# -------------------------------------------------------------
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.serif'] = ['SimSun', 'STSong', 'Times New Roman', 'DejaVu Serif']
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['mathtext.fontset'] = 'stix'
plt.rcParams['mathtext.rm'] = 'STIXGeneral'
plt.rcParams['mathtext.it'] = 'STIXGeneral:italic'
plt.rcParams['mathtext.bf'] = 'STIXGeneral:bold'

# -------------------------------------------------------------
# 2. 路径自适应解析 (支持任意工作路径调用)
# -------------------------------------------------------------
SCRIPT_DIR = Path(__file__).resolve().parent
OUT_DIR_LOCAL = SCRIPT_DIR.parent
PROJECT_ROOT = OUT_DIR_LOCAL.parent
RESULT_DIR = PROJECT_ROOT / 'final' / '对照实验结果' / '问题3'
FIG_DIR_TEX = PROJECT_ROOT / 'paper' / 'figures'

OUT_DIR_LOCAL.mkdir(parents=True, exist_ok=True)
FIG_DIR_TEX.mkdir(parents=True, exist_ok=True)


def load_tail_results():
    """读取 5 组 tail 延拓对照实验数据并提取烘干时长 (h)"""
    tails = [1, 5, 10, 20, 60]
    dry_times = []

    for t in tails:
        log_files = list(RESULT_DIR.glob(f'*tail{t}_*.log'))
        if not log_files:
            raise FileNotFoundError(f"未找到 tail={t} 的对照实验日志文件！路径: {RESULT_DIR}")
        with open(log_files[0], 'r', encoding='utf-8') as f:
            lines = [line for line in f.readlines() if not line.startswith(('运行', 'Excel', 't=', '第3问', '烘干'))]
            log_data = json.loads(''.join(lines))
        dry_s = float(log_data['dry_time_s'])
        dry_times.append(dry_s / 3600.0)

    return tails, np.array(dry_times)


def main():
    print('>>> 正在绘制 问题3环境延拓敏感性分析图 (CUPT 极简学术风 - 冻结定稿版)...')

    tails, dry_times = load_tail_results()
    base_dry_h = dry_times[3]  # N=20 基准点: 57.4354 h

    # ---------------------------------------------------------
    # 3. 创建画布与经典边框刻度
    # ---------------------------------------------------------
    fig, ax = plt.subplots(figsize=(11.0, 5.5), dpi=300)

    # 四边全框封闭 + 四边朝内刻度 + 纯白底色无网格
    ax.tick_params(direction='in', top=True, right=True, which='both',
                   length=6.0, width=1.1, labelsize=11.5)
    for spine in ax.spines.values():
        spine.set_linewidth(1.1)
        spine.set_color('black')
    ax.grid(False)

    # X 轴与 Y 轴范围设定 (充足呼吸留白)
    x_indices = np.array([1, 2, 3, 4, 5])
    ax.set_xlim(0.4, 6.3)
    ax.set_ylim(57.02, 57.72)

    # ---------------------------------------------------------
    # 4. 理论基准线与偏差包络阴影
    # ---------------------------------------------------------
    # 水平理论基准线 (N=20: 57.4354 h)
    line_base = ax.axhline(base_dry_h, color='#666666', linestyle='--', linewidth=1.8,
                           label=r'基准线 ($t^* = 57.44\ \mathrm{h}$)')

    # 竖直虚线标注正式方案 (N=20 位于 x=4)
    ax.axvline(4, color='#666666', linestyle='--', linewidth=1.6)

    # 浅灰色偏差包络区域 (fill_between)
    poly_fill = ax.fill_between(x_indices, dry_times, base_dry_h,
                                color='#E5E7EB', alpha=0.85,
                                label=r'偏差包络')

    # ---------------------------------------------------------
    # 5. 主数据折线与经典大白心黑边圆点
    # ---------------------------------------------------------
    line_main = ax.plot(x_indices, dry_times, color='black', linestyle='-', linewidth=2.4,
                        marker='o', markersize=9.5, markerfacecolor='white',
                        markeredgecolor='black', markeredgewidth=2.2,
                        label=r'烘干时长 $t_{\mathrm{dry}}$', zorder=4)

    # ---------------------------------------------------------
    # 6. 关键注释：竖直虚线（正式方案）与水平基准线（向下箭头）
    # ---------------------------------------------------------
    # 竖直虚线文字标注 (严密控制在画布内部，白底微遮蔽)
    ax.text(4, 57.68, '正式方案\n' + r'($N=20$)', ha='center', va='top',
            fontsize=10.5, color='black', linespacing=1.2,
            bbox=dict(facecolor='white', edgecolor='none', pad=2.0))

    # 水平基准向下指示箭头 (净空区 x=2.85)
    arrow_x = 2.85
    arrow_y_text = 57.61
    ax.text(arrow_x, arrow_y_text, r'$t^* = 57.44\ \mathrm{h}$',
            ha='center', va='bottom', fontsize=11.0, color='black')
    ax.annotate('', xy=(arrow_x, base_dry_h), xytext=(arrow_x, arrow_y_text - 0.005),
                arrowprops=dict(facecolor='black', edgecolor='black', width=1.0, headwidth=5.5, shrink=0.05))

    # ---------------------------------------------------------
    # 7. 右侧单一误差棒 (清晰标注收敛边界)
    # ---------------------------------------------------------
    err_x = 5.45
    err_y_min = dry_times[2]  # N=10: 57.3818
    err_y_max = dry_times[4]  # N=60: 57.4758

    # 绘制深红虚线支架与中心点
    ax.plot([err_x, err_x], [err_y_min, err_y_max], color='#8B0000', linestyle=':', linewidth=2.0, zorder=5)
    ax.plot([err_x - 0.05, err_x + 0.05], [err_y_min, err_y_min], color='#8B0000', linestyle='-', linewidth=1.8, zorder=5)
    ax.plot([err_x - 0.05, err_x + 0.05], [err_y_max, err_y_max], color='#8B0000', linestyle='-', linewidth=1.8, zorder=5)
    ax.plot(err_x, base_dry_h, marker='X', markersize=6.5, color='#8B0000', zorder=6)

    # 误差棒文字：纯粹数学符号，一目了然
    ax.text(err_x + 0.10, base_dry_h,
            r'$\Delta t = 3.2\ \mathrm{min}$' + '\n' + r'$(\pm 0.09\%)$',
            ha='left', va='center', fontsize=10.5, color='#8B0000', linespacing=1.2,
            bbox=dict(facecolor='white', edgecolor='none', pad=2.0))

    # ---------------------------------------------------------
    # 8. 坐标轴标签与纯净刻度 (去定语化)
    # ---------------------------------------------------------
    ax.set_xlabel(r'延拓点数 $N$', fontsize=13.0, labelpad=10)
    ax.set_ylabel(r'烘干时长 $t_{\mathrm{dry}}\ (\mathrm{h})$', fontsize=13.0, labelpad=10)

    ax.set_xticks(x_indices)
    ax.set_xticklabels(['1', '5', '10', '20', '60'], fontsize=11.5)

    y_ticks = np.array([57.1, 57.2, 57.3, 57.4, 57.5, 57.6, 57.7])
    ax.set_yticks(y_ticks)
    ax.set_yticklabels([f'{y:.1f}' for y in y_ticks], fontsize=11.5)

    # ---------------------------------------------------------
    # 9. 右上角极简图例 (直角黑色细线边框)
    # ---------------------------------------------------------
    handles = [line_main[0], line_base, poly_fill]
    labels = [r'$t_{\mathrm{dry}}$',
              r'基准线 ($t^* = 57.44\ \mathrm{h}$)',
              r'偏差包络']

    leg = ax.legend(handles, labels, loc='upper right', fancybox=False,
                    edgecolor='black', facecolor='white', framealpha=0.98,
                    fontsize=10.0, borderpad=0.7, labelspacing=0.5)
    leg.get_frame().set_linewidth(0.9)

    # ---------------------------------------------------------
    # 10. 保存图件至指定目录 (统一输出 300 DPI 超清 PNG 格式)
    # ---------------------------------------------------------
    out_png_eda = OUT_DIR_LOCAL / 'fig_q3_tail_sensitivity.png'
    out_png_tex = FIG_DIR_TEX / 'fig_q3_tail_sensitivity.png'

    for p in [out_png_eda, out_png_tex]:
        fig.savefig(p, dpi=300, bbox_inches='tight')
        print(f'[√] 已保存高清 PNG: {p}')

    plt.close(fig)
    print('>>> [SUCCESS] fig_q3_tail_sensitivity 高清 PNG 绘制完成！')


if __name__ == '__main__':
    main()
