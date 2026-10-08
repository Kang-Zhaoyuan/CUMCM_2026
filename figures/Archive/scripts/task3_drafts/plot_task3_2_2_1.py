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
os.makedirs(OUTPUT_DIR, exist_ok=True)

three_js_path = r"D:\HIT\数模2026\eda_figures\Archive\scripts\three.min.js".replace('\\', '/')
edge_exe = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

W, H = 2600, 2600

# -----------------------------------------------------------------------------
# 1. 几何参数设定 (拉开距离，严格非重叠，正方形截面)
# -----------------------------------------------------------------------------
delta_theta_deg = 52.0

# 变换前的几何体 (Right, 较大)
r0 = 4.85
a0 = 0.85
rin_0 = r0 - a0 / 2.0   # 4.425
rout_0 = r0 + a0 / 2.0  # 5.275
h0 = a0                 # 0.85

# 变换后的几何体 (Left, 较小, 尺度因子 s = 0.70)
# 距离拉开：左微元中心半径设为 3.10
r_s = 3.10
a_s = a0 * (r_s / r0)   # 0.543 (保持正方形截面与等比例缩放)
rin_s = r_s - a_s / 2.0 # 2.828
rout_s = r_s + a_s / 2.0 # 3.372
h_s = a_s                # 0.543

# 间隙检查：
# rin_0 - rout_s = 4.425 - 3.372 = 1.053 (十分充裕的间隔，彻底杜绝拥挤！)
print(f"Initial: [rin={rin_0:.3f}, rout={rout_0:.3f}], a0={a0:.3f}")
print(f"Shrunk : [rin={rin_s:.3f}, rout={rout_s:.3f}], as={a_s:.3f}")
print(f"Gap between bodies: {rin_0 - rout_s:.3f} > 0")

