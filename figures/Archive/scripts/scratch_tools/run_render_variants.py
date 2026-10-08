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

def render_variant(var_name, arrow_js_code):
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

    // 3D Arrow Builder
    function addArrow3D(pStart, pEnd, shaftR, headR, headLen, hexColor) {{
      const dir = new THREE.Vector3().subVectors(pEnd, pStart);
      const totalLen = dir.length();
      const actualHeadLen = Math.min(headLen, totalLen * 0.45);
      const shaftLen = totalLen - actualHeadLen;

      const mat = new THREE.MeshBasicMaterial({{ color: hexColor }});

      // Shaft
      const shaftGeo = new THREE.CylinderGeometry(shaftR, shaftR, shaftLen, 24);
      shaftGeo.translate(0, shaftLen / 2, 0);
      shaftGeo.rotateX(Math.PI / 2);
      const shaftMesh = new THREE.Mesh(shaftGeo, mat);
      shaftMesh.position.copy(pStart);
      shaftMesh.lookAt(pEnd);
      scene.add(shaftMesh);

      // Head cone
      const headGeo = new THREE.ConeGeometry(headR, actualHeadLen, 24);
      headGeo.translate(0, actualHeadLen / 2, 0);
      headGeo.rotateX(Math.PI / 2);
      const headMesh = new THREE.Mesh(headGeo, mat);
      const headPos = new THREE.Vector3().copy(pStart).addScaledVector(dir.clone().normalize(), shaftLen);
      headMesh.position.copy(headPos);
      headMesh.lookAt(pEnd);
      scene.add(headMesh);
    }}

    {arrow_js_code}

    renderer.render(scene, camera);
  </script>
</body>
</html>
"""

    hpath = os.path.join(SCRATCH, f"test_{var_name}.html")
    rpath = os.path.join(SCRATCH, f"test_{var_name}_raw.png")
    fpath = os.path.join(SCRATCH, f"test_{var_name}_final.png")

    with open(hpath, "w", encoding="utf-8") as f:
        f.write(html_content)

    norm_url = f"file:///{hpath.replace(os.sep, '/')}"
    subprocess.run([edge_exe, "--headless", f"--screenshot={rpath}", f"--window-size={W},{H}", norm_url], capture_output=True)

    # Crop and flip
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
    final_img.save(fpath)
    print(f"Rendered {var_name} successfully -> {fpath}")
    return fpath

# Let's test Variant 1: Mid-arc 3D arrows (located at theta = 30 deg), uniform crimson color, thicker in / thinner out
# In 3D: theta = 30 deg (Math.PI / 6)
# Large -> Mother: from r=5.20 to r=4.50, y=0.0
# Mother -> Small: from r=3.75 to r=3.05, y=0.0
# Far -> Mother: r=4.125, from y=1.05 to y=0.35
# Mother -> Near: r=4.125, from y=-0.35 to y=-1.05

var1_js = """
    const th_arrow = (30.0 * Math.PI) / 180.0;
    const cos_th = Math.cos(th_arrow);
    const sin_th = Math.sin(th_arrow);

    const r_mid = (r_mother_in + r_mother_out) / 2.0;

    // Color: Deep Crimson
    const col = 0xB22222;

    // Large -> Mother (Inflow, Thick)
    addArrow3D(
      new THREE.Vector3(5.25 * cos_th, 0.0, -5.25 * sin_th),
      new THREE.Vector3(4.45 * cos_th, 0.0, -4.45 * sin_th),
      0.038, 0.085, 0.22, col
    );

    // Far -> Mother (Inflow, Thick)
    addArrow3D(
      new THREE.Vector3(r_mid * cos_th, 1.10, -r_mid * sin_th),
      new THREE.Vector3(r_mid * cos_th, 0.30, -r_mid * sin_th),
      0.038, 0.085, 0.22, col
    );

    // Mother -> Small (Outflow, Slender)
    addArrow3D(
      new THREE.Vector3(3.80 * cos_th, 0.0, -3.80 * sin_th),
      new THREE.Vector3(3.00 * cos_th, 0.0, -3.00 * sin_th),
      0.022, 0.055, 0.16, col
    );

    // Mother -> Near (Outflow, Slender)
    addArrow3D(
      new THREE.Vector3(r_mid * cos_th, -0.30, -r_mid * sin_th),
      new THREE.Vector3(r_mid * cos_th, -1.10, -r_mid * sin_th),
      0.022, 0.055, 0.16, col
    );
