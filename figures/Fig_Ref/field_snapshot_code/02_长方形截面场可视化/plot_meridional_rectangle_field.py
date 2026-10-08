#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
中药材烘干过程 - 轴对称子午面（长方形截面）场分布可视化
=========================================================
功能说明：
1. 取圆柱体药材的径向-轴向子午截面 [0, R] x [0, L]（长方形），将三维立体场降维至二维平面展示；
2. 严格对应长方形的四个几何与物理边界：
   - 左侧竖直边：圆柱旋转轴线 (r = 0，对称中心，绘制经典点划中心线)
   - 右侧竖直边：圆柱外侧母线 (r = R = 2.0 cm，外侧对流热质交换表面)
   - 底部水平边：截面基准面 (z = 0，底面边界)
   - 顶部水平边：圆柱上顶面 (z = L = 12.5 cm，顶端对流热质交换表面)
3. 支持温度场 (T) 与含水率场 (M) 的高清绘制，支持视觉均衡比例 (balanced) 与物理真实等比 (physical_equal)。
"""

from __future__ import annotations

import argparse
from pathlib import Path
import matplotlib as mpl
import matplotlib.patheffects as pe
import matplotlib.pyplot as plt
import numpy as np

# -----------------------------------------------------------------------------
# 全局排版美学与字体配置
# -----------------------------------------------------------------------------
mpl.rcParams.update({
    "font.sans-serif": ["Microsoft YaHei", "SimHei", "DejaVu Sans"],
    "axes.unicode_minus": False,
    "mathtext.fontset": "stix",
    "font.family": "sans-serif",
})

PRIMARY_COLOR = "#173846"
TICK_COLOR = "#233B47"
BORDER_COLOR = "#526A75"


def plot_meridional_field(
    data_path: Path | str,
    output_dir: Path | str,
    field_type: str = "temperature",
    aspect_mode: str = "balanced",
    dpi: int = 600,
) -> Path:
    """绘制子午面长方形场分布图

    Parameters
    ----------
    data_path : Path | str
        .npz 数据文件路径，包含 r_m, z_m, snapshot_times_s, temperature_snapshots, moisture_snapshots
    output_dir : Path | str
        图片输出目录
    field_type : str
        'temperature' 或 'moisture'
    aspect_mode : str
        'balanced' (利于观察径向梯度的黄金比例) 或 'physical_equal' (1:1 物理真实比例 2cm x 12.5cm)
    dpi : int
        输出图像分辨率，默认 600 DPI

    Returns
    -------
    Path : 输出文件路径
    """
    data_path = Path(data_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    data = np.load(data_path)
    r = data["r_m"] * 100.0  # 转换为 cm
    z = data["z_m"] * 100.0  # 转换为 cm
    t_val = float(data["snapshot_times_s"][0]) if "snapshot_times_s" in data else 3600.0

    R, Z = np.meshgrid(r, z, indexing="ij")
    r_max = float(r[-1])
    z_max = float(z[-1])

    # 字段配置
    if field_type.lower().startswith("t"):
        field_data = data["temperature_snapshots"][0]
        field_name = "temperature"
        cmap_name = "magma"
        cmin, cmax = 40.0, 46.0
        levels = np.linspace(cmin, cmax, 121)
        iso_levels = np.arange(40.5, 45.5, 0.5)
        iso_fmt = r"$%1.1f^\circ\mathrm{C}$"
        cb_label = r"截面温度 $T\ (^\circ\mathrm{C})$"
        cb_ticks = np.arange(40.0, 46.01, 1.0)
        cb_fmt = r"${:.1f}$"
    else:
        field_data = data["moisture_snapshots"][0]
        field_name = "moisture"
        cmap_name = "Blues"
        cmin, cmax = 0.8, 2.6
        levels = np.linspace(cmin, cmax, 121)
        iso_levels = np.arange(1.0, 2.6, 0.3)
        iso_fmt = r"$%1.1f$"
        cb_label = r"截面含水率 $(\mathrm{kg/kg})$"
        cb_ticks = np.arange(0.8, 2.61, 0.3)
        cb_fmt = r"${:.1f}$"

    # 画布与长宽比配置
    if aspect_mode == "physical_equal":
        # 物理真实比例：高宽比为 12.5 : 2 = 6.25:1
        fig, ax = plt.subplots(figsize=(4.0, 9.2), dpi=dpi, facecolor="white")
        time_x, time_y = 0.08, 0.97
        pad_cb = 0.08
    else:
        # 视觉均衡比例：放大径向梯度辨识度，长宽比协调
        fig, ax = plt.subplots(figsize=(6.0, 7.0), dpi=dpi, facecolor="white")
        time_x, time_y = 0.04, 0.95
        pad_cb = 0.06

    # 1. 连续等值云图填充
    cf = ax.contourf(R, Z, field_data, levels=levels, cmap=cmap_name, vmin=cmin, vmax=cmax)

    # 2. 离散等值线及数值标注
    cs = ax.contour(R, Z, field_data, levels=iso_levels, colors="white", linewidths=0.75, alpha=0.65)
    clabels = ax.clabel(cs, inline=True, fmt=iso_fmt, fontsize=8.5, colors="white")
    for txt in clabels:
        txt.set_path_effects([pe.withStroke(linewidth=1.2, foreground=PRIMARY_COLOR)])

    # 3. 坐标轴范围设定
    ax.set_xlim(0.0, r_max)
    ax.set_ylim(0.0, z_max)

    # 4. 主刻度标记
    r_ticks = np.linspace(0.0, r_max, 5)
    z_ticks = np.linspace(0.0, z_max, 6)
    ax.set_xticks(r_ticks)
    ax.set_xticklabels([rf"${val:g}$" for val in r_ticks])
    ax.set_yticks(z_ticks)
    ax.set_yticklabels([rf"${val:g}$" for val in z_ticks])
    ax.tick_params(axis="both", which="major", labelsize=11, colors=TICK_COLOR, length=5, width=0.8)

    # 5. 边界样式定制：左侧为对称轴点划线，其余为实线
    ax.spines["left"].set_linewidth(1.6)
    ax.spines["left"].set_color(PRIMARY_COLOR)
    ax.spines["left"].set_linestyle((0, (8, 4, 2, 4)))  # 经典工程对称中心线样式

    for s in ["right", "top", "bottom"]:
        ax.spines[s].set_linewidth(1.2)
        ax.spines[s].set_color(PRIMARY_COLOR)

    # 6. 坐标轴标签说明（仅保留横轴 r 与纵轴 z）
    ax.set_xlabel(r"$r\ (\mathrm{cm})$", fontsize=13, labelpad=8, color=PRIMARY_COLOR, fontweight="bold")
    ax.set_ylabel(r"$z\ (\mathrm{cm})$", fontsize=13, labelpad=8, color=PRIMARY_COLOR, fontweight="bold")

    if aspect_mode == "physical_equal":
        ratio = z_max / r_max
        ax.set_box_aspect(ratio)

    # 7. 色标条 (Colorbar)
    cb = fig.colorbar(cf, ax=ax, fraction=0.046, pad=pad_cb, ticks=cb_ticks)
    cb.ax.set_yticklabels([cb_fmt.format(t) for t in cb_ticks])
    cb.ax.tick_params(labelsize=10.5, colors=TICK_COLOR, length=4, width=0.8)
    cb.outline.set_linewidth(0.8)
    cb.outline.set_edgecolor(BORDER_COLOR)

    # 色标条下方正着摆放文字及单位
    if field_type.lower().startswith("t"):
        cb_subtext = "截面温度\n(°C)"
    else:
        cb_subtext = "截面含水率\n" + r"$(\mathrm{kg/kg})$"

    cb.ax.text(
        0.8, -0.06,
        cb_subtext,
        transform=cb.ax.transAxes,
        ha="center", va="top",
        fontsize=12, color=PRIMARY_COLOR, fontweight="bold",
        linespacing=1.2,
    )

    # 8. 时间戳徽标（纯数学公式）
    ax.text(
        time_x, time_y,
        rf"$t = {t_val:g}\ \mathrm{{s}}$",
        transform=ax.transAxes,
        fontsize=10.5, color="white", fontweight="bold",
        bbox=dict(boxstyle="round,pad=0.35", facecolor=PRIMARY_COLOR, alpha=0.75, edgecolor="none")
    )

    # 保存图片
    suffix = "_physical" if aspect_mode == "physical_equal" else "_balanced"
    out_filename = f"{field_name}_field_rectangle{suffix}.png"
    out_path = output_dir / out_filename
    fig.savefig(out_path, dpi=dpi, bbox_inches="tight", pad_inches=0.12)
    plt.close(fig)

    print(f"[OK] Successfully saved: {out_path}")
    return out_path


def plot_combined_panel(
    data_path: Path | str,
    output_dir: Path | str,
    dpi: int = 600,
) -> Path:
    """绘制 1x2 一体化并排长方形截面场分布图（左：含水率场，右：温度场）

    与问题一披萨图 (q1_combined_pizza) 及问题四螺旋图 (q4_combined_pizza)
    保持完全一致的一体化双联布局规范，可直接单图嵌入 LaTeX 论文正文。
    """
    import shutil

    data_path = Path(data_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    data = np.load(data_path)
    r = data["r_m"] * 100.0  # cm
    z = data["z_m"] * 100.0  # cm
    t_val = float(data["snapshot_times_s"][0]) if "snapshot_times_s" in data else 3600.0
    T = data["temperature_snapshots"][0]
    M = data["moisture_snapshots"][0]

    R, Z = np.meshgrid(r, z, indexing="ij")
    r_max = float(r[-1])
    z_max = float(z[-1])

    # 1x2 画布
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.5, 6.2), dpi=dpi, facecolor="white")

    r_ticks = np.linspace(0.0, r_max, 5)
    z_ticks = np.linspace(0.0, z_max, 6)

    # ================== 左子图：含水率场 ==================
    cmin_m, cmax_m = 0.8, 2.6
    levels_m = np.linspace(cmin_m, cmax_m, 121)
    iso_levels_m = np.arange(1.0, 2.6, 0.3)

    cf1 = ax1.contourf(R, Z, M, levels=levels_m, cmap="Blues", vmin=cmin_m, vmax=cmax_m)
    cs1 = ax1.contour(R, Z, M, levels=iso_levels_m, colors="white", linewidths=0.70, alpha=0.65)
    clabels_m = ax1.clabel(cs1, inline=True, fmt=r"$%1.1f$", fontsize=8.5, colors="white")
    for txt in clabels_m:
        txt.set_path_effects([pe.withStroke(linewidth=1.2, foreground=PRIMARY_COLOR)])

    ax1.set_xlim(0.0, r_max)
    ax1.set_ylim(0.0, z_max)
    ax1.set_xticks(r_ticks)
    ax1.set_xticklabels([rf"${val:g}$" for val in r_ticks])
    ax1.set_yticks(z_ticks)
    ax1.set_yticklabels([rf"${val:g}$" for val in z_ticks])
    ax1.tick_params(axis="both", which="major", labelsize=11, colors=TICK_COLOR, length=5, width=0.8)

    ax1.spines["left"].set_linewidth(1.6)
    ax1.spines["left"].set_color(PRIMARY_COLOR)
    ax1.spines["left"].set_linestyle((0, (8, 4, 2, 4)))
    for s in ["right", "top", "bottom"]:
        ax1.spines[s].set_linewidth(1.2)
        ax1.spines[s].set_color(PRIMARY_COLOR)

    ax1.set_xlabel(r"$r\ (\mathrm{cm})$", fontsize=13, labelpad=8, color=PRIMARY_COLOR, fontweight="bold")
    ax1.set_ylabel(r"$z\ (\mathrm{cm})$", fontsize=13, labelpad=8, color=PRIMARY_COLOR, fontweight="bold")

    cb_ticks_m = np.arange(0.8, 2.61, 0.3)
    cb1 = fig.colorbar(cf1, ax=ax1, fraction=0.046, pad=0.06, ticks=cb_ticks_m)
    cb1.ax.set_yticklabels([rf"${t:.1f}$" for t in cb_ticks_m])
    cb1.ax.tick_params(labelsize=10.5, colors=TICK_COLOR, length=4, width=0.8)
    cb1.outline.set_linewidth(0.8)
    cb1.outline.set_edgecolor(BORDER_COLOR)

    cb1.ax.text(
        0.8, -0.06,
        "截面含水率\n" + r"$(\mathrm{kg/kg})$",
        transform=cb1.ax.transAxes,
        ha="center", va="top",
        fontsize=12, color=PRIMARY_COLOR, fontweight="bold",
        linespacing=1.2,
    )

    ax1.text(
        0.04, 0.95,
        rf"$t = {t_val:g}\ \mathrm{{s}}$",
        transform=ax1.transAxes,
        fontsize=10.5, color="white", fontweight="bold",
        bbox=dict(boxstyle="round,pad=0.35", facecolor=PRIMARY_COLOR, alpha=0.75, edgecolor="none")
    )

    # ================== 右子图：温度场 ==================
    cmin_t, cmax_t = 40.0, 46.0
    levels_t = np.linspace(cmin_t, cmax_t, 121)
    iso_levels_t = np.arange(40.5, 45.5, 0.5)

    cf2 = ax2.contourf(R, Z, T, levels=levels_t, cmap="magma", vmin=cmin_t, vmax=cmax_t)
    cs2 = ax2.contour(R, Z, T, levels=iso_levels_t, colors="white", linewidths=0.70, alpha=0.45)
    ax2.clabel(cs2, inline=True, fmt=r"$%1.1f^\circ\mathrm{C}$", fontsize=8.5, colors="white")

    ax2.set_xlim(0.0, r_max)
    ax2.set_ylim(0.0, z_max)
    ax2.set_xticks(r_ticks)
    ax2.set_xticklabels([rf"${val:g}$" for val in r_ticks])
    ax2.set_yticks(z_ticks)
    ax2.set_yticklabels([rf"${val:g}$" for val in z_ticks])
    ax2.tick_params(axis="both", which="major", labelsize=11, colors=TICK_COLOR, length=5, width=0.8)

    ax2.spines["left"].set_linewidth(1.6)
    ax2.spines["left"].set_color(PRIMARY_COLOR)
    ax2.spines["left"].set_linestyle((0, (8, 4, 2, 4)))
    for s in ["right", "top", "bottom"]:
        ax2.spines[s].set_linewidth(1.2)
        ax2.spines[s].set_color(PRIMARY_COLOR)

    ax2.set_xlabel(r"$r\ (\mathrm{cm})$", fontsize=13, labelpad=8, color=PRIMARY_COLOR, fontweight="bold")
    ax2.set_ylabel(r"$z\ (\mathrm{cm})$", fontsize=13, labelpad=8, color=PRIMARY_COLOR, fontweight="bold")

    cb_ticks_t = np.arange(40.0, 46.01, 1.0)
    cb2 = fig.colorbar(cf2, ax=ax2, fraction=0.046, pad=0.06, ticks=cb_ticks_t)
    cb2.ax.set_yticklabels([rf"${t:.1f}$" for t in cb_ticks_t])
    cb2.ax.tick_params(labelsize=10.5, colors=TICK_COLOR, length=4, width=0.8)
    cb2.outline.set_linewidth(0.8)
    cb2.outline.set_edgecolor(BORDER_COLOR)

    cb2.ax.text(
        0.8, -0.06,
        "截面温度\n(°C)",
        transform=cb2.ax.transAxes,
        ha="center", va="top",
        fontsize=12, color=PRIMARY_COLOR, fontweight="bold",
        linespacing=1.2,
    )

    ax2.text(
        0.04, 0.95,
        rf"$t = {t_val:g}\ \mathrm{{s}}$",
        transform=ax2.transAxes,
        fontsize=10.5, color="white", fontweight="bold",
        bbox=dict(boxstyle="round,pad=0.35", facecolor=PRIMARY_COLOR, alpha=0.75, edgecolor="none")
    )

    plt.subplots_adjust(wspace=0.28)

    out_combined = output_dir / "q2_combined_rectangle.png"
    fig.savefig(out_combined, dpi=dpi, bbox_inches="tight", pad_inches=0.12)
    plt.close(fig)
    print(f"[OK] Successfully saved combined panel: {out_combined}")

    return out_combined


def main():
    parser = argparse.ArgumentParser(description="圆柱药材烘干轴对称截面长方形场分布绘制")
    parser.add_argument(
        "--data",
        type=str,
        default=r"d:\HIT\数模2026\eda_figures\Fig_Ref\field_snapshot_code\01_圆柱扇区场可视化\q2_solution.npz",
        help="q2_solution.npz 数据路径",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=r"d:\HIT\数模2026\eda_figures\Fig_Ref\field_snapshot_code\02_长方形截面场可视化",
        help="输出图片目录",
    )
    parser.add_argument(
        "--field",
        type=str,
        choices=["moisture", "temperature", "both"],
        default="moisture",
        help="绘制的物理场类型（默认仅绘制含水率场）",
    )
    parser.add_argument(
        "--aspect",
        type=str,
        choices=["balanced", "physical_equal", "both"],
        default="balanced",
        help="长宽比模式（默认视觉均衡比例）",
    )
    parser.add_argument("--dpi", type=int, default=600, help="输出分辨率")
    parser.add_argument("--include-combined", action="store_true", help="是否额外生成并排合图")

    args = parser.parse_args()

    fields = ["moisture", "temperature"] if args.field == "both" else [args.field]
    aspects = ["balanced", "physical_equal"] if args.aspect == "both" else [args.aspect]

    for f in fields:
        for a in aspects:
            plot_meridional_field(
                data_path=args.data,
                output_dir=args.output_dir,
                field_type=f,
                aspect_mode=a,
                dpi=args.dpi,
            )

    if args.include_combined:
        plot_combined_panel(
            data_path=args.data,
            output_dir=args.output_dir,
            dpi=args.dpi,
        )


if __name__ == "__main__":
    main()
