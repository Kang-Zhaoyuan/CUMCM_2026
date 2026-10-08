"""
环境延拓方案敏感性分析对比折线图绘制脚本
严格遵循 `eda_figures/绘图注意事项与规范指引.md` 规范：
- 中英文与公式字体：Microsoft YaHei + STIX，负号正常显示
- 刻度线朝内，主刻度 4.5pt，线宽 2.0pt
- 双子图并排排版，严禁 fig.suptitle，Caption 由论文系统承载
- 原生 raw string r'$...$'，规范 MathText 语法（\leq, \geq, 正确隔离中英文）
- 学术硬朗直角图例框 fancybox=False, edgecolor='#0F172A', framealpha=0.93
- Inset 取景框与底图曲线保持绝对净空，平滑消除离散舍入台阶
- 双轴刻度完全水平贯通对齐，避免视觉混乱
- 导出 300 DPI 高清 PNG 与无损矢量 PDF
"""

from pathlib import Path
import json
import numpy as np
import openpyxl
import matplotlib.pyplot as plt
from scipy.interpolate import PchipInterpolator
from mpl_toolkits.axes_grid1.inset_locator import inset_axes, mark_inset

# -------------------------------------------------------------
# 1. 基础环境与学术排版参数配置
# -------------------------------------------------------------
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['mathtext.fontset'] = 'stix'
plt.rcParams['xtick.direction'] = 'in'
plt.rcParams['ytick.direction'] = 'in'
plt.rcParams['xtick.major.size'] = 4.5
plt.rcParams['ytick.major.size'] = 4.5
plt.rcParams['lines.linewidth'] = 2.0

# 路径定义
PROJECT_ROOT = Path(__file__).resolve().parent.parent
RESULT_DIR = PROJECT_ROOT / 'final' / '对照实验结果' / '问题3'
FIG_DIR_EDA = PROJECT_ROOT / 'eda_figures'
FIG_DIR_TEX = PROJECT_ROOT / 'CUMCM_LaTeX_Structure_Template' / 'figures'

FIG_DIR_EDA.mkdir(parents=True, exist_ok=True)
FIG_DIR_TEX.mkdir(parents=True, exist_ok=True)

# -------------------------------------------------------------
# 2. 读取 5 组 tail 延拓对照实验数据
# -------------------------------------------------------------
tails = [1, 5, 10, 20, 60]
data = {}

for t in tails:
    xlsx_files = list(RESULT_DIR.glob(f'*tail{t}_*.xlsx'))
    log_files = list(RESULT_DIR.glob(f'*tail{t}_*.log'))
    if not xlsx_files or not log_files:
        raise FileNotFoundError(f"未找到 tail={t} 的结果或日志文件！")
    
    # 读取 Excel 时序数据 (第 1 列为时间 s, 第 2 列为中心 r=0 含水率)
    wb = openpyxl.load_workbook(xlsx_files[0], read_only=True, data_only=True)
    rows = list(wb.active.iter_rows(values_only=True))
    wb.close()
    arr = np.array(rows[1:], dtype=float)
    t_h = arr[:, 0] / 3600.0
    c_center = arr[:, 1]
    
    # 解析 log 获取高精度烘干时间和延拓边界值
    with open(log_files[0], 'r', encoding='utf-8') as f:
        lines = [l for l in f.readlines() if not l.startswith(('运行', 'Excel', 't=', '第3问', '烘干'))]
        log_data = json.loads(''.join(lines))
    
    dry_s = float(log_data['dry_time_s'])
    dry_h = dry_s / 3600.0
    env_t = float(log_data['tail'][0])
    env_c = float(log_data['tail'][1])
    
    # 为消除 Excel 保存时 4 位小数四舍五入带来的微小离散阶梯，
    # 在最后逼近达标段 (56.0h ~ 终点) 构建保形单调平滑插值供 Inset 放大使用
    mask = (t_h >= 55.5) & (t_h <= dry_h)
    t_sub = t_h[mask]
    c_sub = c_center[mask]
    diff_idx = np.where(np.diff(c_sub) != 0)[0]
    
    if len(diff_idx) > 2:
        t_nodes = np.r_[t_sub[0], (t_sub[diff_idx] + t_sub[diff_idx+1]) / 2.0, dry_h]
        c_nodes = np.r_[c_sub[0], c_sub[diff_idx+1], 0.150000]
        pchip = PchipInterpolator(t_nodes, c_nodes)
        t_fine = np.linspace(56.8, dry_h, 300)
        c_fine = pchip(t_fine)
    else:
        t_fine = np.linspace(56.8, dry_h, 100)
        c_fine = np.linspace(c_sub[0], 0.150000, 100)
    
    data[t] = {
        't_h': t_h,
        'c_center': c_center,
        't_fine': t_fine,
        'c_fine': c_fine,
        'dry_s': dry_s,
        'dry_h': dry_h,
        'env_t': env_t,
        'env_c': env_c
    }

