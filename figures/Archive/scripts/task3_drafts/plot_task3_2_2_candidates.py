"""
Task 3.2.2: 动边界收缩机制网格微元对比图 (右子图候选方案集)
几何特征:
- 厚圆环柱扇形微元 (Annular sector / Cylindrical sector)
- 截面正方形约束: \Delta r = R_out - R_in = h (\Delta z)
- 左侧: 收缩后微元 (t > 0, 缩小正方形截面, 对应左图方案 C 深酒红)
- 右侧: 收缩前微元 (t = 0, 初始正方形截面, 对应左图方案 C 经典红)
- 空间完全分离 (Non-overlapping, 径向间隔清晰)
- 左下角柱坐标系 (+z, +r, +\theta)
"""

import os
import subprocess
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch
from PIL import Image

SCRATCH = r"C:\Users\kqdx\.gemini\antigravity\brain\ce5f745e-eae3-4eca-9e3f-87c5c965cace\scratch"
EDA_DIR = r"D:\HIT\数模2026\eda_figures"
OUTPUT_DIR = os.path.join(EDA_DIR, "task3_candidates")
ARTIFACT_DIR = r"C:\Users\kqdx\.gemini\antigravity\brain\ce5f745e-eae3-4eca-9e3f-87c5c965cace"
os.makedirs(OUTPUT_DIR, exist_ok=True)

three_js_path = r"D:\HIT\数模2026\eda_figures\Archive\scripts\three.min.js".replace('\\', '/')
edge_exe = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

W, H = 2600, 2600

# -----------------------------------------------------------------------------
# 1. 几何参数设定 (严格正方形截面与非重叠约束)
# -----------------------------------------------------------------------------
delta_theta_deg = 55.0

# 右侧初始微元 (t = 0)
r0 = 4.65
a0 = 0.85
rin_0 = r0 - a0 / 2.0   # 4.225
rout_0 = r0 + a0 / 2.0  # 5.075
h0 = a0                 # 0.85 (正方形: \Delta r = 0.85 = h)

# 左侧收缩微元 (t > 0, 尺度因子 s = 0.76)
s = 0.76
r_s = r0 * s            # 3.534
a_s = a0 * s            # 0.646
rin_s = r_s - a_s / 2.0   # 3.211
rout_s = r_s + a_s / 2.0  # 3.857
h_s = a_s                 # 0.646 (正方形: \Delta r = 0.646 = h)

# 径向间隙: rin_0 - rout_s = 4.225 - 3.857 = 0.368 > 0 (严格非重叠)

# -----------------------------------------------------------------------------
# 2. 3D 相机与视角参数 (继承 plot_fvm_5rings_lineart.py 黄金视角)
# -----------------------------------------------------------------------------
scale_factor = 1.45
target = np.array([4.10, 0.00, 0.00])
cam_orig = np.array([-0.01, 1.86, -8.91])
cam_pos = target + (cam_orig - np.array([3.3, 0, 0])) * scale_factor

C_x, C_y, C_z = cam_pos
D = np.sqrt(C_x**2 + C_z**2)
phi = np.arctan2(-C_z, C_x)

alpha0 = np.arccos(rout_0 / D)
theta_sil0 = phi - alpha0

alphaS = np.arccos(rout_s / D)
theta_silS = phi - alphaS

