import os
import subprocess
import numpy as np
from PIL import Image

SCRATCH = r"C:\Users\kqdx\.gemini\antigravity\brain\984f8f9b-1caf-4e5e-a827-7c48f241b73b\scratch"
EDA_DIR = r"D:\HIT\数模2026\eda_figures"
three_js_path = os.path.join(EDA_DIR, "three.min.js").replace('\\', '/')
edge_exe = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

W, H = 2600, 2600
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

def render_flared_final(output_png_path, s_top=0.13, s_right=0.13, s_bot=0.14):
    html_content = f"""<!DOCTYPE html>
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
    const width = {W};
    const height = {H};

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

    const whiteMaterial = new THREE.MeshBasicMaterial({{
      color: 0xFFFFFF,
      polygonOffset: true,
      polygonOffsetFactor: 1.0,
      polygonOffsetUnits: 1.0
    }});

    const blackTubeMaterial = new THREE.MeshBasicMaterial({{ color: 0x000000 }});
    const thinEdgeMaterial = new THREE.LineBasicMaterial({{ color: 0x000000, linewidth: 2 }});

    function createCylinderBetweenPoints(p1, p2, radius, mat = blackTubeMaterial) {{
      const dir = new THREE.Vector3().subVectors(p2, p1);
      const len = dir.length();
      if (len < 1e-4) return null;
      const geom = new THREE.CylinderGeometry(radius, radius, len, 16, 1, false);
      geom.translate(0, len / 2, 0);
      geom.rotateX(Math.PI / 2);
      const mesh = new THREE.Mesh(geom, mat);
      mesh.position.copy(p1);
      mesh.lookAt(p2);
      return mesh;
    }}

    function createLineBetweenPoints(p1, p2) {{
      const geom = new THREE.BufferGeometry().setFromPoints([p1, p2]);
      return new THREE.Line(geom, thinEdgeMaterial);
    }}

    const ringSpecs = [
      {{ name: 'mother', rIn: r_mother_in, rOut: r_mother_out, y: 0.0, isMother: true }},
      {{ name: 'small',  rIn: r_small_in,  rOut: r_small_out,  y: 0.0, isMother: false }},
      {{ name: 'large',  rIn: r_large_in,  rOut: r_large_out,  y: 0.0, isMother: false }},
      {{ name: 'far',    rIn: r_mother_in, rOut: r_mother_out, y: y_far, isMother: false }},
      {{ name: 'near',   rIn: r_mother_in, rOut: r_mother_out, y: y_near, isMother: false }}
    ];

    ringSpecs.forEach(spec => {{
      const geo = createRingSectorGeometry(spec.rIn, spec.rOut, delta_z);
      const mesh = new THREE.Mesh(geo, whiteMaterial);
      mesh.position.y = spec.y;
      scene.add(mesh);

      const edgeGeo = new THREE.EdgesGeometry(geo, 15);

      if (spec.isMother) {{
        const posAttr = edgeGeo.attributes.position;
        const tubeR = 0.024;
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

    // 1. Large -> Mother (Shifted towards Mother by s_right)
    addFlaredArrow(
      new THREE.Vector3((5.35 - s_right) * cos_c, 0.0, -(5.35 - s_right) * sin_c),
      new THREE.Vector3((4.40 - s_right) * cos_c, 0.0, -(4.40 - s_right) * sin_c),
      0.40, 0.085, 0.22, 0.30, 3.0, 0.02
    );

    // 2. Far -> Mother (Shifted downwards into Mother by s_top)
    addFlaredArrow(
      new THREE.Vector3(r_mid * cos_c, 1.20 - s_top, -r_mid * sin_c),
      new THREE.Vector3(r_mid * cos_c, 0.25 - s_top, -r_mid * sin_c),
      0.40, 0.085, 0.22, 0.30, 3.0, 0.02
    );

    // 3. Mother -> Small
    addFlaredArrow(
      new THREE.Vector3(3.70 * cos_c, 0.0, -3.70 * sin_c),
      new THREE.Vector3(3.05 * cos_c, 0.0, -3.05 * sin_c),
      0.22, 0.050, 0.14, 0.30, 3.0, 0.02
    );

    // 4. Mother -> Near (Shifted downwards into Near by s_bot)
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
    subprocess.run([edge_exe, "--headless", f"--screenshot={rpath}", f"--window-size={W},{H}", norm_url], capture_output=True)

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
        sx = (f_proj * xc / zc + 1.0) * 0.5 * W
        sy = (1.0 - f_proj * yc / zc) * 0.5 * H
        return sx, sy

    rin_m = 3.55
    rout_m = 4.70
    h_m = 1.10
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

    padding = 160
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
    src_x2 = min(W, crop_box[2])
    src_y2 = min(H, crop_box[3])

    cropped_part = img.crop((src_x1, src_y1, src_x2, src_y2))
    paste_x = src_x1 - crop_box[0]
    paste_y = src_y1 - crop_box[1]
    square_img.paste(cropped_part, (paste_x, paste_y))

    final_img = square_img.transpose(Image.FLIP_LEFT_RIGHT)
    final_img.save(output_png_path)
    print(f"Generated refined image -> {output_png_path}")
    return output_png_path

eda_out = os.path.join(EDA_DIR, "fvm_flux_flared_c2_refined.png")
art_out = r"C:\Users\kqdx\.gemini\antigravity\brain\984f8f9b-1caf-4e5e-a827-7c48f241b73b\fvm_flux_flared_c2_refined.png"

render_flared_final(eda_out, s_top=0.13, s_right=0.13, s_bot=0.14)
# Copy to artifact
import shutil
shutil.copy(eda_out, art_out)
print("Done!")