base_dry_h = data[20]['dry_h']

# -------------------------------------------------------------
# 3. 语义调色板与样式映射 (严格执行中英文隔离，避免 MathText 汉字乱码)
# -------------------------------------------------------------
style_map = {
    1:  {'color': '#D35400', 'ls': '-.', 'lw': 1.8, 'marker': 's', 'label': r'$N=1$' + ' (57.17 h)'},
    5:  {'color': '#8E44AD', 'ls': '--', 'lw': 1.8, 'marker': '^', 'label': r'$N=5$' + ' (57.52 h)'},
    10: {'color': '#2980B9', 'ls': ':',  'lw': 2.0, 'marker': 'v', 'label': r'$N=10$' + ' (57.38 h)'},
    20: {'color': '#C0392B', 'ls': '-',  'lw': 2.5, 'marker': 'o', 'label': r'$N=20$' + ' (正式基准, 57.44 h)'},
    60: {'color': '#2C3E50', 'ls': (0, (3, 1, 1, 1)), 'lw': 1.8, 'marker': 'D', 'label': r'$N=60$' + ' (57.48 h)'}
}

# -------------------------------------------------------------
# 4. 创建双子图排版画布 (1 x 2)
# -------------------------------------------------------------
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14.2, 5.5), gridspec_kw={'wspace': 0.28})

# =============================================================
# 子图 (a): 中心含水率衰减曲线与达标判定 (全景 + 绝对净空局部放大)
# =============================================================
ax1.set_title(r'(a) 不同延拓窗口下中心含水率衰减与达标判定', fontsize=13.0, fontweight='bold', pad=12)
ax1.set_xlabel(r'时间 $t\ (\mathrm{h})$', fontsize=11.5, fontweight='bold')
ax1.set_ylabel(r'药材中心含水率 $C_{\mathrm{center}}\ (\mathrm{kg/kg})$', fontsize=11.5, fontweight='bold')

# 绘制全周期宏观曲线
for t in tails:
    st = style_map[t]
    ax1.plot(data[t]['t_h'], data[t]['c_center'], 
             color=st['color'], linestyle=st['ls'], linewidth=st['lw'], 
             label=st['label'], alpha=0.92)

# 达标阈值线 C = 0.15 kg/kg
ax1.axhline(0.15, color='#27AE60', linestyle='--', linewidth=1.6, alpha=0.95,
            label=r'达标阈值 $C \leq 0.15\ \mathrm{kg/kg}$')

ax1.set_xlim(0, 62)
ax1.set_ylim(0, 2.70)
ax1.grid(True, linestyle='--', alpha=0.5)

# 直角方框图例
leg1 = ax1.legend(loc='upper right', fancybox=False, edgecolor='#0F172A',
                  facecolor='white', framealpha=0.95, fontsize=9.5)
leg1.get_frame().set_linewidth(0.8)

# -------------------------------------------------------------
# 子图 (a) 内嵌局部放大镜 (Zoom Inset) 
# 位置布局遵循 5.10 绝对净空法则：
# 放置在 x in [22, 52] h, y in [0.65, 1.85] 的中空无数据区，绝对不与底图相撞
# -------------------------------------------------------------
ax_ins = inset_axes(ax1, width="48%", height="42%", loc='lower left',
                    bbox_to_anchor=(0.28, 0.25, 0.9, 0.9), bbox_transform=ax1.transAxes)

