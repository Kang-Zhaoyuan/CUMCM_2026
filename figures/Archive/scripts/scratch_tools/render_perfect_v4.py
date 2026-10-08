import os
import subprocess
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import shutil

SCRATCH = r"C:\Users\kqdx\.gemini\antigravity\brain\984f8f9b-1caf-4e5e-a827-7c48f241b73b\scratch"
EDA_DIR = r"D:\HIT\数模2026\eda_figures"
ART_DIR = r"C:\Users\kqdx\.gemini\antigravity\brain\984f8f9b-1caf-4e5e-a827-7c48f241b73b"

three_js_path = os.path.join(EDA_DIR, "three.min.js").replace('\\', '/')
edge_exe = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

W_raw, H_raw = 2600, 2600
scale_factor = 1.45

target = np.array([3.30, 0.00, 0.00])
cam_orig = np.array([-0.01, 1.86, -8.91])
cam_pos = target + (cam_orig - target) * scale_factor

C_x, C_y, C_z = cam_pos
D = np.sqrt(C_x**2 + C_z**2)
phi = np.arctan2(-C_z, C_x)

alpha_large = np.arccos(6.15 / D)
theta_large = phi - alpha_large

alpha_mother = np.arccos(4.70 / D)
theta_mother = phi - alpha_mother

alpha_small = np.arccos(3.25 / D)
theta_small = phi - alpha_small