# -----------------------------------------------------------------------------
# 3. 生成 Three.js 场景 HTML
# -----------------------------------------------------------------------------
def build_threejs_html(style_id):
    if style_id == 'A':
        tube_color0 = "0x0F172A"
        tube_colorS = "0x0F172A"
        mat0_code = "new THREE.MeshBasicMaterial({ color: 0xFFFFFF, polygonOffset: true, polygonOffsetFactor: 1.0, polygonOffsetUnits: 1.0 })"
        matS_code = "new THREE.MeshBasicMaterial({ color: 0xFFFFFF, polygonOffset: true, polygonOffsetFactor: 1.0, polygonOffsetUnits: 1.0 })"
    elif style_id == 'B':
        tube_color0 = "0xDC2626"
        tube_colorS = "0x7F1D1D"
        mat0_code = "new THREE.MeshBasicMaterial({ color: 0xFCA5A5, transparent: true, opacity: 0.35, polygonOffset: true, polygonOffsetFactor: 1.0, polygonOffsetUnits: 1.0 })"
        matS_code = "new THREE.MeshBasicMaterial({ color: 0x991B1B, transparent: true, opacity: 0.55, polygonOffset: true, polygonOffsetFactor: 1.0, polygonOffsetUnits: 1.0 })"
    elif style_id == 'C':
        tube_color0 = "0x0F172A"
        tube_colorS = "0x0F172A"
        mat0_code = "new THREE.MeshBasicMaterial({ color: 0xFFFFFF, polygonOffset: true, polygonOffsetFactor: 1.0, polygonOffsetUnits: 1.0 })"
        matS_code = "new THREE.MeshBasicMaterial({ color: 0xFFFFFF, polygonOffset: true, polygonOffsetFactor: 1.0, polygonOffsetUnits: 1.0 })"
    elif style_id == 'D':
        tube_color0 = "0x0F172A"
        tube_colorS = "0x0F172A"
        mat0_code = "new THREE.MeshBasicMaterial({ color: 0xFFFFFF, polygonOffset: true, polygonOffsetFactor: 1.0, polygonOffsetUnits: 1.0 })"
        matS_code = "new THREE.MeshBasicMaterial({ color: 0xFFFFFF, polygonOffset: true, polygonOffsetFactor: 1.0, polygonOffsetUnits: 1.0 })"

    html = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <script src="{three_js_path}"></script>
  <style>
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    body {{ background: #FFFFFF; overflow: hidden; width: {W}px; height: {H}px; }}
    #container {{ width: {W}px; height: {H}px; }}
  </style>
</head>
<body>
  <div id="container"></div>
  <script>
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0xFFFFFF);

    const camera = new THREE.PerspectiveCamera(42, {W} / {H}, 0.1, 100);
    camera.position.set({cam_pos[0]:.4f}, {cam_pos[1]:.4f}, {cam_pos[2]:.4f});
    const target = new THREE.Vector3({target[0]:.4f}, {target[1]:.4f}, {target[2]:.4f});
    camera.lookAt(target);

    const renderer = new THREE.WebGLRenderer({{ antialias: true, preserveDrawingBuffer: true }});
    renderer.setSize({W}, {H});
    renderer.setPixelRatio(1);
    renderer.setClearColor(0xFFFFFF, 1.0);
    document.getElementById('container').appendChild(renderer.domElement);

    function createRingSectorGeometry(rIn, rOut, h) {{
      const startAngle = 0.0;
      const endAngle = ({delta_theta_deg} * Math.PI) / 180.0;

      const shape = new THREE.Shape();
      const segs = 64;

      shape.absarc(0, 0, rOut, startAngle, endAngle, false);
      shape.lineTo(rIn * Math.cos(endAngle), rIn * Math.sin(endAngle));
      shape.absarc(0, 0, rIn, endAngle, startAngle, true);
      shape.lineTo(rOut * Math.cos(startAngle), rOut * Math.sin(startAngle));

      const extrudeSettings = {{
        depth: h,
        bevelEnabled: false,
        curveSegments: segs
      }};

      const geo = new THREE.ExtrudeGeometry(shape, extrudeSettings);
      geo.rotateX(-Math.PI / 2);
      geo.translate(0, -h / 2, 0);
      return geo;
    }}

    const mat0 = {mat0_code};
    const matS = {matS_code};

    const tubeMat0 = new THREE.MeshBasicMaterial({{ color: {tube_color0} }});
    const tubeMatS = new THREE.MeshBasicMaterial({{ color: {tube_colorS} }});
    const redTubeMat = new THREE.MeshBasicMaterial({{ color: 0xDC2626 }});
    const wineTubeMat = new THREE.MeshBasicMaterial({{ color: 0x7F1D1D }});
    const gridMat = new THREE.LineBasicMaterial({{ color: 0x94A3B8, linewidth: 2 }});

    function createCylinderBetweenPoints(p1, p2, radius, mat) {{
      const dir = new THREE.Vector3().subVectors(p2, p1);
      const len = dir.length();
      if (len < 1e-4) return null;
      const geom = new THREE.CylinderGeometry(radius, radius, len, 8, 1, false);
      geom.translate(0, len / 2, 0);
      geom.rotateX(Math.PI / 2);
      const mesh = new THREE.Mesh(geom, mat || tubeMat0);
      mesh.position.copy(p1);
      mesh.lookAt(p2);
      return mesh;
    }}

    // 1. 右侧初始微元
    const geo0 = createRingSectorGeometry({rin_0}, {rout_0}, {h0});
    const mesh0 = new THREE.Mesh(geo0, mat0);
    scene.add(mesh0);

    const edge0 = new THREE.EdgesGeometry(geo0, 15);
    const pos0 = edge0.attributes.position;
    const tubeR0 = 0.024;
    for (let i = 0; i < pos0.count; i += 2) {{
      const p1 = new THREE.Vector3(pos0.getX(i), pos0.getY(i), pos0.getZ(i));
      const p2 = new THREE.Vector3(pos0.getX(i+1), pos0.getY(i+1), pos0.getZ(i+1));
      const cyl = createCylinderBetweenPoints(p1, p2, tubeR0, tubeMat0);
      if (cyl) scene.add(cyl);
    }}

    // 右微元外轮廓圆柱母线
    const th0 = {theta_sil0};
    const p1_0 = new THREE.Vector3({rout_0} * Math.cos(th0), -{h0}/2, -{rout_0} * Math.sin(th0));
    const p2_0 = new THREE.Vector3({rout_0} * Math.cos(th0),  {h0}/2, -{rout_0} * Math.sin(th0));
    scene.add(createCylinderBetweenPoints(p1_0, p2_0, tubeR0, tubeMat0));

    // 2. 左侧收缩微元
    const geoS = createRingSectorGeometry({rin_s}, {rout_s}, {h_s});
    const meshS = new THREE.Mesh(geoS, matS);
    scene.add(meshS);

    const edgeS = new THREE.EdgesGeometry(geoS, 15);
    const posS = edgeS.attributes.position;
    const tubeRS = 0.022;
    for (let i = 0; i < posS.count; i += 2) {{
      const p1 = new THREE.Vector3(posS.getX(i), posS.getY(i), posS.getZ(i));
      const p2 = new THREE.Vector3(posS.getX(i+1), posS.getY(i+1), posS.getZ(i+1));
      const cyl = createCylinderBetweenPoints(p1, p2, tubeRS, tubeMatS);
      if (cyl) scene.add(cyl);
    }}

    // 左微元外轮廓圆柱母线
    const thS = {theta_silS};
    const p1_s = new THREE.Vector3({rout_s} * Math.cos(thS), -{h_s}/2, -{rout_s} * Math.sin(thS));
    const p2_s = new THREE.Vector3({rout_s} * Math.cos(thS),  {h_s}/2, -{rout_s} * Math.sin(thS));
    scene.add(createCylinderBetweenPoints(p1_s, p2_s, tubeRS, tubeMatS));

    // 风格 C: 前正方形截面粗红/酒红边框强化
    if ("{style_id}" === "C") {{
      const th_front = {np.radians(delta_theta_deg)};
      const cos_f = Math.cos(th_front);
      const sin_f = Math.sin(th_front);

      // 右微元前正方形 (经典红)
      const p0_a = new THREE.Vector3({rin_0} * cos_f, -{h0}/2, -{rin_0} * sin_f);
      const p0_b = new THREE.Vector3({rout_0} * cos_f, -{h0}/2, -{rout_0} * sin_f);
      const p0_c = new THREE.Vector3({rout_0} * cos_f,  {h0}/2, -{rout_0} * sin_f);
      const p0_d = new THREE.Vector3({rin_0} * cos_f,  {h0}/2, -{rin_0} * sin_f);
      [ [p0_a, p0_b], [p0_b, p0_c], [p0_c, p0_d], [p0_d, p0_a] ].forEach(pair => {{
        scene.add(createCylinderBetweenPoints(pair[0], pair[1], 0.034, redTubeMat));
      }});

      // 左微元前正方形 (暗酒红)
      const ps_a = new THREE.Vector3({rin_s} * cos_f, -{h_s}/2, -{rin_s} * sin_f);
      const ps_b = new THREE.Vector3({rout_s} * cos_f, -{h_s}/2, -{rout_s} * sin_f);
      const ps_c = new THREE.Vector3({rout_s} * cos_f,  {h_s}/2, -{rout_s} * sin_f);
      const ps_d = new THREE.Vector3({rin_s} * cos_f,  {h_s}/2, -{rin_s} * sin_f);
      [ [ps_a, ps_b], [ps_b, ps_c], [ps_c, ps_d], [ps_d, ps_a] ].forEach(pair => {{
        scene.add(createCylinderBetweenPoints(pair[0], pair[1], 0.030, wineTubeMat));
      }});
    }}

    // 风格 D: 截面网格细分线 (示意相对尺度不变)
    if ("{style_id}" === "D") {{
      const th_front = {np.radians(delta_theta_deg)};
      const cos_f = Math.cos(th_front);
      const sin_f = Math.sin(th_front);

      // 右微元十字网格线
      const r_mid0 = ({rin_0} + {rout_0}) / 2;
      const g0_v1 = new THREE.Vector3(r_mid0 * cos_f, -{h0}/2, -r_mid0 * sin_f);
      const g0_v2 = new THREE.Vector3(r_mid0 * cos_f,  {h0}/2, -r_mid0 * sin_f);
      scene.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints([g0_v1, g0_v2]), gridMat));

      const g0_h1 = new THREE.Vector3({rin_0} * cos_f, 0, -{rin_0} * sin_f);
      const g0_h2 = new THREE.Vector3({rout_0} * cos_f, 0, -{rout_0} * sin_f);
      scene.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints([g0_h1, g0_h2]), gridMat));

      // 左微元十字网格线
      const r_midS = ({rin_s} + {rout_s}) / 2;
      const gs_v1 = new THREE.Vector3(r_midS * cos_f, -{h_s}/2, -r_midS * sin_f);
      const gs_v2 = new THREE.Vector3(r_midS * cos_f,  {h_s}/2, -r_midS * sin_f);
      scene.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints([gs_v1, gs_v2]), gridMat));

      const gs_h1 = new THREE.Vector3({rin_s} * cos_f, 0, -{rin_s} * sin_f);
      const gs_h2 = new THREE.Vector3({rout_s} * cos_f, 0, -{rout_s} * sin_f);
      scene.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints([gs_h1, gs_h2]), gridMat));
    }}

    renderer.render(scene, camera);
  </script>