for t in tails:
    st = style_map[t]
    # 绘制高精度平滑时序曲线
    ax_ins.plot(data[t]['t_fine'], data[t]['c_fine'],
                color=st['color'], linestyle=st['ls'], linewidth=st['lw'], alpha=0.95)
    # 标出终点交点 (dry_h, 0.1500)
    ax_ins.plot(data[t]['dry_h'], 0.1500, marker=st['marker'], markersize=6.0,
                color=st['color'], markeredgecolor='#0F172A', markeredgewidth=0.8, zorder=5)

# 阈值线
ax_ins.axhline(0.1500, color='#27AE60', linestyle='--', linewidth=1.4, alpha=0.95)

# 设置 Inset 坐标范围与刻度
ax_ins.set_xlim(57.05, 57.60)
ax_ins.set_ylim(0.1497, 0.1508)
ax_ins.set_xticks([57.1, 57.2, 57.3, 57.4, 57.5, 57.6])
ax_ins.set_xticklabels(['57.1', '57.2', '57.3', '57.4', '57.5', '57.6'], fontsize=8.5)
ax_ins.set_yticks([0.1500, 0.1505])
ax_ins.set_yticklabels(['0.1500', '0.1505'], fontsize=8.5)
ax_ins.grid(True, linestyle=':', alpha=0.6)
ax_ins.set_title('达标临界区间局部放大 ' + r'($C \rightarrow 0.15$)', fontsize=9.2, fontweight='bold', pad=4)

# 取景框指示线：柔和微导引
mark_inset(ax1, ax_ins, loc1=1, loc2=2, fc="none", ec="#64748B", ls=":", lw=0.9)


# =============================================================
# 子图 (b): 延拓窗口点数敏感性响应曲线 (烘干时长 vs 环境稳态温度)
# =============================================================
ax2.set_title(r'(b) 延拓点数对烘干时长与环境稳态温度的敏感性响应', fontsize=13.0, fontweight='bold', pad=12)
ax2_twin = ax2.twinx()

x_indices = np.arange(len(tails))
x_labels = [r'$N=1$' + '\n(单点)', r'$N=5$', r'$N=10$', r'$N=20$' + '\n(正式方案)', r'$N=60$']

dry_times = np.array([data[t]['dry_h'] for t in tails])
time_diffs_min = (dry_times - base_dry_h) * 60.0
env_temps = np.array([data[t]['env_t'] for t in tails])

# 刻度绝对贯通对齐 (Rule 5.5): 左右轴统一划分为 7 档规整主刻度，并预留充足顶部净空
ax2.set_ylim(57.05, 57.75)
ax2.set_yticks(np.linspace(57.10, 57.70, 7))

ax2_twin.set_ylim(49.875, 50.225)
ax2_twin.set_yticks(np.linspace(49.90, 50.20, 7))

# 基准水平参考线 (N=20)
line_base = ax2.axhline(base_dry_h, color='#C0392B', linestyle=':', linewidth=1.2, alpha=0.7,
                        label=r'基准烘干时长 ($57.44\ \mathrm{h}$)')

# N>=10 稳定收敛阴影区
span_box = ax2.axvspan(1.8, 4.2, color='#27AE60', alpha=0.10,
                       label=r'稳定收敛域 ($N \geq 10,\ |\Delta t| \leq 3.2\ \mathrm{min}$)')

# 左轴: 烘干达标时长折线 (热力红)
l1 = ax2.plot(x_indices, dry_times, color='#C0392B', linestyle='-', linewidth=2.2,
              marker='o', markersize=7.0, markerfacecolor='white', markeredgewidth=2.0,
              label=r'烘干达标时长 $t_{\mathrm{dry}}\ (\mathrm{h})$', zorder=4)

# 右轴: 延拓稳态温度折线 (沉稳海蓝)
l2 = ax2_twin.plot(x_indices, env_temps, color='#2980B9', linestyle='--', linewidth=2.0,
                   marker='s', markersize=6.5, markerfacecolor='white', markeredgewidth=1.8,
                   label=r'延拓稳态温度 $T_{\infty}\ (^\circ\mathrm{C})$', zorder=4)

