# -*- coding: utf-8 -*-
"""
读取 final/附件/附件3/result2.xlsx 并绘制各径向位置含水率时序演化曲线
========================================================================
- 径向测点间隔：0.3 cm (r = 0.0, 0.3, 0.6, 0.9, 1.2, 1.5, 1.8 cm)
- 绘图风格：单色学术科技期刊规范，通过线型（实线、虚线、点划线等）区分不同测点
- 统一输出至 eda_figures/ 根目录，仅保留一张高清 PNG 图件
- 跨平台兼容：自适应 Windows / Linux / macOS，通过原生浏览器内核或 rsvg-convert 渲染超清光栅化位图
"""

from __future__ import annotations

from pathlib import Path
import math
import shutil
import subprocess
from openpyxl import load_workbook

# -----------------------------------------------------------------------------
# 路径解析与候选数据源查找
# -----------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parents[2]
SCRIPT_DIR = Path(__file__).resolve().parent
OUT_DIR = ROOT / 'figures'
OUT_DIR.mkdir(parents=True, exist_ok=True)

source_candidates = [
    ROOT / 'code' / 'results' / 'result2.xlsx',
    ROOT / 'code' / 'results' / 'result2.xlsx',
    ROOT / 'problem' / '附件' / '附件3' / 'result2.xlsx',
]

SOURCE = None
for cand in source_candidates:
    if cand.exists() and cand.stat().st_size > 50000:
        SOURCE = cand
        break

if SOURCE is None:
    raise FileNotFoundError(f"未找到有效的结果文件 result2.xlsx，检索路径: {source_candidates}")


def generate_svg_content(radii: list, data: list, selected: list) -> str:
    """生成精确几何 SVG 矢量文本内容"""
    width, height = 1500, 1100
    left, top, pw, ph = 150, 80, 1260, 870
    ymin, ymax = 0.9, 2.65

    def x(t): return left + t / 10800 * pw
    def y(c): return top + (ymax - c) / (ymax - ymin) * ph

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        '<style>text{font-family:"Latin Modern Roman","CMU Serif","Microsoft YaHei",serif;fill:#111;font-size:26px}.cn{font-family:"Microsoft YaHei","微软雅黑","PingFang SC",sans-serif}</style>',
        f'<defs><clipPath id="plot"><rect x="{left}" y="{top}" width="{pw}" height="{ph}"/></clipPath></defs>'
    ]

    for tick in range(0, 10801, 1800):
        xx = x(tick)
        parts.extend([
            f'<line x1="{xx}" y1="{top}" x2="{xx}" y2="{top + ph}" stroke="#e5e8eb"/>',
            f'<text x="{xx}" y="{top + ph + 43}" text-anchor="middle">{tick}</text>'
        ])

    for tick in (1, 1.25, 1.5, 1.75, 2, 2.25, 2.5):
        yy = y(tick)
        parts.extend([
            f'<line x1="{left}" y1="{yy}" x2="{left + pw}" y2="{yy}" stroke="#e5e8eb"/>',
            f'<text x="{left - 20}" y="{yy + 9}" text-anchor="end">{tick:g}</text>'
        ])

    dash_patterns = ['', '16 7', '3 6', '16 6 3 6',
                     '16 5 3 5 3 5', '24 8', '1 7']

    for legend_index, j in enumerate(selected):
        r = radii[j]
        pts = ' '.join(f'{x(row[0]):.3f},{y(row[j + 1]):.3f}' for row in data)
        dash = f' stroke-dasharray="{dash_patterns[legend_index]}"' if dash_patterns[legend_index] else ''
        cap = 'round' if legend_index in (2, 6) else 'butt'
        parts.append(f'<polyline points="{pts}" fill="none" stroke="#111" stroke-width="4.2"{dash} stroke-linecap="{cap}" clip-path="url(#plot)"/>')

    legend_x, legend_y, legend_w, legend_h = left + pw - 290, top + 28, 260, 342
    parts.append(f'<rect x="{legend_x}" y="{legend_y}" width="{legend_w}" height="{legend_h}" fill="white" stroke="#111" stroke-width="2"/>')

    for legend_index, j in enumerate(selected):
        r = radii[j]
        ly = legend_y + 34 + legend_index * 45
        dash = f' stroke-dasharray="{dash_patterns[legend_index]}"' if dash_patterns[legend_index] else ''
        cap = 'round' if legend_index in (2, 6) else 'butt'
        parts.append(f'<line x1="{legend_x + 20}" y1="{ly}" x2="{legend_x + 92}" y2="{ly}" stroke="#111" stroke-width="4.8"{dash} stroke-linecap="{cap}"/>')
        parts.append(f'<text x="{legend_x + 110}" y="{ly + 8}" style="font-size:23px"><tspan font-style="italic">r</tspan><tspan xml:space="preserve"> = {r:.1f} cm</tspan></text>')

    parts.extend([
        f'<rect x="{left}" y="{top}" width="{pw}" height="{ph}" fill="none" stroke="#111" stroke-width="2.5"/>',
        f'<text x="{left + pw / 2}" y="1040" text-anchor="middle" style="font-size:36px"><tspan class="cn">时间 </tspan><tspan font-style="italic">t</tspan><tspan> (s)</tspan></text>',
        f'<text transform="translate(48 {top + ph / 2}) rotate(-90)" text-anchor="middle" style="font-size:36px"><tspan class="cn">含水率 </tspan><tspan font-style="italic">C</tspan><tspan> (kg/kg)</tspan></text>',
        '</svg>'
    ])

    return '\n'.join(parts)