"""

# Variant 2: Dual gradient: Thicker & Deep Crimson for Inflow, Slender & Soft Coral/Light Terracotta for Outflow
var2_js = """
    const th_arrow = (30.0 * Math.PI) / 180.0;
    const cos_th = Math.cos(th_arrow);
    const sin_th = Math.sin(th_arrow);
    const r_mid = (r_mother_in + r_mother_out) / 2.0;

    const col_in = 0x990000;   // Deep ruby red (High flux)
    const col_out = 0xD9534F;  // Lighter warm vermillion (Diminished flux)

    // Large -> Mother (Inflow, High Flux)
    addArrow3D(
      new THREE.Vector3(5.25 * cos_th, 0.0, -5.25 * sin_th),
      new THREE.Vector3(4.45 * cos_th, 0.0, -4.45 * sin_th),
      0.040, 0.090, 0.24, col_in
    );

    // Far -> Mother (Inflow, High Flux)
    addArrow3D(
      new THREE.Vector3(r_mid * cos_th, 1.10, -r_mid * sin_th),
      new THREE.Vector3(r_mid * cos_th, 0.30, -r_mid * sin_th),
      0.040, 0.090, 0.24, col_in
    );

    // Mother -> Small (Outflow, Low Flux)
    addArrow3D(
      new THREE.Vector3(3.80 * cos_th, 0.0, -3.80 * sin_th),
      new THREE.Vector3(3.00 * cos_th, 0.0, -3.00 * sin_th),
      0.020, 0.050, 0.15, col_out
    );

    // Mother -> Near (Outflow, Low Flux)
    addArrow3D(
      new THREE.Vector3(r_mid * cos_th, -0.30, -r_mid * sin_th),
      new THREE.Vector3(r_mid * cos_th, -1.10, -r_mid * sin_th),
      0.020, 0.050, 0.15, col_out
    );
"""

# Variant 3: On the front cut plane (theta = 60 deg, slightly lifted along normal to cut plane)
# At cut plane theta = 60 deg:
# Normal to cut plane is (-sin(60), 0, -cos(60)) or similar.
# A tiny offset of 0.01 in the direction of the camera ensures clean visibility without z-fighting.
var3_js = """
    const th_cut = (60.0 * Math.PI) / 180.0;
    const cos_c = Math.cos(th_cut);
    const sin_c = Math.sin(th_cut);
    const r_mid = (r_mother_in + r_mother_out) / 2.0;

    // Normal vector to theta = 60 cut face is (-sin(60), 0, -cos(60))
    // We lift slightly along the face normal or towards viewer:
    const n_x = -Math.sin(th_cut) * 0.02;
    const n_z = -Math.cos(th_cut) * 0.02;

    const col_in = 0x990000;
    const col_out = 0xD9534F;

    // Large -> Mother
    addArrow3D(
      new THREE.Vector3(5.25 * cos_c + n_x, 0.0, -5.25 * sin_c + n_z),
      new THREE.Vector3(4.45 * cos_c + n_x, 0.0, -4.45 * sin_c + n_z),
      0.036, 0.080, 0.22, col_in
    );

    // Far -> Mother
    addArrow3D(
      new THREE.Vector3(r_mid * cos_c + n_x, 1.10, -r_mid * sin_c + n_z),
      new THREE.Vector3(r_mid * cos_c + n_x, 0.30, -r_mid * sin_c + n_z),
      0.036, 0.080, 0.22, col_in
    );

    // Mother -> Small
    addArrow3D(
      new THREE.Vector3(3.80 * cos_c + n_x, 0.0, -3.80 * sin_c + n_z),
      new THREE.Vector3(3.00 * cos_c + n_x, 0.0, -3.00 * sin_c + n_z),
      0.020, 0.050, 0.15, col_out
    );

    // Mother -> Near
    addArrow3D(
      new THREE.Vector3(r_mid * cos_c + n_x, -0.30, -r_mid * sin_c + n_z),
      new THREE.Vector3(r_mid * cos_c + n_x, -1.10, -r_mid * sin_c + n_z),
      0.020, 0.050, 0.15, col_out
    );
"""

render_variant("var1_3d_crimson", var1_js)
render_variant("var2_3d_gradient", var2_js)
render_variant("var3_cutplane_gradient", var3_js)

print("All variants rendered successfully.")