# 数据标注点 Callout (全方位避让图例与边界)
for i, (t_val, diff_m, t_temp) in enumerate(zip(dry_times, time_diffs_min, env_temps)):
    if i == 0:  # N=1 单点偏差大
        ax2.annotate(f'{t_val:.2f} h\n({diff_m:+.1f} min)', xy=(i, t_val), xytext=(+14, -14),
                     textcoords='offset points', fontsize=8.8, fontweight='bold', color='#C0392B',
                     arrowprops=dict(arrowstyle='->', color='#C0392B', lw=1.0))
    elif i == 1:  # N=5
        ax2.annotate(f'{t_val:.2f} h\n({diff_m:+.1f} min)', xy=(i, t_val), xytext=(0, +10),
                     textcoords='offset points', ha='center', fontsize=8.5, color='#C0392B')
    elif i == 2:  # N=10
        ax2.annotate(f'{t_val:.2f} h\n({diff_m:+.1f} min)', xy=(i, t_val), xytext=(0, -25),
                     textcoords='offset points', ha='center', fontsize=8.5, color='#C0392B')
    elif i == 3:  # N=20 正式基准
        ax2.annotate(f'{t_val:.2f} h\n(正式基准)', xy=(i, t_val), xytext=(-28, +16),
                     textcoords='offset points', fontsize=8.8, fontweight='bold', color='#C0392B',
                     arrowprops=dict(arrowstyle='->', color='#C0392B', lw=1.0))
    elif i == 4:  # N=60：向下方标注，彻底避开右上角图例
        ax2.annotate(f'{t_val:.2f} h\n({diff_m:+.1f} min)', xy=(i, t_val), xytext=(-16, -26),
                     textcoords='offset points', ha='center', fontsize=8.5, color='#C0392B')

ax2.set_xlabel(r'4小时后环境延拓窗口点数 $N$', fontsize=11.5, fontweight='bold')
ax2.set_ylabel(r'烘干时长 $t_{\mathrm{dry}}\ (\mathrm{h})$', fontsize=11.5, fontweight='bold', color='#C0392B')
ax2_twin.set_ylabel(r'延拓稳态温度 $T_{\infty}\ (^\circ\mathrm{C})$', fontsize=11.5, fontweight='bold', color='#2980B9')

ax2.set_xticks(x_indices)
ax2.set_xticklabels(x_labels, fontsize=9.5)
ax2.tick_params(axis='y', colors='#C0392B')
ax2_twin.tick_params(axis='y', colors='#2980B9')
ax2.grid(True, linestyle='--', alpha=0.5)

# 合并单一图例 (Rule 5.2)
handles2 = [l1[0], l2[0], span_box, line_base]
labels2 = [h.get_label() for h in handles2]
leg2 = ax2.legend(handles2, labels2, loc='upper right', fancybox=False,
                  edgecolor='#0F172A', facecolor='white', framealpha=0.93,
                  fontsize=9.2, ncol=1)
leg2.get_frame().set_linewidth(0.8)

# -------------------------------------------------------------
# 5. 导出高清图件 (bbox_inches='tight')
# -------------------------------------------------------------
out_png_eda = FIG_DIR_EDA / 'fig_q3_tail_sensitivity.png'
out_pdf_eda = FIG_DIR_EDA / 'fig_q3_tail_sensitivity.pdf'
out_png_tex = FIG_DIR_TEX / 'fig_q3_tail_sensitivity.png'
out_pdf_tex = FIG_DIR_TEX / 'fig_q3_tail_sensitivity.pdf'

fig.savefig(out_png_eda, dpi=300, bbox_inches='tight')
fig.savefig(out_pdf_eda, bbox_inches='tight')
fig.savefig(out_png_tex, dpi=300, bbox_inches='tight')
fig.savefig(out_pdf_tex, bbox_inches='tight')

plt.close(fig)

print("敏感性对比图优化版生成成功！")