# -----------------------------------------------------------------------------
# 2. 相机参数
# -----------------------------------------------------------------------------
scale_factor = 1.45
target = np.array([4.00, 0.00, 0.00])
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
# 3. Three.js 场景构建: 包含轮廓线粗细差异与8分割虚线
# -----------------------------------------------------------------------------
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

    const whiteMat = new THREE.MeshBasicMaterial({{
      color: 0xFFFFFF,
      polygonOffset: true,
      polygonOffsetFactor: 1.0,
      polygonOffsetUnits: 1.0
    }});

    // 轮廓材质: 变换前 (粗黑) vs 变换后 (细浅)
    const boldBlackTube = new THREE.MeshBasicMaterial({{ color: 0x0F172A }});
    const lightSlateTube = new THREE.MeshBasicMaterial({{ color: 0x475569 }});
    const dashLineMat = new THREE.LineBasicMaterial({{ color: 0x64748B, linewidth: 2 }});

    function createCylinderBetweenPoints(p1, p2, radius, mat) {{
      const dir = new THREE.Vector3().subVectors(p2, p1);
      const len = dir.length();
      if (len < 1e-4) return null;
      const geom = new THREE.CylinderGeometry(radius, radius, len, 8, 1, false);
      geom.translate(0, len / 2, 0);
      geom.rotateX(Math.PI / 2);
      const mesh = new THREE.Mesh(geom, mat);
      mesh.position.copy(p1);
      mesh.lookAt(p2);
      return mesh;
    }}

    // 高精度分段虚线生成函数
    function addDashedPolyline(points, dashLen = 0.07, gapLen = 0.045, mat = dashLineMat) {{
      for (let i = 0; i < points.length - 1; i++) {{
        const pA = points[i];
        const pB = points[i+1];
        const segDist = pA.distanceTo(pB);
        const dir = new THREE.Vector3().subVectors(pB, pA).normalize();

        let traveled = 0.0;
        let isDash = true;
        while (traveled < segDist) {{
          const curLen = isDash ? dashLen : gapLen;
          const nextDist = Math.min(traveled + curLen, segDist);
          if (isDash) {{
            const pStart = new THREE.Vector3().copy(pA).addScaledVector(dir, traveled);
            const pEnd = new THREE.Vector3().copy(pA).addScaledVector(dir, nextDist);
            const geom = new THREE.BufferGeometry().setFromPoints([pStart, pEnd]);
            scene.add(new THREE.Line(geom, mat));
          }}
          traveled = nextDist;
          isDash = !isDash;
        }}
      }}
    }}

    // 直线虚线便捷包装
    function addDashedLine(p1, p2, dashLen = 0.07, gapLen = 0.045, mat = dashLineMat) {{
      addDashedPolyline([p1, p2], dashLen, gapLen, mat);
    }}

    // 圆弧虚线生成函数
    function addDashedArc(radius, yHeight, thStart, thEnd, numSteps = 40, dashLen = 0.07, gapLen = 0.045, mat = dashLineMat) {{
      const pts = [];
      for (let i = 0; i <= numSteps; i++) {{
        const t = thStart + (thEnd - thStart) * (i / numSteps);
        pts.push(new THREE.Vector3(radius * Math.cos(t), yHeight, -radius * Math.sin(t)));
      }}
      addDashedPolyline(pts, dashLen, gapLen, mat);
    }}

    // -------------------------------------------------------------
    // 构建八分割网格剖分线
    // -------------------------------------------------------------
    function add8CellGridLines(rIn, rOut, h, deltaDeg) {{
      const thMax = deltaDeg * Math.PI / 180.0;
      const thHalf = thMax / 2.0;
      const rMid = (rIn + rOut) / 2.0;
      const yBot = -h / 2.0;
      const yMid = 0.0;
      const yTop = h / 2.0;

      // 1. 前截面 (th = thMax): 田字形
      // 竖中线 (r = rMid)
      addDashedLine(
        new THREE.Vector3(rMid * Math.cos(thMax), yBot, -rMid * Math.sin(thMax)),
        new THREE.Vector3(rMid * Math.cos(thMax), yTop, -rMid * Math.sin(thMax))
      );
      // 横中线 (y = yMid)
      addDashedLine(
        new THREE.Vector3(rIn * Math.cos(thMax), yMid, -rIn * Math.sin(thMax)),
        new THREE.Vector3(rOut * Math.cos(thMax), yMid, -rOut * Math.sin(thMax))
      );

      // 2. 角度正中截面 (th = thHalf): 砍一刀镜像截面
      // 上棱
      addDashedLine(
        new THREE.Vector3(rIn * Math.cos(thHalf), yTop, -rIn * Math.sin(thHalf)),
        new THREE.Vector3(rOut * Math.cos(thHalf), yTop, -rOut * Math.sin(thHalf))
      );
      // 外棱
      addDashedLine(
        new THREE.Vector3(rOut * Math.cos(thHalf), yBot, -rOut * Math.sin(thHalf)),
        new THREE.Vector3(rOut * Math.cos(thHalf), yTop, -rOut * Math.sin(thHalf))
      );
      // 内棱
      addDashedLine(
        new THREE.Vector3(rIn * Math.cos(thHalf), yBot, -rIn * Math.sin(thHalf)),
        new THREE.Vector3(rIn * Math.cos(thHalf), yTop, -rIn * Math.sin(thHalf))
      );
      // 中截面内部竖中线
      addDashedLine(
        new THREE.Vector3(rMid * Math.cos(thHalf), yBot, -rMid * Math.sin(thHalf)),
        new THREE.Vector3(rMid * Math.cos(thHalf), yTop, -rMid * Math.sin(thHalf))
      );
      // 中截面内部横中线
      addDashedLine(
        new THREE.Vector3(rIn * Math.cos(thHalf), yMid, -rIn * Math.sin(thHalf)),
        new THREE.Vector3(rOut * Math.cos(thHalf), yMid, -rOut * Math.sin(thHalf))
      );

      // 3. 径向贯通延伸线 (r = rMid 贯通整个实体)
      // 顶面弧线 (y = yTop, r = rMid)
      addDashedArc(rMid, yTop, 0.0, thMax);
      // 中截面弧线 (y = yMid, r = rMid)
      addDashedArc(rMid, yMid, 0.0, thMax);

      // 4. 水平贯通延伸线 (y = yMid 贯通整个实体)
      // 外圆柱面弧线 (r = rOut, y = yMid)
      addDashedArc(rOut, yMid, 0.0, thMax);
      // 内圆柱面弧线 (r = rIn, y = yMid)
      addDashedArc(rIn, yMid, 0.0, thMax);

      // 5. 后截面 (th = 0.0) 贯通终止线
      // 顶面径向线在 th = 0.0 处已有轮廓，补充内部线
      addDashedLine(
        new THREE.Vector3(rMid, yBot, 0.0),
        new THREE.Vector3(rMid, yTop, 0.0)
      );
      addDashedLine(
        new THREE.Vector3(rIn, yMid, 0.0),
        new THREE.Vector3(rOut, yMid, 0.0)
      );
    }}

    // =============================================================
    // 1. 变换前的几何体 (右侧，较大，轮廓加粗黑色)
    // =============================================================
    const geo0 = createRingSectorGeometry({rin_0}, {rout_0}, {h0});
    const mesh0 = new THREE.Mesh(geo0, whiteMat);
    scene.add(mesh0);

    const edge0 = new THREE.EdgesGeometry(geo0, 15);
    const pos0 = edge0.attributes.position;
    const tubeR0 = 0.030; // 明显较粗的轮廓
    for (let i = 0; i < pos0.count; i += 2) {{
      const p1 = new THREE.Vector3(pos0.getX(i), pos0.getY(i), pos0.getZ(i));
      const p2 = new THREE.Vector3(pos0.getX(i+1), pos0.getY(i+1), pos0.getZ(i+1));
      const cyl = createCylinderBetweenPoints(p1, p2, tubeR0, boldBlackTube);
      if (cyl) scene.add(cyl);
    }}

    // 右外轮廓母线
    const th0 = {theta_sil0};
    const p1_0 = new THREE.Vector3({rout_0} * Math.cos(th0), -{h0}/2, -{rout_0} * Math.sin(th0));
    const p2_0 = new THREE.Vector3({rout_0} * Math.cos(th0),  {h0}/2, -{rout_0} * Math.sin(th0));
    scene.add(createCylinderBetweenPoints(p1_0, p2_0, tubeR0, boldBlackTube));

    // 右实体八分割网格虚线
    add8CellGridLines({rin_0}, {rout_0}, {h0}, {delta_theta_deg});

    // =============================================================
    // 2. 变换后的几何体 (左侧，较小，轮廓更细/更浅)
    // =============================================================
    const geoS = createRingSectorGeometry({rin_s}, {rout_s}, {h_s});
    const meshS = new THREE.Mesh(geoS, whiteMat);
    scene.add(meshS);

    const edgeS = new THREE.EdgesGeometry(geoS, 15);
    const posS = edgeS.attributes.position;
    const tubeRS = 0.016; // 明显更细的轮廓
    for (let i = 0; i < posS.count; i += 2) {{
      const p1 = new THREE.Vector3(posS.getX(i), posS.getY(i), posS.getZ(i));
      const p2 = new THREE.Vector3(posS.getX(i+1), posS.getY(i+1), posS.getZ(i+1));
      const cyl = createCylinderBetweenPoints(p1, p2, tubeRS, lightSlateTube);
      if (cyl) scene.add(cyl);
    }}

    // 左外轮廓母线
    const thS = {theta_silS};
    const p1_s = new THREE.Vector3({rout_s} * Math.cos(thS), -{h_s}/2, -{rout_s} * Math.sin(thS));
    const p2_s = new THREE.Vector3({rout_s} * Math.cos(thS),  {h_s}/2, -{rout_s} * Math.sin(thS));
    scene.add(createCylinderBetweenPoints(p1_s, p2_s, tubeRS, lightSlateTube));

    // 左实体八分割网格虚线
    add8CellGridLines({rin_s}, {rout_s}, {h_s}, {delta_theta_deg});

    renderer.render(scene, camera);
  </script>