def convert_svg_to_png(svg_file: Path, png_file: Path):
    """将 SVG 转换为高清 3000x2200 PNG"""
    # 1. 首选尝试系统自带的 Edge / Chrome (无损浏览器矢量排版渲染，支持全字体与 stroke-dasharray)
    browser_candidates = [
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        shutil.which("msedge"),
        shutil.which("chrome"),
    ]
    browser = next((p for p in browser_candidates if p and Path(p).exists()), None)
    if browser:
        temp_html = svg_file.with_suffix(".temp.html")
        temp_html.write_text(
            f'<!DOCTYPE html><html><head><meta charset="utf-8"><style>'
            f'body {{ margin: 0; padding: 0; background: white; overflow: hidden; }}'
            f'</style></head><body>{svg_file.read_text(encoding="utf-8")}</body></html>',
            encoding="utf-8"
        )
        try:
            cmd = [
                str(browser),
                "--headless=new",
                "--disable-gpu",
                "--force-device-scale-factor=2",
                "--window-size=1500,1100",
                f"--screenshot={png_file}",
                temp_html.as_uri()
            ]
            subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if png_file.exists():
                print(f"[√] 浏览器内核高保真光栅化完成: {png_file}")
                return
        finally:
            if temp_html.exists():
                temp_html.unlink()

    # 2. 尝试 rsvg-convert (macOS / Linux)
    rsvg_cmd = shutil.which('rsvg-convert') or ('/opt/homebrew/bin/rsvg-convert' if Path('/opt/homebrew/bin/rsvg-convert').exists() else None)
    if rsvg_cmd:
        subprocess.run([rsvg_cmd, '-w', '3000', '-h', '2200', str(svg_file), '-o', str(png_file)], check=True)
        print(f"[√] rsvg-convert 渲染完成: {png_file}")
        return

    # 3. 备选方案：PyMuPDF
    import pymupdf
    doc = pymupdf.open(stream=svg_file.read_bytes(), filetype='svg')
    pdf_bytes = doc.convert_to_pdf()
    pdf_doc = pymupdf.open(stream=pdf_bytes, filetype="pdf")
    pix = pdf_doc[0].get_pixmap(matrix=pymupdf.Matrix(2.0, 2.0))
    pix.save(str(png_file))
    print(f"[√] PyMuPDF 渲染完成: {png_file}")


def main():
    print(f">>> 读取数据源: {SOURCE}")
    book = load_workbook(SOURCE, read_only=True, data_only=True)
    rows = list(book['水分浓度'].values)
    radii = rows[0][1:]
    data = rows[1:]
    book.close()

    assert len(radii) == 21 and all(len(row) == 22 for row in data)
    assert all(all(isinstance(v, (int, float)) and math.isfinite(v) for v in row) for row in data)
    assert all(a[0] < b[0] for a, b in zip(data, data[1:]))

    selected = [j for j, r in enumerate(radii) if abs(r / 0.3 - round(r / 0.3)) < 1e-9]

    # 1. 生成 SVG 矢量源文件（保存在 scripts/ 目录备查）
    svg_content = generate_svg_content(radii, data, selected)
    svg_script_file = SCRIPT_DIR / 'result2_moisture_lines_0p3cm.svg'
    svg_script_file.write_text(svg_content, encoding='utf-8')
    print(f"[√] SVG 矢量源文件已就绪: {svg_script_file}")

    # 2. 渲染高分辨率 PNG 图像并输出至 eda_figures/ 根目录
    png_final_file = OUT_DIR / 'result2_moisture_lines_0p3cm.png'
    convert_svg_to_png(svg_script_file, png_final_file)

    # 3. 清理 eda_figures/ 根目录下的多余格式（.pdf, .svg），仅保留一张 .png
    redundant_pdf = OUT_DIR / 'result2_moisture_lines_0p3cm.pdf'
    if redundant_pdf.exists():
        # 归档至 Archive/pdf/
        archive_pdf_dir = OUT_DIR / 'Archive' / 'pdf'
        archive_pdf_dir.mkdir(parents=True, exist_ok=True)
        shutil.move(str(redundant_pdf), str(archive_pdf_dir / redundant_pdf.name))
        print(f"[√] 已归档冗余 PDF 至: {archive_pdf_dir / redundant_pdf.name}")

    redundant_svg = OUT_DIR / 'result2_moisture_lines_0p3cm.svg'
    if redundant_svg.exists():
        redundant_svg.unlink()
        print(f"[√] 已移除 eda_figures/ 根目录的冗余 SVG 文件")

    # 同步一份 PNG 副本到 scripts/ 目录备查
    shutil.copy2(png_final_file, SCRIPT_DIR / png_final_file.name)

    print(f"\n[OK] 成功生成并保留唯一定稿图件:")
    print(f"     {png_final_file}")
    print(f"     包含 {len(data)} 个时间步 × {len(selected)} 个代表性径向测点")


if __name__ == '__main__':
    main()
