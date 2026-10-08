import subprocess, os, shutil
from PIL import Image
import numpy as np

# Camera setup
C = np.array([-0.01, 1.86, -8.91])
T = np.array([3.30, 0.00, 0.00])
up = np.array([0.0, 1.0, 0.0])

w = (T - C) / np.linalg.norm(T - C)
u = np.cross(up, w)
u = u / np.linalg.norm(u)
v = np.cross(w, u)

fov = 42.0
f = 1.0 / np.tan(np.radians(fov / 2.0))

W, H = 2400, 2400

def to_screen(P):
    p_rel = P - C
    xc = np.dot(p_rel, u)
    yc = np.dot(p_rel, v)
    zc = np.dot(p_rel, w)
    ndc_x = f * xc / zc
    ndc_y = f * yc / zc
    sx = (ndc_x + 1.0) * 0.5 * W
    sy = (1.0 - ndc_y) * 0.5 * H
    return sx, sy

# Mother ring 3D bounds
rin = 3.55
rout = 4.70
h = 1.10
t_half = np.radians(60.0)

mother_pts = []
for t in np.linspace(-t_half, t_half, 50):
    for r in [rin, rout]:
        for y in [-h/2, h/2]:
            P = np.array([r * np.cos(t), y, -r * np.sin(t)])
            mother_pts.append(to_screen(P))

mother_pts = np.array(mother_pts)
m_xmin, m_ymin = np.min(mother_pts, axis=0)
m_xmax, m_ymax = np.max(mother_pts, axis=0)
cx_mother = (m_xmin + m_xmax) / 2.0
cy_mother = (m_ymin + m_ymax) / 2.0

print(f'2400x2400: Mother Ring Center = ({cx_mother:.2f}, {cy_mother:.2f})')

html_perfect = f"""<!DOCTYPE html>
<html>
<head>
<script src="three.min.js"></script>
<style>* {{ margin: 0; padding: 0; }} body {{ background: #fff; overflow: hidden; width: {W}px; height: {H}px; }}</style>
</head>
<body>
<div id="c" style="width:{W}px;height:{H}px;"></div>
<script>
const width = {W};
const height = {H};
const scene = new THREE.Scene();
scene.background = new THREE.Color(0xFFFFFF);

const camera = new THREE.PerspectiveCamera(42, 1, 0.1, 100);
camera.position.set(-0.01, 1.86, -8.91);
camera.lookAt(3.30, 0, 0);

const renderer = new THREE.WebGLRenderer({{ antialias: true, preserveDrawingBuffer: true }});
renderer.setSize(width, height);
renderer.setClearColor(0xFFFFFF, 1.0);
document.getElementById('c').appendChild(renderer.domElement);

function createRing(rIn, rOut, h, sweepDeg) {{
  const sweepRad = (sweepDeg * Math.PI) / 180.0;
  const shape = new THREE.Shape();
  shape.absarc(0, 0, rOut, -sweepRad/2, sweepRad/2, false);
  shape.lineTo(rIn * Math.cos(sweepRad/2), rIn * Math.sin(sweepRad/2));
  shape.absarc(0, 0, rIn, sweepRad/2, -sweepRad/2, true);
  shape.lineTo(rOut * Math.cos(-sweepRad/2), rOut * Math.sin(-sweepRad/2));
  const geo = new THREE.ExtrudeGeometry(shape, {{ depth: h, bevelEnabled: false, curveSegments: 64 }});
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

const blackTubeMat = new THREE.MeshBasicMaterial({{ color: 0x000000 }});
const thinEdgeMat = new THREE.LineBasicMaterial({{ color: 0x000000, linewidth: 2 }});

function createCylinderBetweenPoints(p1, p2, radius) {{
  const dir = new THREE.Vector3().subVectors(p2, p1);
  const len = dir.length();
  if (len < 1e-4) return null;
  const geom = new THREE.CylinderGeometry(radius, radius, len, 6, 1, false);
  geom.translate(0, len / 2, 0);
  geom.rotateX(Math.PI / 2);
  
  const mesh = new THREE.Mesh(geom, blackTubeMat);
  mesh.position.copy(p1);
  mesh.lookAt(p2);
  return mesh;
}}

const rings = [
  {{ name: 'mother', rIn: 3.55, rOut: 4.70, y: 0.0, isMother: true }},
  {{ name: 'small',  rIn: 2.10, rOut: 3.25, y: 0.0, isMother: false }},
  {{ name: 'large',  rIn: 5.00, rOut: 6.15, y: 0.0, isMother: false }},
  {{ name: 'far',    rIn: 3.55, rOut: 4.70, y: 1.40, isMother: false }},
  {{ name: 'near',   rIn: 3.55, rOut: 4.70, y: -1.40, isMother: false }}
];

rings.forEach(r => {{
  const geo = createRing(r.rIn, r.rOut, 1.10, 120);
  const mesh = new THREE.Mesh(geo, whiteMat);
  mesh.position.y = r.y;
  scene.add(mesh);

  const edgeGeo = new THREE.EdgesGeometry(geo, 15);

  if (r.isMother) {{
    // Bold tubes for Mother Ring
    const posAttr = edgeGeo.attributes.position;
    const tubeR = 0.024;
    for (let i = 0; i < posAttr.count; i += 2) {{
      const p1 = new THREE.Vector3(posAttr.getX(i), posAttr.getY(i) + r.y, posAttr.getZ(i));
      const p2 = new THREE.Vector3(posAttr.getX(i+1), posAttr.getY(i+1) + r.y, posAttr.getZ(i+1));
      const cyl = createCylinderBetweenPoints(p1, p2, tubeR);
      if (cyl) scene.add(cyl);
    }}
  }} else {{
    // Slender solid edges for other 4 rings
    const edges = new THREE.LineSegments(edgeGeo, thinEdgeMat);
    edges.position.y = r.y;
    scene.add(edges);
  }}
}});

renderer.render(scene, camera);
</script>
</body>
</html>"""

