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

# Exact silhouette tangent angles on cylinder sectors
alpha_large = np.arccos(6.15 / D)
theta_large = phi - alpha_large

alpha_mother = np.arccos(4.70 / D)
theta_mother = phi - alpha_mother

alpha_small = np.arccos(3.25 / D)
theta_small = phi - alpha_small

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

    // Angle halved: from 0 deg to 60 deg (near face at 60 deg kept fixed, tail shortened)
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

    function createCylinderBetweenPoints(p1, p2, radius) {{
      const dir = new THREE.Vector3().subVectors(p2, p1);
      const len = dir.length();
      if (len < 1e-4) return null;
      const geom = new THREE.CylinderGeometry(radius, radius, len, 6, 1, false);
      geom.translate(0, len / 2, 0);
      geom.rotateX(Math.PI / 2);
      const mesh = new THREE.Mesh(geom, blackTubeMaterial);
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
        // Mother ring: bold solid black lines
        const posAttr = edgeGeo.attributes.position;
        const tubeR = 0.024;
        for (let i = 0; i < posAttr.count; i += 2) {{
          const p1 = new THREE.Vector3(posAttr.getX(i), posAttr.getY(i) + spec.y, posAttr.getZ(i));
          const p2 = new THREE.Vector3(posAttr.getX(i+1), posAttr.getY(i+1) + spec.y, posAttr.getZ(i+1));
          const cyl = createCylinderBetweenPoints(p1, p2, tubeR);
          if (cyl) scene.add(cyl);
        }}
      }} else {{
        // Other 4 rings: slender solid black lines with perfect perspective occlusion
        const lineSegments = new THREE.LineSegments(edgeGeo, thinEdgeMaterial);
        lineSegments.position.y = spec.y;
        scene.add(lineSegments);
      }}
    }});

    // Add silhouette generator lines (vertical boundary lines) for outer cylinders:
    // 1. Large ring outer cylinder (r = 6.15)
    const th_large = {theta_large};
    const p1_large = new THREE.Vector3(r_large_out * Math.cos(th_large), -delta_z / 2, -r_large_out * Math.sin(th_large));
    const p2_large = new THREE.Vector3(r_large_out * Math.cos(th_large),  delta_z / 2, -r_large_out * Math.sin(th_large));
    scene.add(createLineBetweenPoints(p1_large, p2_large));

    // 2. Far ring outer cylinder (r = 4.70, y_far)
    const th_mother = {theta_mother};
    const p1_far = new THREE.Vector3(r_mother_out * Math.cos(th_mother), y_far - delta_z / 2, -r_mother_out * Math.sin(th_mother));
    const p2_far = new THREE.Vector3(r_mother_out * Math.cos(th_mother), y_far + delta_z / 2, -r_mother_out * Math.sin(th_mother));
    scene.add(createLineBetweenPoints(p1_far, p2_far));

    // 3. Mother ring outer cylinder (r = 4.70, y = 0) - bold tube because it is mother ring!
    const p1_mother = new THREE.Vector3(r_mother_out * Math.cos(th_mother), -delta_z / 2, -r_mother_out * Math.sin(th_mother));
    const p2_mother = new THREE.Vector3(r_mother_out * Math.cos(th_mother),  delta_z / 2, -r_mother_out * Math.sin(th_mother));
    const cyl_mother = createCylinderBetweenPoints(p1_mother, p2_mother, 0.024);
    if (cyl_mother) scene.add(cyl_mother);

    // 4. Near ring outer cylinder (r = 4.70, y_near)
    const p1_near = new THREE.Vector3(r_mother_out * Math.cos(th_mother), y_near - delta_z / 2, -r_mother_out * Math.sin(th_mother));
    const p2_near = new THREE.Vector3(r_mother_out * Math.cos(th_mother), y_near + delta_z / 2, -r_mother_out * Math.sin(th_mother));
    scene.add(createLineBetweenPoints(p1_near, p2_near));

    // 5. Small ring outer cylinder (r = 3.25, y = 0)
    const th_small = {theta_small};
    const p1_small = new THREE.Vector3(r_small_out * Math.cos(th_small), -delta_z / 2, -r_small_out * Math.sin(th_small));
    const p2_small = new THREE.Vector3(r_small_out * Math.cos(th_small),  delta_z / 2, -r_small_out * Math.sin(th_small));
    scene.add(createLineBetweenPoints(p1_small, p2_small));

    renderer.render(scene, camera);
  </script>
</body>
</html>
"""

hpath = os.path.join(SCRATCH, "test_halved_lineart.html")
rpath = os.path.join(SCRATCH, "test_halved_lineart_raw.png")
fpath = os.path.join(SCRATCH, "test_halved_lineart_final.png")

with open(hpath, "w", encoding="utf-8") as f:
    f.write(html_content)

norm_url = f"file:///{hpath.replace(os.sep, '/')}"
subprocess.run([edge_exe, "--headless", f"--screenshot={rpath}", f"--window-size={W},{H}", norm_url])

# Centering projection
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
# Mother ring 3D vertices from 0 to 60 deg
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

x_min_all, x_max_all = int(np.min(x_idx)), int(np.max(x_idx))
y_min_all, y_max_all = int(np.min(y_idx)), int(np.max(y_idx))

padding = 160
dx1 = abs(x_min_all - cx_mother)
dx2 = abs(x_max_all - cx_mother)
dy1 = abs(y_min_all - cy_mother)
dy2 = abs(y_max_all - cy_mother)

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
print(f"Rendered halved lineart with silhouettes! Final size: {final_img.size}")
