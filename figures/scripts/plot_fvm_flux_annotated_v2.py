"""
================================================================================
2026 全国大学生数学建模竞赛 (CUMCM) A 题 - 核心机理分析示意图
【有限体积法 (FVM) 五环控制体热通量与传热矢量拓扑图】
--------------------------------------------------------------------------------
图件输出: fvm_flux_annotated_v2.png
几何底图: Archive/images/fvm_flux_flared_c2_refined.png
设计规范:
  1. 3D 柱坐标五环结构（母环/中心单元 (i,j)、内环 (i-1,j)、外环 (i+1,j)、远环 (i,j+1)、近环 (i,j-1)）
  2. 方案4视场与排版: 整体放大 18% 并向左上方平移微调，画幅饱满，视觉重心平衡
  3. 四向热通量矢量箭头: 标准科研正红，采用平滑喇叭口 (Flared) 空间渐变造型，反映实际传热物理场
  4. 严谨工程制图尺寸标注:
     - Δr: 近环底部边界共线虚线引出，双向尺寸箭头标注
     - Δz: 外环前截面上下棱线 100% 共线虚线引出，双向尺寸箭头严格平行于最外轮廓棱线
  5. 左下角柱坐标系: +z 竖直向上，+r 扇形面沿透视角延展
================================================================================
"""

import os
import sys
import argparse
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PIL import Image

# -------------------------------------------------------------------------
# 1. 路径自动解析与底图加载
# -------------------------------------------------------------------------
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

# 兼容当前目录及从 scripts/ 或项目根目录调用
if os.path.basename(CURRENT_DIR) == "scripts":
    EDA_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
elif os.path.basename(CURRENT_DIR) == "eda_figures":
    EDA_DIR = CURRENT_DIR
else:
    EDA_DIR = os.path.abspath(os.path.join(CURRENT_DIR, "eda_figures"))

# 寻找 3D 渲染底图 (fvm_flux_flared_c2_refined.png)
base_candidates = [
    os.path.join(EDA_DIR, "Archive", "images", "fvm_flux_flared_c2_refined.png"),
    os.path.join(EDA_DIR, "Archive", "fvm_flux_flared_c2_refined.png"),
    os.path.join(EDA_DIR, "fvm_flux_flared_c2_refined.png"),
    os.path.join(CURRENT_DIR, "Archive", "images", "fvm_flux_flared_c2_refined.png"),
]

base_path = None
for candidate in base_candidates:
    if os.path.exists(candidate):
        base_path = candidate
        break

if base_path is None:
    raise FileNotFoundError(
        f"未找到 3D 线稿底图 'fvm_flux_flared_c2_refined.png'。\n"
        f"请确保该底图位于 Archive/images/ 目录下。\n"
        f"检索路径列表: {base_candidates}"
    )

base_img = Image.open(base_path)
W, H = base_img.size
C = np.array([W / 2.0, H / 2.0])

# -------------------------------------------------------------------------
# 2. 方案4几何变换参数 (放大 18%，左上微调居中)
# -------------------------------------------------------------------------
S = 1.18
shift = np.array([-95.0, -155.0])

def tf(p):
    """画布变换函数: 缩放 S 并加上平移偏置 shift"""
    return C + (p - C) * S + shift

# -------------------------------------------------------------------------
# 3. 基础几何特征提取坐标 (基于原底图尺寸像素)
# -------------------------------------------------------------------------
# 近环底面两角点与边界棱线单位切向向量
bi_base = np.array([787.0, 1694.0])
bo_base = np.array([1068.0, 1790.0])
v_left_base = np.array([0.00493, 1.0]) / np.sqrt(1.0 + 0.00493**2)
v_right_base = np.array([0.00307, 1.0]) / np.sqrt(1.0 + 0.00307**2)

# 外环前截面右侧上下角点与棱线斜率向量
TR_base = np.array([1516.93, 1070.43])
BR_base = np.array([1504.89, 1463.82])
u_top_base = np.array([1.0, 0.17293]) / np.sqrt(1.0 + 0.17293**2)
u_bot_base = np.array([1.0, 0.22093]) / np.sqrt(1.0 + 0.22093**2)

# 外环最外侧轮廓竖直棱向量 (TR -> BR)
v_edge_base = (BR_base - TR_base) / np.linalg.norm(BR_base - TR_base)

