import subprocess, os, shutil
from PIL import Image

html_all_edges = """<!DOCTYPE html>
<html>
<head>
<script src="three.min.js"></script>
<style>* { margin: 0; padding: 0; } body { background: #fff; overflow: hidden; width: 1400px; height: 1400px; }</style>
</head>
<body>
<div id="c" style="width:1400px;height:1400px;"></div>
<script>
const scene = new THREE.Scene();
scene.background = new THREE.Color(0xFFFFFF);
const camera = new THREE.PerspectiveCamera(42, 1, 0.1, 100);
camera.position.set(-0.01, 1.86, -8.91);
camera.lookAt(3.30, 0, 0);

const renderer = new THREE.WebGLRenderer({ antialias: true, preserveDrawingBuffer: true });
renderer.setSize(1400, 1400);
renderer.setClearColor(0xFFFFFF, 1.0);
document.getElementById('c').appendChild(renderer.domElement);

function createRing(rIn, rOut, h, sweepDeg) {
  const sweepRad = (sweepDeg * Math.PI) / 180.0;
  const shape = new THREE.Shape();
  shape.absarc(0, 0, rOut, -sweepRad/2, sweepRad/2, false);
  shape.lineTo(rIn * Math.cos(sweepRad/2), rIn * Math.sin(sweepRad/2));
  shape.absarc(0, 0, rIn, sweepRad/2, -sweepRad/2, true);
  shape.lineTo(rOut * Math.cos(-sweepRad/2), rOut * Math.sin(-sweepRad/2));
  const geo = new THREE.ExtrudeGeometry(shape, { depth: h, bevelEnabled: false, curveSegments: 64 });
  geo.rotateX(-Math.PI / 2);
  geo.translate(0, -h / 2, 0);
  return geo;
}

// Solid white material for occlusion
const whiteMat = new THREE.MeshBasicMaterial({
  color: 0xFFFFFF,
  polygonOffset: true,
  polygonOffsetFactor: 1.0,
  polygonOffsetUnits: 1.0
});

const edgeMat = new THREE.LineBasicMaterial({ color: 0x000000, linewidth: 2 });

const rings = [
  { name: 'mother', rIn: 3.55, rOut: 4.70, y: 0.0, isMother: true },
  { name: 'small',  rIn: 2.10, rOut: 3.25, y: 0.0, isMother: false },
  { name: 'large',  rIn: 5.00, rOut: 6.15, y: 0.0, isMother: false },
  { name: 'far',    rIn: 3.55, rOut: 4.70, y: 1.40, isMother: false },
  { name: 'near',   rIn: 3.55, rOut: 4.70, y: -1.40, isMother: false }
];

rings.forEach(r => {
  const geo = createRing(r.rIn, r.rOut, 1.10, 120);
  const mesh = new THREE.Mesh(geo, whiteMat);
  mesh.position.y = r.y;
  scene.add(mesh);

  const edgeGeo = new THREE.EdgesGeometry(geo, 15);
  const edges = new THREE.LineSegments(edgeGeo, edgeMat);
  edges.position.y = r.y;
  scene.add(edges);
});

renderer.render(scene, camera);
</script>
</body>
</html>"""

html_path = r'C:\Users\kqdx\.gemini\antigravity\brain\984f8f9b-1caf-4e5e-a827-7c48f241b73b\scratch\test_all_edges.html'
with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html_all_edges)

edge_exe = r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
raw_png = r'C:\Users\kqdx\.gemini\antigravity\brain\984f8f9b-1caf-4e5e-a827-7c48f241b73b\scratch\all_edges.png'
cmd = [edge_exe, '--headless', f'--screenshot={raw_png}', '--window-size=1400,1400', f'file:///{html_path.replace(os.sep, "/")}']
subprocess.run(cmd, check=True)
print('All edges rendered.')