</body>
</html>
"""

hpath = os.path.join(SCRATCH, "task3_2_2_1_render.html")
rpath = os.path.join(SCRATCH, "task3_2_2_1_raw.png")

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
base_img = img.crop(crop_box).transpose(Image.FLIP_LEFT_RIGHT)
cw, ch = base_img.size

# Matplotlib 高保真矢量合成
plt.rcParams['mathtext.fontset'] = 'cm'
plt.rcParams['font.serif'] = ['Times New Roman', 'DejaVu Serif']
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'DejaVu Sans']

fig, ax = plt.subplots(figsize=(10, 10), dpi=300)
ax.imshow(base_img, extent=[0, cw, ch, 0])
ax.set_xlim(0, cw)
ax.set_ylim(ch, 0)
ax.axis('off')

# 截面下底边投影斜率 (m = 0.178, 夹角约 10.1°)
m = 0.178
th = np.arctan(m)
u = np.array([np.cos(th), np.sin(th)])

# 1. 左下角柱坐标系 (+z, +r, +\theta)
orig_x = cw * 0.18
orig_y = ch * 0.82
length = cw * 0.13

# +z 轴
z_top = (orig_x, orig_y - length * 1.15)
ax.annotate('', xy=z_top, xytext=(orig_x, orig_y),
            arrowprops=dict(arrowstyle='->', color='#0F172A', lw=2.2, mutation_scale=18), zorder=20)
ax.text(z_top[0], z_top[1] - 16, r'$+z$', fontsize=17, fontweight='bold', color='#0F172A', ha='center', va='bottom')

# +r 轴 (严格与截面底边及演化箭头平行)
r_tip = (orig_x + length * u[0], orig_y + length * u[1])

# 扇形面 +\theta
th_start = -np.radians(35)
th_angles = np.linspace(th_start, th, 50)
arc_x = orig_x + (length * 0.95) * np.cos(th_angles)
arc_y = orig_y + (length * 0.95) * np.sin(th_angles) * 0.48
poly_x = [orig_x] + list(arc_x) + [orig_x]
poly_y = [orig_y] + list(arc_y) + [orig_y]

ax.fill(poly_x, poly_y, color='#F1F5F9', alpha=0.90, zorder=15)
ax.plot(poly_x, poly_y, color='#475569', linewidth=1.4, zorder=16)

mid_th = (th_start + th) / 2
th_x = orig_x + (length * 0.58) * np.cos(mid_th)
th_y = orig_y + (length * 0.58) * np.sin(mid_th) * 0.48
ax.text(th_x, th_y, r'$+\theta$', fontsize=14, fontstyle='italic', color='#1E293B', ha='center', va='center', zorder=22)

ax.annotate('', xy=r_tip, xytext=(orig_x, orig_y),
            arrowprops=dict(arrowstyle='->', color='#0F172A', lw=2.2, mutation_scale=18), zorder=20)
ax.text(r_tip[0] + 16, r_tip[1] + 4, r'$+r$', fontsize=17, fontweight='bold', color='#0F172A', ha='left', va='center')

# 2. 直线演化箭头 (严格平行于底边，从变换前指向变换后，零重叠)
p_start = (720, 960)
p_end = (540, 960 - 180 * m)
arr = FancyArrowPatch(p_start, p_end,
                       connectionstyle='arc3,rad=0',
                       arrowstyle='-|>,head_length=9.0,head_width=5.5',
                       color='#0F172A', lw=2.4, zorder=30)
ax.add_patch(arr)

temp_comp_path = os.path.join(SCRATCH, "task3_2_2_1_composite.png")
fig.savefig(temp_comp_path, dpi=300, bbox_inches='tight', pad_inches=0.05)
plt.close(fig)

# 3. 全局自动对称裁剪与平衡构图 (四边均等呼吸空间)
comp_img = Image.open(temp_comp_path)
comp_arr = np.array(comp_img.convert('L'))
non_w = comp_arr < 250
ys, xs = np.where(non_w)

cx_comp = int((xs.min() + xs.max()) / 2)
cy_comp = int((ys.min() + ys.max()) / 2)
span_comp = max(xs.max() - xs.min(), ys.max() - ys.min())
pad_comp = int(span_comp * 0.12)
R_final = int(span_comp / 2 + pad_comp)

box_final = (cx_comp - R_final, cy_comp - R_final, cx_comp + R_final, cy_comp + R_final)
final_img = comp_img.crop(box_final)

# 输出路径
out_file = os.path.join(OUTPUT_DIR, "task3_2_2_1_final.png")
final_img.save(out_file)

artifact_dir = r"C:\Users\kqdx\.gemini\antigravity\brain\ce5f745e-eae3-4eca-9e3f-87c5c965cace"
art_file = os.path.join(artifact_dir, "task3_2_2_1_final.png")
final_img.save(art_file)

print(f"Task 3.2.2.1 最终正式图已生成: {out_file}")
print(f"Artifact 图像已同步: {art_file}")