</body>
</html>
"""
    return html

def render_and_crop_base(style_id):
    html = build_threejs_html(style_id)
    hpath = os.path.join(SCRATCH, f"candidate_{style_id}.html")
    rpath = os.path.join(SCRATCH, f"candidate_{style_id}_raw.png")
    with open(hpath, "w", encoding="utf-8") as f:
        f.write(html)

    subprocess.run([edge_exe, "--headless", f"--screenshot={rpath}", f"--window-size={W},{H}", f"file:///{hpath.replace(os.sep, '/')}"], check=True)

    img = Image.open(rpath)
    arr = np.array(img.convert("L"))
    non_white = arr < 250
    y_idx, x_idx = np.where(non_white)

    cx = int((np.min(x_idx) + np.max(x_idx)) / 2)
    cy = int((np.min(y_idx) + np.max(y_idx)) / 2)
    span = max(np.max(x_idx) - np.min(x_idx), np.max(y_idx) - np.min(y_idx))
    pad = int(span * 0.44)
    R_crop = int(span / 2 + pad)

    crop_box = (cx - R_crop, cy - R_crop, cx + R_crop, cy + R_crop)
    # 水平翻转：使收缩后的微元位于左侧，初始微元位于右侧
    cropped = img.crop(crop_box).transpose(Image.FLIP_LEFT_RIGHT)
    return cropped

def draw_coordinate_system(ax, orig_x, orig_y, length=180.0):
    """
    绘制极简高保真柱坐标系 (+z, +r, +\theta)
    """
    # +z 轴
    z_top = (orig_x, orig_y - length * 1.15)
    ax.annotate('', xy=z_top, xytext=(orig_x, orig_y),
                arrowprops=dict(arrowstyle='->', color='#0F172A', lw=2.2, mutation_scale=18), zorder=20)
    ax.text(z_top[0], z_top[1] - 16, r'$+z$', fontsize=18, fontweight='bold', color='#0F172A', ha='center', va='bottom')

    # +r 轴
    ray_angle = np.radians(20)
    r_tip = (orig_x + length * np.cos(ray_angle), orig_y + length * np.sin(ray_angle) * 0.48)

    # 扇形面 +\theta
    theta_angles = np.linspace(np.radians(-26), np.radians(20), 50)
    arc_x = orig_x + (length * 0.95) * np.cos(theta_angles)
    arc_y = orig_y + (length * 0.95) * np.sin(theta_angles) * 0.48
    poly_x = [orig_x] + list(arc_x) + [orig_x]
    poly_y = [orig_y] + list(arc_y) + [orig_y]

    ax.fill(poly_x, poly_y, color='#F1F5F9', alpha=0.90, zorder=15)
    ax.plot(poly_x, poly_y, color='#475569', linewidth=1.4, zorder=16)

    ax.annotate('', xy=r_tip, xytext=(orig_x, orig_y),
                arrowprops=dict(arrowstyle='->', color='#0F172A', lw=2.2, mutation_scale=18), zorder=20)
    ax.text(r_tip[0] + 16, r_tip[1] + 4, r'$+r$', fontsize=18, fontweight='bold', color='#0F172A', ha='left', va='center')

    # +\theta 标识
    mid_th = np.radians(-3)
    th_x = orig_x + (length * 0.55) * np.cos(mid_th)
    th_y = orig_y + (length * 0.55) * np.sin(mid_th) * 0.48 - 12
    ax.text(th_x, th_y, r'$+\theta$', fontsize=15, fontstyle='italic', color='#334155', ha='center', va='center', zorder=22)

def build_candidate_figure(style_id, title_text):
    plt.rcParams['mathtext.fontset'] = 'cm'
    plt.rcParams['font.serif'] = ['Times New Roman', 'DejaVu Serif']
    plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'DejaVu Sans']

    base_img = render_and_crop_base(style_id)
    cw, ch = base_img.size

    fig, ax = plt.subplots(figsize=(8, 8), dpi=300)
    ax.imshow(base_img, extent=[0, cw, ch, 0])
    ax.set_xlim(0, cw)
    ax.set_ylim(ch, 0)
    ax.axis('off')

    # 1. 坐标轴 (左下角)
    orig_x = cw * 0.16
    orig_y = ch * 0.84
    draw_coordinate_system(ax, orig_x, orig_y, length=cw * 0.135)

    # 2. 径向收缩指示微矢 (连接右微元前截面与左微元前截面)
    # 右微元前正方形中心约在 (cw * 0.60, ch * 0.68)
    # 左微元前正方形中心约在 (cw * 0.38, ch * 0.63)
    arr_start = (cw * 0.53, ch * 0.66)
    arr_end = (cw * 0.43, ch * 0.61)

    if style_id in ['A', 'C']:
        arr = FancyArrowPatch(arr_start, arr_end,
                               connectionstyle="arc3,rad=-0.10",
                               arrowstyle='-|>,head_length=8.0,head_width=4.8',
                               color='#7F1D1D', lw=2.2, zorder=30)
        ax.add_patch(arr)
    elif style_id == 'B':
        arr = FancyArrowPatch(arr_start, arr_end,
                               connectionstyle="arc3,rad=-0.10",
                               arrowstyle='-|>,head_length=8.5,head_width=5.0',
                               color='#7F1D1D', lw=2.4, zorder=30)
        ax.add_patch(arr)
    elif style_id == 'D':
        arr = FancyArrowPatch(arr_start, arr_end,
                               connectionstyle="arc3,rad=-0.10",
                               arrowstyle='-|>,head_length=8.0,head_width=4.8',
                               color='#0F172A', lw=2.2, zorder=30)
        ax.add_patch(arr)

        # 标注尺寸符号: \Delta r = h
        p_bl = (cw * 0.54, ch * 0.80)
        p_br = (cw * 0.68, ch * 0.84)
        ax.plot([p_bl[0], p_br[0]], [p_bl[1] + 12, p_br[1] + 12], color='#0F172A', lw=1.3, zorder=25)
        ax.text((p_bl[0] + p_br[0]) / 2, (p_bl[1] + p_br[1]) / 2 + 32, r'$\Delta r = h$',
                fontsize=15, color='#0F172A', ha='center', va='top')

    # 3. 极简候选标识标题 (仅用于对比讨论)
    ax.text(cw * 0.04, ch * 0.06, title_text, fontsize=15, fontweight='bold', color='#0F172A', ha='left', va='top')

    out_file = os.path.join(OUTPUT_DIR, f"task3_2_2_candidate_{style_id.lower()}.png")
    fig.savefig(out_file, dpi=300, bbox_inches='tight', pad_inches=0.02)
    plt.close(fig)

    art_file = os.path.join(ARTIFACT_DIR, f"task3_2_2_candidate_{style_id.lower()}.png")
    Image.open(out_file).save(art_file)

    print(f"Generated Style {style_id} -> {out_file}")
    return out_file

def generate_comparison_sheet(files):
    fig, axes = plt.subplots(2, 2, figsize=(14, 14), dpi=300)
    for ax, f in zip(axes.flat, files):
        im = Image.open(f)
        ax.imshow(im)
        ax.axis('off')

    plt.subplots_adjust(wspace=0.03, hspace=0.03)
    comp_file = os.path.join(OUTPUT_DIR, "task3_2_2_candidates_comparison.png")
    fig.savefig(comp_file, dpi=300, bbox_inches='tight', pad_inches=0.03)
    plt.close(fig)

    art_comp = os.path.join(ARTIFACT_DIR, "task3_2_2_candidates_comparison.png")
    Image.open(comp_file).save(art_comp)
    print(f"Comparison sheet generated -> {comp_file}")

if __name__ == "__main__":
    styles = [
        ('A', "方案 A: 经典黑线线稿 + 暗酒红径向收缩微矢 (极简素雅)"),
        ('B', "方案 B: 半透明双色体素 (承袭左图方案 C 红/酒红配色)"),
        ('C', "方案 C: 正方形前截面红/酒红轮廓强化 (截面特征醒目)"),
        ('D', "方案 D: 截面网格剖分与等度量指示 (几何尺度与网格不变性)")
    ]
    generated_files = []
    for s_id, title in styles:
        f = build_candidate_figure(s_id, title)
        generated_files.append(f)

    generate_comparison_sheet(generated_files)
    print("All candidates generated successfully!")
