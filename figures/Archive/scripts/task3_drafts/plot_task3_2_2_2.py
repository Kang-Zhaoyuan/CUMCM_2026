import os
import subprocess
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch
from PIL import Image

SCRATCH = r"C:\Users\kqdx\.gemini\antigravity\brain\ce5f745e-eae3-4eca-9e3f-87c5c965cace\scratch"
three_js_path = r"D:\HIT\数模2026\eda_figures\Archive\scripts\three.min.js".replace('\\', '/')
edge_exe = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

W, H = 2600, 2600
delta_theta_deg = 52.0

h_common = 0.85

# 变换前 (右)
r0 = 4.85
a0 = 0.85
rin_0 = r0 - a0 / 2.0
rout_0 = r0 + a0 / 2.0
h0 = h_common

# 变换后 (左)
r_s = 3.10
a_s = a0 * (r_s / r0)
rin_s = r_s - a_s / 2.0
rout_s = r_s + a_s / 2.0
h_s = h_common

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

    const boldBlackTube = new THREE.MeshBasicMaterial({{ color: 0x111111 }});
    const lightBlackTube = new THREE.MeshBasicMaterial({{ color: 0x555555 }});
    const dashLineMat = new THREE.LineBasicMaterial({{ color: 0x777777, linewidth: 2 }});

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

    function addDashedPolyline(points, dashLen = 0.060, gapLen = 0.040, mat = dashLineMat) {{
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

    function addDashedLine(p1, p2, dashLen = 0.060, gapLen = 0.040, mat = dashLineMat) {{
      addDashedPolyline([p1, p2], dashLen, gapLen, mat);
    }}

    function addDashedArc(radius, yHeight, thStart, thEnd, numSteps = 40, dashLen = 0.060, gapLen = 0.040, mat = dashLineMat) {{
      const pts = [];
      for (let i = 0; i <= numSteps; i++) {{
        const t = thStart + (thEnd - thStart) * (i / numSteps);
        pts.push(new THREE.Vector3(radius * Math.cos(t), yHeight, -radius * Math.sin(t)));
      }}
      addDashedPolyline(pts, dashLen, gapLen, mat);
    }}

    // 三个方向全三分剖分: 径向2刀，高度2刀，圆心角2刀 (3x3x3=27)
    function add3x3x3GridLines(rIn, rOut, h, deltaDeg) {{
      const thMax = deltaDeg * Math.PI / 180.0;
      
      const dr = rOut - rIn;
      const r_cuts = [rIn + dr / 3.0, rIn + 2.0 * dr / 3.0];
      
      const yBot = -h / 2.0;
      const yTop = h / 2.0;
      const y_cuts = [-h / 6.0, h / 6.0];
      
      const th_cuts = [thMax / 3.0, 2.0 * thMax / 3.0];

      // 1. 前截面 (th = thMax): 九宫格剖分
      for (const yc of y_cuts) {{
        addDashedLine(
          new THREE.Vector3(rIn * Math.cos(thMax), yc, -rIn * Math.sin(thMax)),
          new THREE.Vector3(rOut * Math.cos(thMax), yc, -rOut * Math.sin(thMax))
        );
      }}
      for (const rc of r_cuts) {{
        addDashedLine(
          new THREE.Vector3(rc * Math.cos(thMax), yBot, -rc * Math.sin(thMax)),
          new THREE.Vector3(rc * Math.cos(thMax), yTop, -rc * Math.sin(thMax))
        );
      }}

      // 2. 内部两道角度切片截面 (th = th_cuts[0] 与 th_cuts[1])
      for (const thc of th_cuts) {{
        addDashedLine(
          new THREE.Vector3(rIn * Math.cos(thc), yTop, -rIn * Math.sin(thc)),
          new THREE.Vector3(rOut * Math.cos(thc), yTop, -rOut * Math.sin(thc))
        );
        addDashedLine(
          new THREE.Vector3(rOut * Math.cos(thc), yBot, -rOut * Math.sin(thc)),
          new THREE.Vector3(rOut * Math.cos(thc), yTop, -rOut * Math.sin(thc))
        );
        addDashedLine(
          new THREE.Vector3(rIn * Math.cos(thc), yBot, -rIn * Math.sin(thc)),
          new THREE.Vector3(rIn * Math.cos(thc), yTop, -rIn * Math.sin(thc))
        );
        addDashedLine(
          new THREE.Vector3(rIn * Math.cos(thc), yBot, -rIn * Math.sin(thc)),
          new THREE.Vector3(rOut * Math.cos(thc), yBot, -rOut * Math.sin(thc))
        );

        for (const yc of y_cuts) {{
          addDashedLine(
            new THREE.Vector3(rIn * Math.cos(thc), yc, -rIn * Math.sin(thc)),
            new THREE.Vector3(rOut * Math.cos(thc), yc, -rOut * Math.sin(thc))
          );
        }}
        for (const rc of r_cuts) {{
          addDashedLine(
            new THREE.Vector3(rc * Math.cos(thc), yBot, -rc * Math.sin(thc)),
            new THREE.Vector3(rc * Math.cos(thc), yTop, -rc * Math.sin(thc))
          );
        }}
      }}

      // 3. 贯通同心圆弧
      for (const rc of r_cuts) {{
        addDashedArc(rc, yTop, 0.0, thMax);
      }}

      const all_radii = [rIn, r_cuts[0], r_cuts[1], rOut];
      for (const yc of y_cuts) {{
        for (const r of all_radii) {{
          addDashedArc(r, yc, 0.0, thMax);
        }}
      }}

      // 4. 后截面 (th = 0.0)
      for (const yc of y_cuts) {{
        addDashedLine(
          new THREE.Vector3(rIn, yc, 0.0),
          new THREE.Vector3(rOut, yc, 0.0)
        );
      }}
      for (const rc of r_cuts) {{
        addDashedLine(
          new THREE.Vector3(rc, yBot, 0.0),
          new THREE.Vector3(rc, yTop, 0.0)
        );
      }}
    }}

    // 变换前 (右)
    const geo0 = createRingSectorGeometry({rin_0}, {rout_0}, {h0});
    const mesh0 = new THREE.Mesh(geo0, whiteMat);
    scene.add(mesh0);

    const edge0 = new THREE.EdgesGeometry(geo0, 15);
    const pos0 = edge0.attributes.position;
    const tubeR0 = 0.030;
    for (let i = 0; i < pos0.count; i += 2) {{
      const p1 = new THREE.Vector3(pos0.getX(i), pos0.getY(i), pos0.getZ(i));
      const p2 = new THREE.Vector3(pos0.getX(i+1), pos0.getY(i+1), pos0.getZ(i+1));
      const cyl = createCylinderBetweenPoints(p1, p2, tubeR0, boldBlackTube);
      if (cyl) scene.add(cyl);
    }}

    const th0 = {theta_sil0};
    const p1_0 = new THREE.Vector3({rout_0} * Math.cos(th0), -{h0}/2, -{rout_0} * Math.sin(th0));
    const p2_0 = new THREE.Vector3({rout_0} * Math.cos(th0),  {h0}/2, -{rout_0} * Math.sin(th0));
    scene.add(createCylinderBetweenPoints(p1_0, p2_0, tubeR0, boldBlackTube));

    add3x3x3GridLines({rin_0}, {rout_0}, {h0}, {delta_theta_deg});

    // 变换后 (左)
    const geoS = createRingSectorGeometry({rin_s}, {rout_s}, {h_s});
    const meshS = new THREE.Mesh(geoS, whiteMat);
    scene.add(meshS);

    const edgeS = new THREE.EdgesGeometry(geoS, 15);
    const posS = edgeS.attributes.position;
    const tubeRS = 0.016;
    for (let i = 0; i < posS.count; i += 2) {{
      const p1 = new THREE.Vector3(posS.getX(i), posS.getY(i), posS.getZ(i));
      const p2 = new THREE.Vector3(posS.getX(i+1), posS.getY(i+1), posS.getZ(i+1));
      const cyl = createCylinderBetweenPoints(p1, p2, tubeRS, lightBlackTube);
      if (cyl) scene.add(cyl);
    }}

    const thS = {theta_silS};
    const p1_s = new THREE.Vector3({rout_s} * Math.cos(thS), -{h_s}/2, -{rout_s} * Math.sin(thS));
    const p2_s = new THREE.Vector3({rout_s} * Math.cos(thS),  {h_s}/2, -{rout_s} * Math.sin(thS));
    scene.add(createCylinderBetweenPoints(p1_s, p2_s, tubeRS, lightBlackTube));

    add3x3x3GridLines({rin_s}, {rout_s}, {h_s}, {delta_theta_deg});

    renderer.render(scene, camera);
  </script>
</body>
</html>
"""

hpath = os.path.join(SCRATCH, "test_task3_2_2_3.html")
rpath = os.path.join(SCRATCH, "test_task3_2_2_3_raw.png")

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

plt.rcParams['mathtext.fontset'] = 'cm'
plt.rcParams['font.serif'] = ['Times New Roman', 'DejaVu Serif']
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'DejaVu Sans']

fig, ax = plt.subplots(figsize=(10, 10), dpi=300)
ax.imshow(base_img, extent=[0, cw, ch, 0])
ax.set_xlim(0, cw)
ax.set_ylim(ch, 0)
ax.axis('off')

m = 0.178
th = np.arctan(m)
u = np.array([np.cos(th), np.sin(th)])

# 1. 左下角柱坐标系 (+z, +r)
orig_x = cw * 0.16
orig_y = ch * 0.65
length = cw * 0.115

z_top = (orig_x, orig_y - length * 1.15)
r_tip = (orig_x + length * u[0], orig_y + length * u[1])

# 零缝隙 miter 折线绘制两轴
ax.plot([z_top[0], orig_x, r_tip[0]], [z_top[1], orig_y, r_tip[1]],
        color='#111111', lw=2.2, solid_joinstyle='miter', solid_capstyle='projecting', zorder=20)

# 箭头端点使用 shrinkA=0, shrinkB=0 确保与主干无缝接合
ax.annotate('', xy=z_top, xytext=(orig_x, z_top[1] + 12),
            arrowprops=dict(arrowstyle='->', color='#111111', lw=2.2, mutation_scale=16, shrinkA=0, shrinkB=0), zorder=21)
ax.text(z_top[0], z_top[1] - 16, r'$+z$', fontsize=17, fontweight='bold', color='#111111', ha='center', va='bottom')

ax.annotate('', xy=r_tip, xytext=(r_tip[0] - 12 * u[0], r_tip[1] - 12 * u[1]),
            arrowprops=dict(arrowstyle='->', color='#111111', lw=2.2, mutation_scale=16, shrinkA=0, shrinkB=0), zorder=21)
ax.text(r_tip[0] + 16, r_tip[1] + 4, r'$+r$', fontsize=17, fontweight='bold', color='#111111', ha='left', va='center')

# 2. 细巧的直线演化箭头 (下移至 y=1000，完美留白零重叠，精致内敛)
# start: (730, 1000), end: (570, 971.5), L = 160
p_start = (730, 1000)
p_end = (570, 1000 - 160 * m)
arr_fine = FancyArrowPatch(p_start, p_end,
                           connectionstyle='arc3,rad=0',
                           arrowstyle='-|>,head_length=6.5,head_width=3.8',
                           color='#111111', lw=1.35, zorder=30)
ax.add_patch(arr_fine)

temp_path = os.path.join(SCRATCH, "test_task3_2_2_3_comp.png")
fig.savefig(temp_path, dpi=300, bbox_inches='tight', pad_inches=0.05)
plt.close(fig)

# 3. 紧凑扁平型裁切
c_img = Image.open(temp_path)
c_arr = np.array(c_img.convert('L'))
ys, xs = np.where(c_arr < 250)

pad_x = int((xs.max() - xs.min()) * 0.06)
pad_y = int((ys.max() - ys.min()) * 0.08)

cropped = c_img.crop((xs.min() - pad_x, ys.min() - pad_y, xs.max() + pad_x, ys.max() + pad_y))
out_final = os.path.join(SCRATCH, "test_task3_2_2_3_final.png")
cropped.save(out_final)
print(f"Saved test_task3_2_2_3_final.png: size={cropped.size}, aspect_ratio={cropped.size[0]/cropped.size[1]:.2f}")