def generate_base_3d(output_png_path, s_top=0.13, s_right=0.13, s_bot=0.02, padding=320):
    html_content = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <script src="{three_js_path}"></script>
  <style>
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    body {{ background: #FFFFFF; overflow: hidden; width: {W_raw}px; height: {H_raw}px; }}
    #container {{ width: {W_raw}px; height: {H_raw}px; }}
  </style>
</head>
<body>
  <div id="container"></div>
  <script>
    const width = {W_raw};
    const height = {H_raw};

    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0xFFFFFF);

    const camera = new THREE.PerspectiveCamera(42, width / height, 0.1, 100);
    camera.position.set({cam_pos[0]:.4f}, {cam_pos[1]:.4f}, {cam_pos[2]:.4f});
    const target = new THREE.Vector3({target[0]:.4f}, {target[1]:.4f}, {target[2]:.4f});
    camera.lookAt(target);

    const renderer = new THREE.WebGLRenderer({{ antialias: true, preserveDrawingBuffer: true }});
    renderer.setSize(width, height);
    renderer.setPixelRatio(1);
    renderer.setClearColor(0xFFFFFF, 1.0);
    document.getElementById('container').appendChild(renderer.domElement);

    const r_small_in = 2.10;
    const r_small_out = 3.25;
    const delta_r = 1.15;
    const delta_z = 1.10;
    const gap = 0.30;

    const r_mother_in = r_small_out + gap; // 3.55
    const r_mother_out = r_mother_in + delta_r; // 4.70

    const r_large_in = r_mother_out + gap; // 5.00
    const r_large_out = r_large_in + delta_r; // 6.15

    const y_far = delta_z + gap; // 1.40
    const y_near = -(delta_z + gap); // -1.40

    function createRingSectorGeometry(rIn, rOut, h) {{
      const startAngle = 0.0;
      const endAngle = (60.0 * Math.PI) / 180.0;

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

    function createLineBetweenPoints(p1, p2, color = 0x000000, linewidth = 1) {{
      const geom = new THREE.BufferGeometry().setFromPoints([p1, p2]);
      return new THREE.Line(geom, new THREE.LineBasicMaterial({{ color: color, linewidth: linewidth }}));
    }}

    function createCylinderBetweenPoints(p1, p2, radius, color = 0x000000) {{
      const dir = new THREE.Vector3().subVectors(p2, p1);
      const len = dir.length();
      if (len < 1e-4) return null;
      const geom = new THREE.CylinderGeometry(radius, radius, len, 12);
      const mat = new THREE.MeshBasicMaterial({{ color: color }});
      const cyl = new THREE.Mesh(geom, mat);
      cyl.position.copy(p1).addScaledVector(dir, 0.5);
      cyl.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), dir.clone().normalize());
      return cyl;
    }}

    const bodyMaterial = new THREE.MeshBasicMaterial({{
      color: 0xFFFFFF,
      polygonOffset: true,
      polygonOffsetFactor: 1,
      polygonOffsetUnits: 1
    }});

    const thinEdgeMaterial = new THREE.LineBasicMaterial({{ color: 0x000000, linewidth: 1 }});

    const rings = [
      {{ rIn: r_mother_in, rOut: r_mother_out, y: 0.0, isMother: true }},
      {{ rIn: r_mother_in, rOut: r_mother_out, y: y_far, isMother: false }},
      {{ rIn: r_mother_in, rOut: r_mother_out, y: y_near, isMother: false }},
      {{ rIn: r_small_in,  rOut: r_small_out,  y: 0.0, isMother: false }},
      {{ rIn: r_large_in,  rOut: r_large_out,  y: 0.0, isMother: false }}
    ];

    rings.forEach(spec => {{
      const geo = createRingSectorGeometry(spec.rIn, spec.rOut, delta_z);
      const mesh = new THREE.Mesh(geo, bodyMaterial);
      mesh.position.y = spec.y;
      scene.add(mesh);

      const edgeGeo = new THREE.EdgesGeometry(geo, 20);
      if (spec.isMother) {{
        const tubeR = 0.024;
        const posAttr = edgeGeo.attributes.position;
        for (let i = 0; i < posAttr.count; i += 2) {{
          const p1 = new THREE.Vector3(posAttr.getX(i), posAttr.getY(i) + spec.y, posAttr.getZ(i));
          const p2 = new THREE.Vector3(posAttr.getX(i+1), posAttr.getY(i+1) + spec.y, posAttr.getZ(i+1));
          const cyl = createCylinderBetweenPoints(p1, p2, tubeR);
          if (cyl) scene.add(cyl);
        }}
      }} else {{
        const lineSegments = new THREE.LineSegments(edgeGeo, thinEdgeMaterial);
        lineSegments.position.y = spec.y;
        scene.add(lineSegments);
      }}
    }});

    // Silhouettes
    const th_large = {theta_large};
    scene.add(createLineBetweenPoints(
      new THREE.Vector3(r_large_out * Math.cos(th_large), -delta_z / 2, -r_large_out * Math.sin(th_large)),
      new THREE.Vector3(r_large_out * Math.cos(th_large),  delta_z / 2, -r_large_out * Math.sin(th_large))
    ));

    const th_mother = {theta_mother};
    scene.add(createLineBetweenPoints(
      new THREE.Vector3(r_mother_out * Math.cos(th_mother), y_far - delta_z / 2, -r_mother_out * Math.sin(th_mother)),
      new THREE.Vector3(r_mother_out * Math.cos(th_mother), y_far + delta_z / 2, -r_mother_out * Math.sin(th_mother))
    ));

    const cyl_mother = createCylinderBetweenPoints(
      new THREE.Vector3(r_mother_out * Math.cos(th_mother), -delta_z / 2, -r_mother_out * Math.sin(th_mother)),
      new THREE.Vector3(r_mother_out * Math.cos(th_mother),  delta_z / 2, -r_mother_out * Math.sin(th_mother)),
      0.024
    );
    if (cyl_mother) scene.add(cyl_mother);

    scene.add(createLineBetweenPoints(
      new THREE.Vector3(r_mother_out * Math.cos(th_mother), y_near - delta_z / 2, -r_mother_out * Math.sin(th_mother)),
      new THREE.Vector3(r_mother_out * Math.cos(th_mother), y_near + delta_z / 2, -r_mother_out * Math.sin(th_mother))
    ));

    const th_small = {theta_small};
    scene.add(createLineBetweenPoints(
      new THREE.Vector3(r_small_out * Math.cos(th_small), -delta_z / 2, -r_small_out * Math.sin(th_small)),
      new THREE.Vector3(r_small_out * Math.cos(th_small),  delta_z / 2, -r_small_out * Math.sin(th_small))
    ));

    // Standard Red Gradient Generator
    function makeRedGradientTexture(alphaStart = 0.12, alphaEnd = 1.0, hexColor = '235, 15, 15') {{
      const c = document.createElement('canvas');
      c.width = 256; c.height = 16;
      const ctx = c.getContext('2d');
      const grad = ctx.createLinearGradient(0, 0, 256, 0);
      grad.addColorStop(0.00, `rgba(${{hexColor}}, ${{alphaStart}})`);
      grad.addColorStop(0.35, `rgba(${{hexColor}}, ${{alphaStart + (alphaEnd - alphaStart) * 0.45}})`);
      grad.addColorStop(0.70, `rgba(${{hexColor}}, ${{alphaStart + (alphaEnd - alphaStart) * 0.85}})`);
      grad.addColorStop(1.00, `rgba(${{hexColor}}, ${{alphaEnd}})`);
      ctx.fillStyle = grad;
      ctx.fillRect(0, 0, 256, 16);
      const tex = new THREE.CanvasTexture(c);
      return tex;
    }}

    const defaultRedTex = makeRedGradientTexture(0.12, 1.0, '235, 20, 20');

    // Cut plane geometry basis
    const th_cut = (60.0 * Math.PI) / 180.0;
    const e_r = new THREE.Vector3(Math.cos(th_cut), 0, -Math.sin(th_cut));
    const e_y = new THREE.Vector3(0, 1, 0);
    const n_cam = new THREE.Vector3(-Math.sin(th_cut), 0, -Math.cos(th_cut)).normalize();

    function addFlaredArrow(pStart, pEnd, wTail, wNeck, wHead, headRatio, power, lift = 0.02) {{
      const dir = new THREE.Vector3().subVectors(pEnd, pStart);
      const L = dir.length();
      const u = dir.clone().normalize();
      const v = new THREE.Vector3().crossVectors(n_cam, u).normalize();

      const Lhead = L * headRatio;
      const Lshaft = L - Lhead;
      const segs = 36;

      const vertices = [];
      const uvs = [];
      const indices = [];

      for (let i = 0; i <= segs; i++) {{
        const t = i / segs;
        const x = t * Lshaft;
        const w = (wNeck / 2) + ((wTail - wNeck) / 2) * Math.pow(1 - t, power);
        const uVal = t * (Lshaft / L);

        const pT = pStart.clone().addScaledVector(u, x).addScaledVector(v, w).addScaledVector(n_cam, lift);
        const pB = pStart.clone().addScaledVector(u, x).addScaledVector(v, -w).addScaledVector(n_cam, lift);

        vertices.push(pT.x, pT.y, pT.z);
        uvs.push(uVal, 1.0);
        vertices.push(pB.x, pB.y, pB.z);
        uvs.push(uVal, 0.0);
      }}

      for (let i = 0; i < segs; i++) {{
        const i0 = 2 * i;
        const i1 = 2 * i + 1;
        const i2 = 2 * (i + 1);
        const i3 = 2 * (i + 1) + 1;

        indices.push(i0, i1, i2);
        indices.push(i2, i1, i3);
      }}

      // Arrowhead
      const baseIdx = vertices.length / 3;
      const pHeadTop = pStart.clone().addScaledVector(u, Lshaft).addScaledVector(v, wHead / 2).addScaledVector(n_cam, lift);
      const pHeadBot = pStart.clone().addScaledVector(u, Lshaft).addScaledVector(v, -wHead / 2).addScaledVector(n_cam, lift);
      const pTip = pStart.clone().addScaledVector(u, L).addScaledVector(n_cam, lift);

      vertices.push(pHeadTop.x, pHeadTop.y, pHeadTop.z);
      uvs.push(Lshaft / L, 1.0);
      vertices.push(pHeadBot.x, pHeadBot.y, pHeadBot.z);
      uvs.push(Lshaft / L, 0.0);
      vertices.push(pTip.x, pTip.y, pTip.z);
      uvs.push(1.0, 0.5);

      indices.push(baseIdx, baseIdx + 1, baseIdx + 2);

      const geom = new THREE.BufferGeometry();
      geom.setAttribute('position', new THREE.Float32BufferAttribute(vertices, 3));
      geom.setAttribute('uv', new THREE.Float32BufferAttribute(uvs, 2));
      geom.setIndex(indices);
      geom.computeVertexNormals();

      const mat = new THREE.MeshBasicMaterial({{
        map: defaultRedTex,
        transparent: true,
        side: THREE.DoubleSide,
        depthTest: true
      }});
      scene.add(new THREE.Mesh(geom, mat));
    }}

    const r_mid = (r_mother_in + r_mother_out) / 2.0;
    const cos_c = Math.cos(th_cut);
    const sin_c = Math.sin(th_cut);

    const s_top = {s_top};
    const s_right = {s_right};
    const s_bot = {s_bot};

    // 1. Large -> Mother
    addFlaredArrow(
      new THREE.Vector3((5.35 - s_right) * cos_c, 0.0, -(5.35 - s_right) * sin_c),
      new THREE.Vector3((4.40 - s_right) * cos_c, 0.0, -(4.40 - s_right) * sin_c),
      0.40, 0.085, 0.22, 0.30, 3.0, 0.02
    );

    // 2. Far -> Mother
    addFlaredArrow(
      new THREE.Vector3(r_mid * cos_c, 1.20 - s_top, -r_mid * sin_c),
      new THREE.Vector3(r_mid * cos_c, 0.25 - s_top, -r_mid * sin_c),
      0.40, 0.085, 0.22, 0.30, 3.0, 0.02
    );

    // 3. Mother -> Small
    addFlaredArrow(
      new THREE.Vector3(3.80 * cos_c, 0.0, -3.80 * sin_c),
      new THREE.Vector3(3.22 * cos_c, 0.0, -3.22 * sin_c),
      0.22, 0.050, 0.14, 0.30, 3.0, 0.02
    );

    // 4. Mother -> Near (Shifted upwards: s_bot = 0.02)
    addFlaredArrow(
      new THREE.Vector3(r_mid * cos_c, -0.35 - s_bot, -r_mid * sin_c),
      new THREE.Vector3(r_mid * cos_c, -1.00 - s_bot, -r_mid * sin_c),
      0.22, 0.050, 0.14, 0.30, 3.0, 0.02
    );

    renderer.render(scene, camera);
  </script>
</body>
</html>
"""
    hpath = os.path.join(SCRATCH, "flared_refined.html")
    rpath = os.path.join(SCRATCH, "flared_refined_raw.png")

    with open(hpath, "w", encoding="utf-8") as f:
        f.write(html_content)

    norm_url = f"file:///{hpath.replace(os.sep, '/')}"
    subprocess.run([edge_exe, "--headless", f"--screenshot={rpath}", f"--window-size={W_raw},{H_raw}", norm_url], capture_output=True)

    C = cam_pos
    T = target
    up = np.array([0.0, 1.0, 0.0])

    w_cam = (T - C) / np.linalg.norm(T - C)
    r_cam = np.cross(w_cam, up); r_cam /= np.linalg.norm(r_cam)
    u_cam = np.cross(r_cam, w_cam); u_cam /= np.linalg.norm(u_cam)

    fov = 42.0
    f_proj = 1.0 / np.tan(np.radians(fov / 2.0))

    def to_screen(P):
        rel = P - C
        xc = np.dot(rel, r_cam)
        yc = np.dot(rel, u_cam)
        zc = np.dot(rel, w_cam)
        sx = (f_proj * xc / zc + 1.0) * 0.5 * W_raw
        sy = (1.0 - f_proj * yc / zc) * 0.5 * H_raw
        return sx, sy

    rin_m, rout_m, h_m = 3.55, 4.70, 1.10
    mother_pts = []
    for t in np.linspace(0.0, np.radians(60.0), 50):
        for r in [rin_m, rout_m]:
            for y in [-h_m / 2.0, h_m / 2.0]:
                P = np.array([r * np.cos(t), y, -r * np.sin(t)])
                mother_pts.append(to_screen(P))

    mother_pts = np.array(mother_pts)
    m_xmin, m_ymin = np.min(mother_pts, axis=0)
    m_xmax, m_ymax = np.max(mother_pts, axis=0)
    cx_mother = (m_xmin + m_xmax) / 2.0
    cy_mother = (m_ymin + m_ymax) / 2.0

    img = Image.open(rpath).convert("RGBA")
    arr = np.array(img.convert("L"))
    non_white = arr < 250
    y_idx, x_idx = np.where(non_white)

    dx1 = abs(np.min(x_idx) - cx_mother)
    dx2 = abs(np.max(x_idx) - cx_mother)
    dy1 = abs(np.min(y_idx) - cy_mother)
    dy2 = abs(np.max(y_idx) - cy_mother)

    R = int(np.ceil(max(dx1, dx2, dy1, dy2))) + padding
    crop_box = (
        int(round(cx_mother - R)),
        int(round(cy_mother - R)),
        int(round(cx_mother + R)),
        int(round(cy_mother + R))
    )

    canvas_size = 2 * R
    square_img = Image.new("RGBA", (canvas_size, canvas_size), (255, 255, 255, 255))
    src_x1 = max(0, crop_box[0])
    src_y1 = max(0, crop_box[1])
    src_x2 = min(W_raw, crop_box[2])
    src_y2 = min(H_raw, crop_box[3])

    cropped_part = img.crop((src_x1, src_y1, src_x2, src_y2))
    paste_x = src_x1 - crop_box[0]
    paste_y = src_y1 - crop_box[1]
    square_img.paste(cropped_part, (paste_x, paste_y))

    final_img = square_img.transpose(Image.FLIP_LEFT_RIGHT)
    final_img.save(output_png_path)
    print(f"Generated refined base image ({canvas_size}x{canvas_size}) -> {output_png_path}")
    return R, cx_mother, cy_mother

# Generate base with padding = 320 to comfortably accommodate the outer ring z-dimension text
base_img_path = os.path.join(EDA_DIR, "fvm_flux_flared_c2_refined.png")
R_val, cx_m, cy_m = generate_base_3d(base_img_path, s_top=0.13, s_right=0.13, s_bot=0.02, padding=320)

# Calculate coordinate mapping for new canvas:
# Old R was 897 (with padding 160). New R is R_val (with padding 320).
dR = R_val - 897
print(f"Shift delta dR = {dR}")

# =========================================================================
# 2. Render Annotations
# =========================================================================
img = Image.open(base_img_path)
W, H = img.size

fig, ax = plt.subplots(figsize=(12, 12), dpi=300)
ax.imshow(img)
ax.set_xlim(0, W)
ax.set_ylim(H, 0)
ax.axis('off')

plt.rcParams['mathtext.fontset'] = 'cm'
plt.rcParams['font.serif'] = ['Times New Roman', 'DejaVu Serif']
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'DejaVu Sans']

# -------------------------------------------------------------------------
# A. Radial Dimensioning on Near Ring (近环底部): r_{i+1/2} - r_{i-1/2}
# -------------------------------------------------------------------------
p_bi = np.array([627.3 + dR, 1533.0 + dR])
p_bo = np.array([909.6 + dR, 1633.8 + dR])
ext_len_r = 68
d_offset_r = 55

ax.plot([p_bi[0], p_bi[0]], [p_bi[1], p_bi[1] + ext_len_r],
        color='#333333', linestyle='--', linewidth=1.2, zorder=5)
ax.plot([p_bo[0], p_bo[0]], [p_bo[1], p_bo[1] + ext_len_r],
        color='#333333', linestyle='--', linewidth=1.2, zorder=5)

dim_r1 = p_bi + np.array([0, d_offset_r])
dim_r2 = p_bo + np.array([0, d_offset_r])

ax.annotate('', xy=dim_r1, xytext=dim_r2,
            arrowprops=dict(arrowstyle='<->', color='#000000', lw=1.5, shrinkA=0, shrinkB=0),
            zorder=6)

dim_mid_r = (dim_r1 + dim_r2) / 2
# Text placed cleanly below the extension line termination level, completely free of any lines
ax.text(dim_mid_r[0], p_bo[1] + ext_len_r + 28, r'$r_{i+1/2} - r_{i-1/2}$',
        fontsize=17, fontweight='bold', color='#000000', ha='center', va='top', zorder=7)

# -------------------------------------------------------------------------
# B. Axial Dimensioning on Outer Ring (E, 外环右侧轮廓素线): z_{j+1/2} - z_{j-1/2}
# -------------------------------------------------------------------------
p_sil_top = np.array([1594.6 + dR, 739.7 + dR])
p_sil_bot = np.array([1578.9 + dR, 1057.4 + dR])

ext_len_z = 60
d_offset_z = 40

ax.plot([p_sil_top[0], p_sil_top[0] + ext_len_z], [p_sil_top[1], p_sil_top[1]],
        color='#333333', linestyle='--', linewidth=1.2, zorder=5)
ax.plot([p_sil_bot[0], p_sil_bot[0] + ext_len_z], [p_sil_bot[1], p_sil_bot[1]],
        color='#333333', linestyle='--', linewidth=1.2, zorder=5)

dim_z1 = p_sil_top + np.array([d_offset_z, 0])
dim_z2 = p_sil_bot + np.array([d_offset_z, 0])

ax.annotate('', xy=dim_z1, xytext=dim_z2,
            arrowprops=dict(arrowstyle='<->', color='#000000', lw=1.5, shrinkA=0, shrinkB=0),
            zorder=6)

dim_mid_z = (dim_z1 + dim_z2) / 2
ax.text(dim_mid_z[0] + 16, dim_mid_z[1], r'$z_{j+1/2} - z_{j-1/2}$',
        fontsize=17, fontweight='bold', color='#000000', ha='left', va='center', zorder=7)

# -------------------------------------------------------------------------
# C. Coordinate System in Bottom-Left (3D Sector only, NO +theta, NO centerline)
# -------------------------------------------------------------------------
orig = np.array([160, H - 160])

# Vertical Z-axis
z_top = orig + np.array([0, -180])
ax.annotate('', xy=z_top, xytext=orig,
            arrowprops=dict(arrowstyle='->', color='#000000', lw=2.2, mutation_scale=18),
            zorder=6)
ax.text(z_top[0], z_top[1] - 15, r'$+z$', fontsize=20, fontweight='bold', color='#000000', ha='center', va='bottom')

# 3D Sector
r_len = 155
ray1 = orig + np.array([r_len * np.cos(np.radians(20)), r_len * np.sin(np.radians(20)) * 0.48])
ray2 = orig + np.array([r_len * np.cos(np.radians(-28)), r_len * np.sin(np.radians(-28)) * 0.48])

theta_angles = np.linspace(np.radians(-28), np.radians(20), 50)
arc_pts_x = orig[0] + r_len * np.cos(theta_angles)
arc_pts_y = orig[1] + r_len * np.sin(theta_angles) * 0.48

sector_poly_x = [orig[0]] + list(arc_pts_x) + [orig[0]]
sector_poly_y = [orig[1]] + list(arc_pts_y) + [orig[1]]
ax.fill(sector_poly_x, sector_poly_y, color='#EBF3FB', alpha=0.85, zorder=4)
ax.plot(sector_poly_x, sector_poly_y, color='#3B6077', linewidth=1.4, zorder=5)

# Ray 1 with arrow (+r)
ax.annotate('', xy=ray1, xytext=orig,
            arrowprops=dict(arrowstyle='->', color='#000000', lw=2.0, mutation_scale=16),
            zorder=6)
ax.text(ray1[0] + 16, ray1[1] + 6, r'$+r$', fontsize=20, fontweight='bold', color='#000000', ha='left', va='center')

# -------------------------------------------------------------------------
# D. Four Heat Fluxes Q: Strict Collinearity with Arrow Axes of Symmetry
# -------------------------------------------------------------------------
c_red = '#E01010'
fsize = 16

# 1. Top arrow (North -> Mother): Axis of symmetry is vertical line x = 765.0 + dR
x_top = 765.0 + dR
y_top = 515.0 + dR
ax.text(x_top, y_top, r'$Q_{i,\, j+1/2}$',
        fontsize=fsize, color=c_red, fontweight='bold', ha='center', va='center', zorder=8)

# 2. Bottom arrow (Mother -> South): Axis of symmetry is vertical line x = 764.5 + dR
x_bot = 764.5 + dR
y_bot = 1445.0 + dR
ax.text(x_bot, y_bot, r'$Q_{i,\, j-1/2}$',
        fontsize=fsize, color=c_red, fontweight='bold', ha='center', va='center', zorder=8)

# 3. Left arrow (Mother -> West): Axis of symmetry line:
# y = 0.2146 * (x - dR) + 820.72 + dR
x_left = 445.0 + dR
y_left = 0.2146 * (x_left - dR) + 820.72 + dR
ax.text(x_left, y_left, r'$Q_{i-1/2,\, j}$',
        fontsize=fsize, color=c_red, fontweight='bold', ha='center', va='center', zorder=8)

# 4. Right arrow (East -> Mother): Same radial axis of symmetry line:
x_right = 1205.0 + dR
y_right = 0.2146 * (x_right - dR) + 820.72 + dR
ax.text(x_right, y_right, r'$Q_{i+1/2,\, j}$',
        fontsize=fsize, color=c_red, fontweight='bold', ha='center', va='center', zorder=8)

out_png = os.path.join(SCRATCH, "fvm_flux_annotated_v4_perfect.png")
fig.savefig(out_png, dpi=300, bbox_inches='tight', pad_inches=0.02)
plt.close(fig)
print(f"Saved {out_png}")

# Sync to EDA figures and artifacts
eda_target = os.path.join(EDA_DIR, "fvm_flux_annotated_v2.png")
art_target = os.path.join(ART_DIR, "fvm_flux_annotated_v2.png")
shutil.copy(out_png, eda_target)
shutil.copy(out_png, art_target)
print("Synced to target files successfully!")
