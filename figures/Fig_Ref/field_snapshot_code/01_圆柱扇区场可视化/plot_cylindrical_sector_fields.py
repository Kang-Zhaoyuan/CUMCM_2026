#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""绘制二维轴对称圆柱药材场的三维扇区切片图。

数据接口
--------
1. NPZ（推荐）：包含 r_m、z_m、snapshot_times_s，以及
   temperature_snapshots / moisture_snapshots。
2. CSV / Excel 长表：包含 r_cm（或 r_m）、z_cm（或 z_m）、time_s（可选）
   和 temperature_c / moisture（或 value）列。
3. CSV / Excel 二维矩阵：首行（除 A1）为 z(cm)，首列（除 A1）为 r(cm)，
   其余单元格为场值。若 A1 含“时间”，说明它是时间-径向剖面表，程序会拒绝
   将一维剖面伪造成二维场。

示例
----
python plot_cylindrical_sector_fields.py \
  --input q2_solution.npz --time-s 3600 --field both --output-dir output

箭头表示模型通量：温度场为 -k·grad(T)，水分场为 -D·grad(C)。每个切片划分为固定的
3×2 极坐标采样网格，每个灰色网格交点发出一个箭头；长度按图内最大通量线性归一化，短箭头
表示弱、长箭头表示强。箭头不是带单位的前沿速度。默认使用仅向 z 最大端逐渐加密的 9 个
轴向切片。所有场值均来自输入文件，程序不生成或补造模拟数据。
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap, Normalize
from matplotlib.figure import Figure
from matplotlib.lines import Line2D
from matplotlib.offsetbox import AnnotationBbox, DrawingArea, HPacker, TextArea
from matplotlib.patches import FancyArrowPatch, PathPatch
from matplotlib.path import Path as MplPath
from mpl_toolkits.mplot3d import Axes3D, proj3d  # noqa: F401
from mpl_toolkits.mplot3d.art3d import Line3DCollection
from scipy.interpolate import RegularGridInterpolator


TEMPERATURE_CMAP = LinearSegmentedColormap.from_list(
    "temperature_reference",
    [
        "#09030F",
        "#281047",
        "#5B126E",
        "#941D67",
        "#CE334B",
        "#EE681F",
        "#FCA91B",
        "#FFE16A",
        "#FFF7B0",
    ],
)

MOISTURE_CMAP = LinearSegmentedColormap.from_list(
    "moisture_reference",
    [
        "#263FBA",
        "#5375D6",
        "#89A5E6",
        "#C3D0EA",
        "#EEEAE7",
        "#F3B7A4",
        "#E86F5A",
        "#C40032",
    ],
)


@dataclass(frozen=True)
class FieldData:
    r_cm: np.ndarray
    z_cm: np.ndarray
    temperature_c: np.ndarray | None
    moisture: np.ndarray | None
    time_s: float | None
    source_kind: str


@dataclass(frozen=True)
class FieldStyle:
    key: str
    title: str
    colorbar_label: str
    cmap: LinearSegmentedColormap
    decimals: int
    output_name: str


FIELD_STYLES = {
    "temperature": FieldStyle(
        key="temperature",
        title="圆柱药材内部温度场",
        colorbar_label=r"温度 $(^\circ\mathrm{C})$",
        cmap=TEMPERATURE_CMAP,
        decimals=1,
        output_name="temperature_field.png",
    ),
    "moisture": FieldStyle(
        key="moisture",
        title="圆柱药材内部含水率场",
        colorbar_label=r"含水率 $(\mathrm{kg/kg})$",
        cmap=MOISTURE_CMAP,
        decimals=2,
        output_name="moisture_field.png",
    ),
}


def configure_matplotlib() -> None:
    """设置适合中文科研图的字体和可编辑矢量文本。"""
    mpl.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": [
                "Microsoft YaHei",
                "SimHei",
                "Arial",
                "DejaVu Sans",
                "sans-serif",
            ],
            "mathtext.fontset": "stix",
            "axes.unicode_minus": False,
            "font.size": 11,
            "axes.labelsize": 12,
            "axes.titlesize": 18,
            "xtick.labelsize": 10,
            "ytick.labelsize": 10,
            "pdf.fonttype": 42,
            "svg.fonttype": "none",
            "savefig.facecolor": "white",
            "savefig.edgecolor": "white",
        }
    )


def _normalize_column(name: object) -> str:
    return str(name).strip().lower().replace(" ", "").replace("（", "(").replace("）", ")")


def _find_column(columns: Iterable[object], aliases: Iterable[str]) -> object | None:
    normalized = {_normalize_column(column): column for column in columns}
    for alias in aliases:
        key = _normalize_column(alias)
        if key in normalized:
            return normalized[key]
    return None


def _validate_field_data(data: FieldData) -> FieldData:
    r = np.asarray(data.r_cm, dtype=float)
    z = np.asarray(data.z_cm, dtype=float)
    if r.ndim != 1 or z.ndim != 1 or r.size < 2 or z.size < 2:
        raise ValueError("r 与 z 坐标必须是一维数组，且各至少含两个坐标点。")
    if not np.all(np.isfinite(r)) or not np.all(np.isfinite(z)):
        raise ValueError("r 或 z 坐标包含 NaN/无穷值。")
    if np.any(np.diff(r) <= 0.0) or np.any(np.diff(z) <= 0.0):
        raise ValueError("r 与 z 坐标必须严格递增。")
    if r[0] < -1.0e-10 or z[0] < -1.0e-10:
        raise ValueError("本绘图器要求非负的半径和半轴向坐标。")

    expected = (r.size, z.size)
    for name, field in (("temperature_c", data.temperature_c), ("moisture", data.moisture)):
        if field is None:
            continue
        array = np.asarray(field, dtype=float)
        if array.shape != expected:
            if array.T.shape == expected:
                array = array.T
            else:
                raise ValueError(f"{name} 的形状 {array.shape} 与坐标网格 {expected} 不一致。")
        if not np.all(np.isfinite(array)):
            raise ValueError(f"{name} 包含 NaN/无穷值；程序不会静默删点。")
        if name == "temperature_c":
            object.__setattr__(data, "temperature_c", array)
        else:
            object.__setattr__(data, "moisture", array)
    return data