html_path = r'C:\Users\kqdx\.gemini\antigravity\brain\984f8f9b-1caf-4e5e-a827-7c48f241b73b\scratch\test_perfect_2400.html'
with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html_perfect)

edge_exe = r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
raw_png = r'C:\Users\kqdx\.gemini\antigravity\brain\984f8f9b-1caf-4e5e-a827-7c48f241b73b\scratch\raw_2400.png'
cmd = [edge_exe, '--headless', f'--screenshot={raw_png}', f'--window-size={W},{H}', f'file:///{html_path.replace(os.sep, "/")}']
subprocess.run(cmd, check=True)

# Now crop perfectly centered on Mother Ring Center
img = Image.open(raw_png).convert('RGBA')
arr = np.array(img.convert('L'))
non_white = arr < 250
y_idx, x_idx = np.where(non_white)

x_min_all, x_max_all = int(np.min(x_idx)), int(np.max(x_idx))
y_min_all, y_max_all = int(np.min(y_idx)), int(np.max(y_idx))

# Radius from Mother center to cover all content
dx1 = abs(x_min_all - cx_mother)
dx2 = abs(x_max_all - cx_mother)
dy1 = abs(y_min_all - cy_mother)
dy2 = abs(y_max_all - cy_mother)

padding = 100
R = int(np.ceil(max(dx1, dx2, dy1, dy2))) + padding

crop_box = (
    int(round(cx_mother - R)),
    int(round(cy_mother - R)),
    int(round(cx_mother + R)),
    int(round(cy_mother + R))
)

print(f'Crop box: {crop_box}, size = {crop_box[2] - crop_box[0]}x{crop_box[3] - crop_box[1]}')

# Create a clean white canvas of size (2R, 2R) and paste the cropped area to guarantee zero out-of-bounds clipping
canvas_size = 2 * R
square_img = Image.new('RGBA', (canvas_size, canvas_size), (255, 255, 255, 255))

# Compute overlap with source image
src_x1 = max(0, crop_box[0])
src_y1 = max(0, crop_box[1])
src_x2 = min(W, crop_box[2])
src_y2 = min(H, crop_box[3])

cropped_part = img.crop((src_x1, src_y1, src_x2, src_y2))
paste_x = src_x1 - crop_box[0]
paste_y = src_y1 - crop_box[1]
square_img.paste(cropped_part, (paste_x, paste_y))

# Apply horizontal flip (left to right)
final_img = square_img.transpose(Image.FLIP_LEFT_RIGHT)

out_png = r'C:\Users\kqdx\.gemini\antigravity\brain\984f8f9b-1caf-4e5e-a827-7c48f241b73b\scratch\perfect_centered.png'
final_img.save(out_png, dpi=(300, 300))
print(f'Successfully created perfectly centered image: {out_png}')