# -------------------------------------------------------------------------
# 4. 四个热通量 Q 字母精确位置 (经过多轮微调定稿)
# -------------------------------------------------------------------------
q_N = np.array([806.24, 542.54])   # Qi, j+1/2 (上方，向内热流)
q_S = np.array([805.65, 1441.69])  # Qi, j-1/2 (下方，向外热流)
q_W = np.array([409.64, 924.66])   # Qi-1/2, j (左方，向外热流)
q_E = np.array([1304.14, 1087.61]) # Qi+1/2, j (右方，向内热流)

# -------------------------------------------------------------------------
# 5. 核心制图与标注渲染主函数
# -------------------------------------------------------------------------
def render_figure(output_path, show_grid=False):
    """
    渲染最终矢量化图件并保存为 300 DPI 出版级 PNG
    """
    plt.rcParams['mathtext.fontset'] = 'cm'
    plt.rcParams['font.serif'] = ['Times New Roman', 'DejaVu Serif']
    plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'DejaVu Sans']

    fig, ax = plt.subplots(figsize=(10, 10), dpi=300)

    # 绘制底图并施加几何变换
    tl_corner = tf(np.array([0.0, 0.0]))
    br_corner = tf(np.array([float(W), float(H)]))
    extent = [tl_corner[0], br_corner[0], br_corner[1], tl_corner[1]]

    ax.imshow(base_img, extent=extent, interpolation='bilinear')
    ax.set_xlim(0, W)
    ax.set_ylim(H, 0)

    # --- (A) 近环 Δr 标注 ---
    bi = tf(bi_base)
    bo = tf(bo_base)
    v_l = v_left_base
    v_r = v_right_base

    d_off_r = 52.0 * S
    L_ext_r = d_off_r + 26.0 * S

    # 严谨共线延长虚线
    ax.plot([bi[0], bi[0] + L_ext_r * v_l[0]], [bi[1], bi[1] + L_ext_r * v_l[1]],
            color='#333333', linestyle='--', linewidth=1.3, zorder=5)
    ax.plot([bo[0], bo[0] + L_ext_r * v_r[0]], [bo[1], bo[1] + L_ext_r * v_r[1]],
            color='#333333', linestyle='--', linewidth=1.3, zorder=5)

    p_dim_r1 = bi + d_off_r * v_l
    p_dim_r2 = bo + d_off_r * v_r

    # 双向尺寸箭头
    ax.annotate('', xy=p_dim_r1, xytext=p_dim_r2,
                arrowprops=dict(arrowstyle='<->', color='#000000', lw=1.6, shrinkA=0, shrinkB=0), zorder=6)

    dim_mid_r = (p_dim_r1 + p_dim_r2) / 2.0
    ax.text(dim_mid_r[0], max(bi[1], bo[1]) + L_ext_r + 28, r'$\Delta r$',
            fontsize=18 * S, fontweight='bold', color='#000000', ha='center', va='top', zorder=7)

    # --- (B) 外环 Δz 标注 ---
    TR = tf(TR_base)
    BR = tf(BR_base)
    u_t = u_top_base
    u_b = u_bot_base
    v_edge = (BR - TR) / np.linalg.norm(BR - TR)

    d_off_z = 56.0 * S
    p_top_dim = TR + d_off_z * u_t

    # 几何解析求解: 确保双向箭头严格平行于最外轮廓棱向量 v_edge
    A_mat = np.column_stack([u_b, -v_edge])
    t_val, _ = np.linalg.solve(A_mat, p_top_dim - BR)
    p_bot_dim = BR + t_val * u_b

    L_ext_top = d_off_z + 24.0 * S
    L_ext_bot = t_val + 24.0 * S

    # 严谨共线延长虚线
    ax.plot([TR[0], TR[0] + L_ext_top * u_t[0]], [TR[1], TR[1] + L_ext_top * u_t[1]],
            color='#333333', linestyle='--', linewidth=1.3, zorder=5)
    ax.plot([BR[0], BR[0] + L_ext_bot * u_b[0]], [BR[1], BR[1] + L_ext_bot * u_b[1]],
            color='#333333', linestyle='--', linewidth=1.3, zorder=5)

    # 严格平行的双向尺寸箭头
    ax.annotate('', xy=p_top_dim, xytext=p_bot_dim,
                arrowprops=dict(arrowstyle='<->', color='#000000', lw=1.6, shrinkA=0, shrinkB=0), zorder=6)

    p_mid_z = (p_top_dim + p_bot_dim) / 2.0
    ax.text(p_mid_z[0] + 16, p_mid_z[1], r'$\Delta z$',
            fontsize=18 * S, fontweight='bold', color='#000000', ha='left', va='center', zorder=7)

    # --- (C) 四个热通量 Q 字母标注 ---
    c_red = '#E01010'
    fsize = 16.5 * S

    ax.text(q_N[0], q_N[1], r'$Q_{i,\, j+1/2}$', fontsize=fsize, color=c_red, fontweight='bold', ha='center', va='center', zorder=8)
    ax.text(q_S[0], q_S[1], r'$Q_{i,\, j-1/2}$', fontsize=fsize, color=c_red, fontweight='bold', ha='center', va='center', zorder=8)
    ax.text(q_W[0], q_W[1], r'$Q_{i-1/2,\, j}$', fontsize=fsize, color=c_red, fontweight='bold', ha='center', va='center', zorder=8)
    ax.text(q_E[0], q_E[1], r'$Q_{i+1/2,\, j}$', fontsize=fsize, color=c_red, fontweight='bold', ha='center', va='center', zorder=8)

    # --- (D) 左下角柱坐标系 (+z 与扇形面 +r) ---
    orig = np.array([160.0, H - 160.0])
    z_top = orig + np.array([0, -180.0])
    ax.annotate('', xy=z_top, xytext=orig,
                arrowprops=dict(arrowstyle='->', color='#000000', lw=2.2, mutation_scale=18), zorder=6)
    ax.text(z_top[0], z_top[1] - 15, r'$+z$', fontsize=20, fontweight='bold', color='#000000', ha='center', va='bottom')

    r_len = 155.0
    ray1 = orig + np.array([r_len * np.cos(np.radians(20)), r_len * np.sin(np.radians(20)) * 0.48])
    theta_angles = np.linspace(np.radians(-28), np.radians(20), 50)
    arc_pts_x = orig[0] + r_len * np.cos(theta_angles)
    arc_pts_y = orig[1] + r_len * np.sin(theta_angles) * 0.48
    sector_poly_x = [orig[0]] + list(arc_pts_x) + [orig[0]]
    sector_poly_y = [orig[1]] + list(arc_pts_y) + [orig[1]]
    ax.fill(sector_poly_x, sector_poly_y, color='#EBF3FB', alpha=0.85, zorder=4)
    ax.plot(sector_poly_x, sector_poly_y, color='#3B6077', linewidth=1.4, zorder=5)

    ax.annotate('', xy=ray1, xytext=orig,
                arrowprops=dict(arrowstyle='->', color='#000000', lw=2.0, mutation_scale=16), zorder=6)
    ax.text(ray1[0] + 16, ray1[1] + 6, r'$+r$', fontsize=20, fontweight='bold', color='#000000', ha='left', va='center')

    # 可选参考网格
    if show_grid:
        ax.axis('on')
        ax.set_xticks(np.arange(0, W + 1, 100))
        ax.set_yticks(np.arange(0, H + 1, 100))
        ax.set_xticks(np.arange(0, W + 1, 50), minor=True)
        ax.set_yticks(np.arange(0, H + 1, 50), minor=True)
        ax.grid(which='major', color='#3498DB', linestyle='-', linewidth=0.75, alpha=0.45)
        ax.grid(which='minor', color='#85C1E9', linestyle=':', linewidth=0.5, alpha=0.35)
        ax.tick_params(axis='both', which='major', labelsize=8, colors='#2C3E50')
    else:
        ax.axis('off')

    fig.savefig(output_path, dpi=300, bbox_inches='tight', pad_inches=0.04)
    plt.close(fig)
    print(f"[Success] 成功生成高清图件 -> {output_path}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="绘制 FVM 五环传热通量示意图")
    parser.add_argument('--grid', action='store_true', help="是否同时输出带坐标参考网格的版本")
    parser.add_argument('--output', type=str, default=None, help="自定义输出图件路径")
    args = parser.parse_args()

    archive_dir = os.path.join(EDA_DIR, "Archive", "images")
    os.makedirs(archive_dir, exist_ok=True)
    out_file = args.output or os.path.join(archive_dir, "fvm_flux_annotated_v2.png")
    render_figure(out_file, show_grid=False)

    if args.grid:
        grid_out = os.path.splitext(out_file)[0] + "_grid.png"
        render_figure(grid_out, show_grid=True)