def _interpolate_time_series(times: np.ndarray, values: np.ndarray, target: float) -> np.ndarray:
    """在线性时间轴上插值完整二维场；空间网格保持不变。"""
    times = np.asarray(times, dtype=float)
    if times.ndim != 1 or np.any(np.diff(times) <= 0.0):
        raise ValueError("时间坐标必须严格递增。")
    if target < times[0] - 1.0e-9 or target > times[-1] + 1.0e-9:
        raise ValueError(f"请求时刻 {target:g} s 超出可用范围 [{times[0]:g}, {times[-1]:g}] s。")
    exact = np.flatnonzero(np.isclose(times, target, rtol=0.0, atol=1.0e-9))
    if exact.size:
        return np.asarray(values[int(exact[0])], dtype=float)
    hi = int(np.searchsorted(times, target))
    lo = hi - 1
    weight = (target - times[lo]) / (times[hi] - times[lo])
    return (1.0 - weight) * np.asarray(values[lo], dtype=float) + weight * np.asarray(values[hi], dtype=float)


def load_npz(path: Path, time_s: float | None) -> FieldData:
    with np.load(path) as raw:
        keys = set(raw.files)
        required_coordinates = {"r_m", "z_m"}
        if not required_coordinates.issubset(keys):
            raise ValueError(f"NPZ 缺少坐标键：{sorted(required_coordinates - keys)}")
        r_cm = np.asarray(raw["r_m"], dtype=float) * 100.0
        z_cm = np.asarray(raw["z_m"], dtype=float) * 100.0

        selected_time = time_s
        temperature = None
        moisture = None
        if "snapshot_times_s" in keys:
            times = np.asarray(raw["snapshot_times_s"], dtype=float)
            if selected_time is None:
                selected_time = float(times[len(times) // 2])
            if "temperature_snapshots" in keys:
                temperature = _interpolate_time_series(times, raw["temperature_snapshots"], selected_time)
            if "moisture_snapshots" in keys:
                moisture = _interpolate_time_series(times, raw["moisture_snapshots"], selected_time)
        else:
            if time_s is not None:
                raise ValueError("该 NPZ 没有 snapshot_times_s，不能按指定时刻选取场。")
            if "temperature_final" in keys:
                temperature = np.asarray(raw["temperature_final"], dtype=float)
            if "moisture_final" in keys:
                moisture = np.asarray(raw["moisture_final"], dtype=float)

    return _validate_field_data(
        FieldData(r_cm, z_cm, temperature, moisture, selected_time, "NPZ 完整二维场")
    )


def _select_long_table_time(
    table: pd.DataFrame,
    time_column: object | None,
    target_time: float | None,
    r_column: object,
    z_column: object,
    value_column: object,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, float | None]:
    work = table[[column for column in (time_column, r_column, z_column, value_column) if column is not None]].copy()
    for column in work.columns:
        work[column] = pd.to_numeric(work[column], errors="raise")
    selected_time = None
    if time_column is None:
        chosen = work
    else:
        times = np.sort(work[time_column].unique().astype(float))
        if target_time is None:
            target_time = float(times[len(times) // 2])
        if target_time < times[0] - 1.0e-9 or target_time > times[-1] + 1.0e-9:
            raise ValueError(f"请求时刻 {target_time:g} s 超出表格时间范围。")
        selected_time = float(target_time)
        exact = times[np.isclose(times, target_time, rtol=0.0, atol=1.0e-9)]
        if exact.size:
            chosen = work[np.isclose(work[time_column], exact[0], rtol=0.0, atol=1.0e-9)]
        else:
            hi_index = int(np.searchsorted(times, target_time))
            lo_time, hi_time = float(times[hi_index - 1]), float(times[hi_index])
            lo = work[np.isclose(work[time_column], lo_time)].pivot(index=r_column, columns=z_column, values=value_column)
            hi = work[np.isclose(work[time_column], hi_time)].pivot(index=r_column, columns=z_column, values=value_column)
            if not lo.index.equals(hi.index) or not lo.columns.equals(hi.columns):
                raise ValueError("相邻时刻的 r-z 网格不一致，不能安全插值。")
            weight = (target_time - lo_time) / (hi_time - lo_time)
            matrix = (1.0 - weight) * lo.to_numpy(float) + weight * hi.to_numpy(float)
            return lo.index.to_numpy(float), lo.columns.to_numpy(float), matrix, selected_time

    if chosen.duplicated([r_column, z_column]).any():
        raise ValueError("同一时刻存在重复的 r-z 坐标，无法唯一构造二维场。")
    matrix = chosen.pivot(index=r_column, columns=z_column, values=value_column)
    if matrix.isna().any().any():
        raise ValueError("长表的 r-z 笛卡尔网格不完整；程序不会填补缺失场值。")
    return matrix.index.to_numpy(float), matrix.columns.to_numpy(float), matrix.to_numpy(float), selected_time


def _load_tabular(path: Path, field: str, time_s: float | None, sheet: str | None) -> FieldData:
    suffix = path.suffix.lower()
    if suffix in {".xlsx", ".xlsm", ".xls"}:
        if sheet is None:
            candidates = ["温度", "temperature"] if field == "temperature" else ["水分浓度", "含水率", "moisture"]
            workbook = pd.ExcelFile(path)
            sheet_lookup = {_normalize_column(name): name for name in workbook.sheet_names}
            sheet = next((sheet_lookup[_normalize_column(name)] for name in candidates if _normalize_column(name) in sheet_lookup), workbook.sheet_names[0])
        table = pd.read_excel(path, sheet_name=sheet)
        source_kind = f"Excel 工作表 {sheet}"
    elif suffix in {".csv", ".tsv"}:
        separator = "\t" if suffix == ".tsv" else ","
        table = pd.read_csv(path, sep=separator)
        source_kind = f"{suffix[1:].upper()} 表格"
    else:
        raise ValueError(f"不支持的表格扩展名：{suffix}")

    r_column = _find_column(table.columns, ["r_cm", "radius_cm", "半径(cm)", "r"])
    r_m_column = _find_column(table.columns, ["r_m", "radius_m", "半径(m)"])
    z_column = _find_column(table.columns, ["z_cm", "axial_cm", "轴向位置(cm)", "z"])
    z_m_column = _find_column(table.columns, ["z_m", "axial_m", "轴向位置(m)"])
    time_column = _find_column(table.columns, ["time_s", "time", "时间(s)", "时间"])
    value_aliases = ["temperature_c", "temperature", "温度", "value", "场值"] if field == "temperature" else ["moisture", "moisture_content", "含水率", "水分浓度", "value", "场值"]
    value_column = _find_column(table.columns, value_aliases)

    if (r_column is not None or r_m_column is not None) and (z_column is not None or z_m_column is not None) and value_column is not None:
        actual_r = r_column if r_column is not None else r_m_column
        actual_z = z_column if z_column is not None else z_m_column
        r, z, values, selected_time = _select_long_table_time(
            table, time_column, time_s, actual_r, actual_z, value_column
        )
        if r_column is None:
            r = r * 100.0
        if z_column is None:
            z = z * 100.0
    else:
        raw = pd.read_excel(path, sheet_name=sheet, header=None) if suffix in {".xlsx", ".xlsm", ".xls"} else pd.read_csv(path, sep=("\t" if suffix == ".tsv" else ","), header=None)
        top_left = _normalize_column(raw.iloc[0, 0])
        if "时间" in top_left or "time" in top_left:
            raise ValueError(
                "检测到时间-径向一维剖面表。它没有 z 坐标，不能恢复二维 r-z 场；请改用完整 NPZ 或二维长表/矩阵。"
            )
        r = pd.to_numeric(raw.iloc[1:, 0], errors="raise").to_numpy(float)
        z = pd.to_numeric(raw.iloc[0, 1:], errors="raise").to_numpy(float)
        values = raw.iloc[1:, 1:].apply(pd.to_numeric, errors="raise").to_numpy(float)
        selected_time = time_s
        source_kind += "（二维矩阵）"

    temperature = values if field == "temperature" else None
    moisture = values if field == "moisture" else None
    return _validate_field_data(FieldData(r, z, temperature, moisture, selected_time, source_kind))


def load_field_data(path: Path, field: str, time_s: float | None, sheet: str | None) -> FieldData:
    if path.suffix.lower() == ".npz":
        return load_npz(path, time_s)
    return _load_tabular(path, field, time_s, sheet)


def q2_transport_coefficients(temperature_c: np.ndarray, moisture: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """返回冻结 Q2/Q3 模型中的导热系数 k 与水分扩散系数 D。"""
    if np.any(moisture <= 0.0) or np.any(temperature_c <= -273.15):
        raise ValueError("场值超出 Q2/Q3 物性公式的定义域。")
    conductivity = 0.21 + 0.38 * moisture / (moisture + 1.0)
    temperature_k = temperature_c + 273.15
    diffusivity = 2.4e-3 * np.exp(-0.45 / moisture - 3850.0 / temperature_k)
    return conductivity, diffusivity


def calculate_flux(
    field: np.ndarray,
    r_cm: np.ndarray,
    z_cm: np.ndarray,
    kind: str,
    temperature_c: np.ndarray | None,
    moisture: np.ndarray | None,
    coefficient_mode: str,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, str]:
    """计算 r-z 平面内的通量分量及其模。"""
    r_m = np.asarray(r_cm) / 100.0
    z_m = np.asarray(z_cm) / 100.0
    grad_r, grad_z = np.gradient(field, r_m, z_m, edge_order=2)

    coefficient = np.ones_like(field)
    semantics = "负梯度代理"
    if coefficient_mode == "q2":
        if temperature_c is None or moisture is None:
            raise ValueError(
                "coefficient-mode=q2 需要同一数据源同时提供 temperature 与 moisture；"
                "若只有单场数据，请改用 --coefficient-mode gradient。"
            )
        conductivity, diffusivity = q2_transport_coefficients(temperature_c, moisture)
        coefficient = conductivity if kind == "temperature" else diffusivity
        semantics = r"$-k\nabla T$ 模型热通量" if kind == "temperature" else r"$-D\nabla C$ 模型水分通量"
    elif coefficient_mode not in {"gradient", "q2"}:
        raise ValueError(f"未知 coefficient_mode：{coefficient_mode}")

    flux_r = -coefficient * grad_r
    flux_z = -coefficient * grad_z
    magnitude = np.hypot(flux_r, flux_z)
    return flux_r, flux_z, magnitude, semantics


def _interpolate_column(field: np.ndarray, z_cm: np.ndarray, target_z: float) -> np.ndarray:
    if target_z < z_cm[0] - 1.0e-9 or target_z > z_cm[-1] + 1.0e-9:
        raise ValueError(f"切片 z={target_z:g} cm 超出坐标范围。")
    if np.any(np.diff(z_cm) <= 0.0):
        raise ValueError("z 坐标必须严格递增，才能进行切片插值。")
    exact = np.flatnonzero(np.isclose(z_cm, target_z, rtol=0.0, atol=1.0e-9))
    if exact.size:
        return field[:, int(exact[0])]
    hi = int(np.searchsorted(z_cm, target_z))
    lo = hi - 1
    weight = (target_z - z_cm[lo]) / (z_cm[hi] - z_cm[lo])
    return (1.0 - weight) * field[:, lo] + weight * field[:, hi]


def _create_arrow_head_3d(
    start_pt: np.ndarray,
    end_pt: np.ndarray,
    head_len: float = 0.08,
    head_angle: float = 0.38,
) -> list[list[np.ndarray]]:
    """为三维矢量末端生成双倒刺箭羽线段（3D Needle-Tip Arrowhead）。"""
    vec = end_pt - start_pt
    v_norm = float(np.linalg.norm(vec))
    if v_norm < 1e-8:
        return []
    u = vec / v_norm
    if abs(u[2]) < 0.9:
        perp = np.cross(u, np.array([0.0, 0.0, 1.0]))
    else:
        perp = np.cross(u, np.array([0.0, 1.0, 0.0]))
    perp /= np.linalg.norm(perp)

    cos_a = np.cos(head_angle)
    sin_a = np.sin(head_angle)
    b1_dir = -cos_a * u + sin_a * perp
    b2_dir = -cos_a * u - sin_a * perp

    p_b1 = end_pt + head_len * b1_dir
    p_b2 = end_pt + head_len * b2_dir
    return [[end_pt, p_b1], [end_pt, p_b2]]


def _render_dense_volume_vectors(
    ax: Axes3D,
    r_cm: np.ndarray,
    z_cm: np.ndarray,
    flux_r: np.ndarray,
    flux_z: np.ndarray,
    magnitude: np.ndarray,
    half_angle_rad: float,
    arrow_color: str = "auto",
) -> int:
    """在全域三维圆柱空间（包括切片面与层间过渡区共 16 层）生成自适应高密梯度矢量场。

    每个矢量由轴线段与 3D 箭羽组成，独立作为 Line3DCollection 挂载至坐标轴，
    完全依托 computed_zorder=True 实现与各个圆盘切片的绝对平等双向透视遮挡。
    """
    valid_mag = magnitude[np.isfinite(magnitude)]
    if valid_mag.size == 0 or float(np.max(valid_mag)) <= np.finfo(float).tiny:
        return 0

    mag_min = float(np.min(valid_mag))
    mag_max = float(np.max(valid_mag))
    mag_span = max(mag_max - mag_min, 1e-12)

    interp_Fr = RegularGridInterpolator((r_cm, z_cm), flux_r, bounds_error=False, fill_value=0.0)
    interp_Fz = RegularGridInterpolator((r_cm, z_cm), flux_z, bounds_error=False, fill_value=0.0)
    interp_mag = RegularGridInterpolator((r_cm, z_cm), magnitude, bounds_error=False, fill_value=0.0)

    r_max = float(r_cm[-1])
    z_max = float(z_cm[-1])
    eval_z = np.linspace(0.2, z_max - 0.2, 16)

    candidates_spec = [
        (0.25 * r_max, [0.0]),
        (0.55 * r_max, [-0.30 * half_angle_rad, 0.30 * half_angle_rad]),
        (0.82 * r_max, [-0.36 * half_angle_rad, 0.0, 0.36 * half_angle_rad]),
        (0.98 * r_max, [-0.42 * half_angle_rad, -0.14 * half_angle_rad, 0.14 * half_angle_rad, 0.42 * half_angle_rad]),
    ]

    use_custom_color = (arrow_color not in ("auto", "black", "#000000"))
    if use_custom_color:
        base_rgba = mpl.colors.to_rgba(arrow_color)

    arrow_count = 0
    for ez in eval_z:
        for radial_pos, angles in candidates_spec:
            fr = float(interp_Fr((radial_pos, ez)))
            fz = float(interp_Fz((radial_pos, ez)))
            loc_mag = float(interp_mag((radial_pos, ez)))
            loc_norm = float(np.hypot(fr, fz))
            if loc_norm <= np.finfo(float).tiny:
                continue

            radial_dir = fr / loc_norm
            axial_dir = fz / loc_norm

            norm_str = float(np.clip((loc_mag - mag_min) / mag_span, 0.0, 1.0))
            strength = norm_str ** 0.6

            arrow_len = 0.10 + 0.16 * strength
            end_r = radial_pos + radial_dir * arrow_len
            end_z = ez + axial_dir * arrow_len

            lw = 0.55 + 0.85 * strength

            if use_custom_color:
                c_rgba = (base_rgba[0], base_rgba[1], base_rgba[2], 0.45 + 0.55 * strength)
            else:
                gray_level = 0.45 * (1.0 - strength) + 0.05 * strength
                alpha = 0.45 + 0.55 * strength
                c_rgba = (gray_level, gray_level, gray_level + 0.03 * (1.0 - strength), alpha)

            head_len = 0.06 + 0.04 * strength
            for angle in angles:
                sx = radial_pos * np.cos(angle)
                sy = radial_pos * np.sin(angle)
                ex = end_r * np.cos(angle)
                ey = end_r * np.sin(angle)
                start_p = np.array([sx, sy, ez])
                end_p = np.array([ex, ey, end_z])

                segs = [[start_p, end_p]]
                for head_seg in _create_arrow_head_3d(start_p, end_p, head_len=head_len, head_angle=0.38):
                    segs.append(head_seg)

                lc = Line3DCollection(segs, colors=[c_rgba] * len(segs), linewidths=[lw] * len(segs))
                ax.add_collection(lc)
                arrow_count += 1

    return arrow_count


def _trace_streamline_rk2(
    r_grid: np.ndarray,
    z_grid: np.ndarray,
    vr_grid: np.ndarray,
    vz_grid: np.ndarray,
    start_r: float,
    start_z: float,
    ds: float = 0.035,
    max_steps: int = 180,
    forward: bool = True,
) -> tuple[np.ndarray, np.ndarray]:
    """在 (r, z) 平面上进行二阶 Runge-Kutta 梯度通量流线积分追踪。"""
    interp_vr = RegularGridInterpolator((r_grid, z_grid), vr_grid, bounds_error=False, fill_value=0.0)
    interp_vz = RegularGridInterpolator((r_grid, z_grid), vz_grid, bounds_error=False, fill_value=0.0)

    r_pts = [start_r]
    z_pts = [start_z]
    cur_r, cur_z = start_r, start_z
    sign = 1.0 if forward else -1.0
    r_min, r_max = r_grid[0], r_grid[-1]
    z_min, z_max = z_grid[0], z_grid[-1]

    for _ in range(max_steps):
        vr = float(interp_vr((cur_r, cur_z)))
        vz = float(interp_vz((cur_r, cur_z)))
        norm = np.hypot(vr, vz)
        if norm < 1e-7:
            break
        dr = sign * (vr / norm) * ds
        dz = sign * (vz / norm) * ds

        mid_r = cur_r + 0.5 * dr
        mid_z = cur_z + 0.5 * dz
        if not (r_min <= mid_r <= r_max and z_min <= mid_z <= z_max):
            break
        vr_m = float(interp_vr((mid_r, mid_z)))
        vz_m = float(interp_vz((mid_r, mid_z)))
        norm_m = np.hypot(vr_m, vz_m)
        if norm_m < 1e-7:
            break
        cur_r += sign * (vr_m / norm_m) * ds
        cur_z += sign * (vz_m / norm_m) * ds

        if not (r_min <= cur_r <= r_max and z_min <= cur_z <= z_max):
            cur_r = np.clip(cur_r, r_min, r_max)
            cur_z = np.clip(cur_z, z_min, z_max)
            r_pts.append(cur_r)
            z_pts.append(cur_z)
            break
        r_pts.append(cur_r)
        z_pts.append(cur_z)

    return np.array(r_pts), np.array(z_pts)


def _render_streamlines_field(
    ax: Axes3D,
    r_cm: np.ndarray,
    z_cm: np.ndarray,
    flux_r: np.ndarray,
    flux_z: np.ndarray,
    magnitude: np.ndarray,
    half_angle_rad: float,
    kind: str,
) -> int:
    """构建具有连续线宽渐变与三维箭头导引的流体力学流线型梯度场。"""
    mag_min = float(np.min(magnitude))
    mag_max = float(np.max(magnitude))
    mag_span = max(mag_max - mag_min, 1e-12)

    interp_mag = RegularGridInterpolator((r_cm, z_cm), magnitude, bounds_error=False, fill_value=0.0)
    theta_planes = [-0.35 * half_angle_rad, 0.0, 0.35 * half_angle_rad]

    if kind == "moisture":
        seeds = [
            (0.20, 1.2), (0.20, 3.5), (0.20, 6.0), (0.20, 8.5), (0.20, 10.5),
            (0.65, 1.5), (0.65, 4.5), (0.65, 7.5), (0.65, 10.5),
            (1.15, 2.0), (1.15, 5.5), (1.15, 8.5), (1.15, 11.2),
            (1.60, 2.5), (1.60, 6.5), (1.60, 10.0), (1.60, 11.8),
        ]
        forward = True
    else:
        seeds = [
            (1.95, 1.0), (1.95, 3.0), (1.95, 5.0), (1.95, 7.0), (1.95, 9.0), (1.95, 11.0),
            (1.80, 12.3), (1.40, 12.3), (1.00, 12.3), (0.60, 12.3), (0.20, 12.3),
            (1.60, 2.0), (1.60, 4.5), (1.60, 7.5), (1.60, 10.5),
        ]
        forward = True

    streamline_count = 0
    for th in theta_planes:
        for sr, sz in seeds:
            rf, zf = _trace_streamline_rk2(r_cm, z_cm, flux_r, flux_z, sr, sz, ds=0.04, max_steps=120, forward=forward)
            if len(rf) < 4:
                continue

            xf = rf * np.cos(th)
            yf = rf * np.sin(th)
            pts = np.column_stack([xf, yf, zf])
            segs = np.stack([pts[:-1], pts[1:]], axis=1)

            mid_r = 0.5 * (rf[:-1] + rf[1:])
            mid_z = 0.5 * (zf[:-1] + zf[1:])
            loc_mags = np.array([float(interp_mag((mr, mz))) for mr, mz in zip(mid_r, mid_z)])
            strengths = np.clip((loc_mags - mag_min) / mag_span, 0.0, 1.0) ** 0.6

            line_colors = []
            line_widths = []
            for st in strengths:
                g = 0.45 * (1.0 - st) + 0.05 * st
                alpha = 0.45 + 0.55 * st
                line_colors.append((g, g, g + 0.03 * (1.0 - st), alpha))
                line_widths.append(0.60 + 0.80 * st)

            lc = Line3DCollection(segs, colors=line_colors, linewidths=line_widths)
            ax.add_collection(lc)

            idx_head = min(len(pts) - 1, max(2, int(len(pts) * 0.75)))
            head_segs = _create_arrow_head_3d(pts[idx_head - 1], pts[idx_head], head_len=0.12, head_angle=0.40)
            if head_segs:
                st_h = strengths[min(idx_head, len(strengths) - 1)]
                g_h = 0.45 * (1.0 - st_h) + 0.05 * st_h
                c_h = (g_h, g_h, g_h, 0.50 + 0.50 * st_h)
                lw_h = 0.70 + 0.70 * st_h
                lc_head = Line3DCollection(head_segs, colors=[c_h, c_h], linewidths=[lw_h, lw_h])
                ax.add_collection(lc_head)

            streamline_count += 1

    return streamline_count


def _top_refined_slice_positions(
    z_min_cm: float,
    z_max_cm: float,
    count: int = 9,
    top_bias: float = 1.0,
) -> np.ndarray:
    """生成严格递增切片位置；top_bias=1.0 为均匀等距切片。"""
    if count < 3:
        raise ValueError("slice-count 至少为 3。")
    if not 1.0 <= top_bias <= 3.0:
        raise ValueError("slice-top-bias 应位于 [1, 3]；1 表示均匀，越大越靠顶端加密。")
    u = np.linspace(0.0, 1.0, count)
    mapped = 1.0 - (1.0 - u) ** top_bias
    return z_min_cm + (z_max_cm - z_min_cm) * mapped


def _nice_color_scale(
    data_min: float,
    data_max: float,
    target_intervals: int = 5,
) -> tuple[float, float, np.ndarray, int]:
    """返回覆盖数据范围、标签严格等差的整洁色标范围与刻度。"""
    span = float(data_max - data_min)
    if span <= np.finfo(float).tiny:
        delta = max(abs(data_min) * 0.05, 1.0)
        return data_min - delta, data_max + delta, np.array([data_min]), 2
    raw_step = span / target_intervals
    exponent = float(np.floor(np.log10(raw_step)))
    unit = 10.0**exponent
    fraction = raw_step / unit
    multiplier = next(value for value in (1.0, 2.0, 2.5, 4.0, 5.0, 10.0) if fraction <= value)
    step = multiplier * unit
    lower = float(np.floor(data_min / step) * step)
    upper = float(np.ceil(data_max / step) * step)
    intervals = int(round((upper - lower) / step))
    ticks = lower + step * np.arange(intervals + 1, dtype=float)
    decimals = max(0, int(-np.floor(np.log10(step))))
    if not np.isclose(step * 10**decimals, round(step * 10**decimals)):
        decimals += 1
    return lower, upper, ticks, decimals


def render_field(
    data: FieldData,
    kind: str,
    output_path: Path,
    sector_angle_deg: float,
    slice_z_cm: np.ndarray,
    elev: float,
    azim: float,
    dpi: int,
    coefficient_mode: str,
    arrow_color: str,
    pdf_path: Path | None = None,
    vector_style: str = "arrows",
) -> dict[str, float | int | str]:
    style = FIELD_STYLES[kind]
    field = data.temperature_c if kind == "temperature" else data.moisture
    if field is None:
        raise ValueError(f"输入数据不包含 {kind} 二维场。")

    r_cm = data.r_cm
    z_cm = data.z_cm
    vmin, vmax = float(np.min(field)), float(np.max(field))
    if not vmax > vmin:
        raise ValueError(f"{kind} 场为常值，无法构造有意义的连续色标。")
    color_vmin, color_vmax, color_ticks, color_decimals = _nice_color_scale(vmin, vmax)
    norm = Normalize(vmin=color_vmin, vmax=color_vmax)

    flux_r, flux_z, magnitude, flux_semantics = calculate_flux(
        field,
        r_cm,
        z_cm,
        kind,
        data.temperature_c,
        data.moisture,
        coefficient_mode,
    )

    fig: Figure = plt.figure(figsize=(7.2, 6.0), dpi=600, facecolor="white")
    ax = fig.add_axes(
        [0.020, 0.095, 0.735, 0.815], projection="3d", computed_zorder=True
    )

    half_angle = np.deg2rad(sector_angle_deg / 2.0)
    theta = np.linspace(-half_angle, half_angle, 41)
    rr_horizontal, tt_horizontal = np.meshgrid(r_cm, theta, indexing="ij")

    # 多个水平扇形切片：每一片都使用该 z 高度处的完整径向场值。
    for target_z in slice_z_cm:
        radial_values = _interpolate_column(field, z_cm, float(target_z))
        values = np.repeat(radial_values[:, None], theta.size, axis=1)
        x = rr_horizontal * np.cos(tt_horizontal)
        y = rr_horizontal * np.sin(tt_horizontal)
        z_surface = np.full_like(x, target_z)
        ax.plot_surface(
            x,
            y,
            z_surface,
            facecolors=style.cmap(norm(values)),
            rcount=r_cm.size,
            ccount=theta.size,
            linewidth=0.0,
            antialiased=False,
            shade=False,
            alpha=0.97,
            rasterized=True,
        )

    # 仅在顶层切片绘制清晰的外边缘轮廓，彻底删除下层被遮挡切片的虚线/轮廓线，保持表面纯净与真实的透视遮挡
    top_z = slice_z_cm[-1]
    ax.plot(
        r_cm[-1] * np.cos(theta),
        r_cm[-1] * np.sin(theta),
        np.full_like(theta, top_z),
        color="#173846",
        linewidth=0.90,
        alpha=0.85,
    )
    for side in (-half_angle, half_angle):
        ax.plot(
            r_cm * np.cos(side),
            r_cm * np.sin(side),
            np.full_like(r_cm, top_z),
            color="#173846",
            linewidth=0.70,
            alpha=0.85,
        )

    # 矢量场与切片具有同等三维空间优先级，依托 computed_zorder=True 实现完全平等的双向透视遮挡
    if vector_style == "streamlines":
        vector_count = _render_streamlines_field(
            ax=ax,
            r_cm=r_cm,
            z_cm=z_cm,
            flux_r=flux_r,
            flux_z=flux_z,
            magnitude=magnitude,
            half_angle_rad=half_angle,
            kind=kind,
        )
    else:
        vector_count = _render_dense_volume_vectors(
            ax=ax,
            r_cm=r_cm,
            z_cm=z_cm,
            flux_r=flux_r,
            flux_z=flux_z,
            magnitude=magnitude,
            half_angle_rad=half_angle,
            arrow_color=arrow_color,
        )

    # 不使用长方体三维坐标盒，只保留渲染范围和观察角度。
    lateral = r_cm[-1] * np.sin(half_angle)
    ax.set_xlim(-0.10, r_cm[-1] * 1.28)
    ax.set_ylim(-lateral * 1.18, lateral * 1.42)
    ax.set_zlim(z_cm[0] - 0.75, z_cm[-1] + 0.85)
    ax.view_init(elev=elev, azim=azim)
    # 适度压缩显示纵横比，避免真实 6.25:1 半轴域把径向梯度和箭头压得过窄；坐标值不变。
    ax.set_box_aspect((3.3, 2.3, 5.6))
    ax.set_axis_off()

    scalar_mappable = mpl.cm.ScalarMappable(norm=norm, cmap=style.cmap)
    scalar_mappable.set_array(field)
    colorbar = fig.colorbar(scalar_mappable, ax=ax, fraction=0.05, pad=0.02)
    colorbar_ax = colorbar.ax
    colorbar_ax.set_position([0.740, 0.200, 0.045, 0.595])
    colorbar.ax.tick_params(labelsize=12, width=0.9, length=5, colors="#233B47")
    colorbar.outline.set_linewidth(0.8)
    colorbar.outline.set_edgecolor("#526A75")
    colorbar.set_ticks(color_ticks)
    tick_decimals = max(style.decimals, color_decimals)
    colorbar.set_ticklabels([rf"${value:.{tick_decimals}f}$" for value in color_ticks])
    colorbar_ax.set_title(style.colorbar_label, fontsize=13, fontweight="bold", color="#173846", pad=14)

    # 把 z 标尺和半径标注放到最上层的二维覆盖轴，避免三维深度排序遮挡文字。
    fig.canvas.draw()

    def project_to_figure(x_value: float, y_value: float, z_value: float) -> tuple[float, float]:
        projected_x, projected_y, _ = proj3d.proj_transform(x_value, y_value, z_value, ax.get_proj())
        display_xy = ax.transData.transform((projected_x, projected_y))
        figure_xy = fig.transFigure.inverted().transform(display_xy)
        return float(figure_xy[0]), float(figure_xy[1])

    ruler_theta = half_angle
    ruler_r = r_cm[-1] * 1.55
    ruler_x = ruler_r * np.cos(ruler_theta)
    ruler_y = ruler_r * np.sin(ruler_theta)
    # z 标尺恢复为原先的六个等距主刻度，不把非均匀切片逐一画成小刻线。
    ruler_ticks = np.linspace(float(z_cm[0]), float(z_cm[-1]), 6)
    projected_ruler_points = [project_to_figure(ruler_x, ruler_y, float(tick)) for tick in ruler_ticks]
    vertical_ruler_x = float(np.mean([point[0] for point in projected_ruler_points]))
    ruler_points = [(vertical_ruler_x, point[1]) for point in projected_ruler_points]
    fig.add_artist(
        Line2D(
            [ruler_points[0][0], ruler_points[-1][0]],
            [ruler_points[0][1], ruler_points[-1][1]],
            transform=fig.transFigure,
            color="#173846",
            linewidth=1.25,
            solid_capstyle="round",
            zorder=100,
        )
    )
    for tick, (tick_x, tick_y) in zip(ruler_ticks, ruler_points, strict=True):
        fig.add_artist(
            Line2D(
                [tick_x - 0.008, tick_x + 0.008],
                [tick_y, tick_y],
                transform=fig.transFigure,
                color="#173846",
                linewidth=1.0,
                zorder=100,
            )
        )
        fig.text(
            tick_x + 0.017,
            tick_y,
            rf"${tick:g}$",
            color="#173846",
            fontsize=12,
            ha="left",
            va="center",
            zorder=100,
        )
    fig.text(
        ruler_points[-1][0],
        ruler_points[-1][1] + 0.030,
        r"$z\ (\mathrm{cm})$",
        color="#173846",
        fontsize=13,
        fontweight="bold",
        ha="center",
        va="bottom",
        zorder=100,
    )

    radius_theta = -half_angle
    radius_z = z_cm[0] + 0.12
    radius_start = project_to_figure(0.0, 0.0, radius_z)
    radius_end = project_to_figure(
        r_cm[-1] * np.cos(radius_theta),
        r_cm[-1] * np.sin(radius_theta),
        radius_z,
    )
    # 沿底侧棱的屏幕投影绘制下大括号，避免用一条线冒充尺寸标注。
    start = np.asarray(radius_start, dtype=float)
    end = np.asarray(radius_end, dtype=float)
    tangent = end - start
    tangent /= np.linalg.norm(tangent)
    normal_2d = np.array([-tangent[1], tangent[0]])
    if normal_2d[1] > 0.0:
        normal_2d *= -1.0
    brace_gap = 0.010
    brace_depth = 0.030
    brace_start = start + brace_gap * normal_2d
    brace_end = end + brace_gap * normal_2d
    brace_span = brace_end - brace_start

    def brace_point(u: float, v: float) -> tuple[float, float]:
        point = brace_start + u * brace_span + v * brace_depth * normal_2d
        return float(point[0]), float(point[1])

    brace_vertices = [
        brace_point(0.00, 0.00),
        brace_point(0.02, 0.00),
        brace_point(0.02, 0.55),
        brace_point(0.10, 0.55),
        brace_point(0.24, 0.55),
        brace_point(0.42, 0.55),
        brace_point(0.47, 0.72),
        brace_point(0.49, 0.80),
        brace_point(0.495, 0.96),
        brace_point(0.50, 1.00),
        brace_point(0.505, 0.96),
        brace_point(0.51, 0.80),
        brace_point(0.53, 0.72),
        brace_point(0.58, 0.55),
        brace_point(0.76, 0.55),
        brace_point(0.90, 0.55),
        brace_point(0.98, 0.55),
        brace_point(0.98, 0.00),
        brace_point(1.00, 0.00),
    ]
    brace_codes = [
        MplPath.MOVETO,
        MplPath.CURVE4,
        MplPath.CURVE4,
        MplPath.CURVE4,
        MplPath.CURVE4,
        MplPath.CURVE4,
        MplPath.CURVE4,
        MplPath.CURVE4,
        MplPath.CURVE4,
        MplPath.CURVE4,
        MplPath.CURVE4,
        MplPath.CURVE4,
        MplPath.CURVE4,
        MplPath.CURVE4,
        MplPath.CURVE4,
        MplPath.CURVE4,
        MplPath.CURVE4,
        MplPath.CURVE4,
        MplPath.CURVE4,
    ]
    fig.add_artist(
        PathPatch(
            MplPath(brace_vertices, brace_codes),
            transform=fig.transFigure,
            facecolor="none",
            edgecolor="#173846",
            linewidth=1.35,
            capstyle="round",
            joinstyle="round",
            zorder=100,
        )
    )
    fig_w, fig_h = fig.get_size_inches()
    dx_phys = (end[0] - start[0]) * fig_w
    dy_phys = (end[1] - start[1]) * fig_h
    angle_deg = float(np.degrees(np.arctan2(dy_phys, dx_phys)))

    brace_label = 0.5 * (brace_start + brace_end) + 0.055 * normal_2d
    fig.text(
        brace_label[0],
        brace_label[1],
        rf"$R = {r_cm[-1]:g}\ \mathrm{{cm}}$",
        color="#173846",
        fontsize=13,
        fontweight="bold",
        rotation=angle_deg,
        rotation_mode="anchor",
        ha="center",
        va="top",
        zorder=100,
    )

    # 把箭头与文字打包成一个整体，再让整体中心与色条/色标标题中心严格共线。
    legend_drawing = DrawingArea(40, 14, 0, 0)
    legend_arrow = FancyArrowPatch(
        (1, 7),
        (39, 7),
        arrowstyle="-|>",
        mutation_scale=11,
        linewidth=1.25,
        color="#111827",
        shrinkA=0.0,
        shrinkB=0.0,
    )
    legend_drawing.add_artist(legend_arrow)
    if vector_style == "streamlines":
        legend_desc = "热流梯度轨迹" if kind == "temperature" else "水分迁移流线"
    else:
        legend_desc = "三维热通量" if kind == "temperature" else "三维水分通量"
    legend_text = TextArea(
        legend_desc,
        textprops={"fontsize": 10.0, "color": "#173846", "va": "center"},
    )
    legend_row = HPacker(children=[legend_drawing, legend_text], align="center", pad=0, sep=6)
    colorbar_center_x = colorbar_ax.get_position().x0 + colorbar_ax.get_position().width / 2.0
    legend_group = AnnotationBbox(
        legend_row,
        (colorbar_center_x, 0.105),
        xycoords="figure fraction",
        box_alignment=(0.5, 0.5),
        frameon=False,
        pad=0.0,
        zorder=100,
    )
    fig.add_artist(legend_group)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=dpi, facecolor="white", bbox_inches="tight", pad_inches=0.12)
    if pdf_path is not None:
        pdf_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(pdf_path, facecolor="white", bbox_inches="tight", pad_inches=0.12)
        fig.savefig(pdf_path.with_suffix(".svg"), facecolor="white", bbox_inches="tight", pad_inches=0.12)
        fig.savefig(pdf_path.with_suffix(".tiff"), dpi=dpi, facecolor="white", bbox_inches="tight", pad_inches=0.12)
    plt.close(fig)
    return {
        "field": kind,
        "time_s": "none" if data.time_s is None else float(data.time_s),
        "min": vmin,
        "max": vmax,
        "vectors": vector_count,
        "vector_style": vector_style,
        "elev": float(elev),
        "azim": float(azim),
        "source_kind": data.source_kind,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True, help="NPZ、CSV、TSV 或 Excel 输入文件")
    parser.add_argument("--field", choices=("temperature", "moisture", "both"), default="both")
    parser.add_argument("--time-s", type=float, default=None, help="选取/插值的同一时刻，单位 s")
    parser.add_argument("--sheet", default=None, help="CSV 不使用；Excel 可指定工作表")
    parser.add_argument("--output-dir", type=Path, default=Path("."))
    parser.add_argument("--sector-angle", type=float, default=65.0, help="圆柱扇区圆心角，单位度")
    parser.add_argument(
        "--slice-z-cm",
        type=float,
        nargs="+",
        default=None,
        help="显式指定水平切片轴向坐标（cm）；省略时自动生成顶部加密切片",
    )
    parser.add_argument("--slice-count", type=int, default=9, help="自动切片数量，默认 9")
    parser.add_argument(
        "--slice-top-bias",
        type=float,
        default=1.0,
        help="切片向 z 最大端加密的指数；1 为均匀，默认 1.0",
    )
    parser.add_argument("--elev", type=float, default=24.0, help="三维观察仰角")
    parser.add_argument("--azim", type=float, default=-64.0, help="三维观察方位角")
    parser.add_argument("--dpi", type=int, default=600)
    parser.add_argument(
        "--arrow-color",
        default="auto",
        help="三维通量矢量颜色；auto 为根据梯度自适应黑灰渐变，也可输入指定颜色",
    )
    parser.add_argument(
        "--vector-style",
        choices=("arrows", "streamlines"),
        default="arrows",
        help="矢量场呈现形式：arrows (高密度三维自适应梯度矢量) 或 streamlines (流体力学流线型梯度轨迹)",
    )
    parser.add_argument(
        "--coefficient-mode",
        choices=("q2", "gradient"),
        default="q2",
        help="q2 使用冻结模型 k、D；gradient 仅使用负梯度代理",
    )
    parser.add_argument("--qa-pdf-dir", type=Path, default=None, help="可选：另存 PDF 供排版审计")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if not args.input.is_file():
        raise FileNotFoundError(args.input)
    if not 5.0 <= args.sector_angle <= 180.0:
        raise ValueError("sector-angle 应位于 5°–180°。")
    if args.dpi < 150:
        raise ValueError("科研图 dpi 不应低于 150；建议 300。")
    if args.arrow_color != "auto" and not mpl.colors.is_color_like(args.arrow_color):
        raise ValueError(f"arrow-color 不是 Matplotlib 可识别的颜色：{args.arrow_color}")

    configure_matplotlib()
    requested = ["temperature", "moisture"] if args.field == "both" else [args.field]
    # NPZ 可一次读取两个场；表格通常一个工作表对应一个场，逐场读取。
    shared_data = load_npz(args.input, args.time_s) if args.input.suffix.lower() == ".npz" else None
    reports = []
    for kind in requested:
        data = shared_data if shared_data is not None else load_field_data(args.input, kind, args.time_s, args.sheet)
        assert data is not None
        if args.slice_z_cm is None:
            slice_z = _top_refined_slice_positions(
                float(data.z_cm[0]),
                float(data.z_cm[-1]),
                count=args.slice_count,
                top_bias=args.slice_top_bias,
            )
        else:
            slice_z = np.asarray(args.slice_z_cm, dtype=float)
        if np.any(np.diff(slice_z) <= 0.0):
            raise ValueError("slice-z-cm 必须严格递增且不能重复。")
        resolved_arrow_color = args.arrow_color
        output_path = args.output_dir / FIELD_STYLES[kind].output_name
        pdf_path = args.qa_pdf_dir / FIELD_STYLES[kind].output_name.replace(".png", ".pdf") if args.qa_pdf_dir else None
        reports.append(
            render_field(
                data=data,
                kind=kind,
                output_path=output_path,
                sector_angle_deg=args.sector_angle,
                slice_z_cm=slice_z,
                elev=args.elev,
                azim=args.azim,
                dpi=args.dpi,
                coefficient_mode=args.coefficient_mode,
                arrow_color=resolved_arrow_color,
                pdf_path=pdf_path,
                vector_style=args.vector_style,
            )
        )

    for report in reports:
        print(
            "{field} ({vector_style}): t={time_s}, range=[{min:.8g}, {max:.8g}], vectors={vectors}, "
            "view=(elev={elev:g}, azim={azim:g}), source={source_kind}".format(**report)
        )


if __name__ == "__main__":
    main()
