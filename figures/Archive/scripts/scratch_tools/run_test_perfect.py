import subprocess, os, shutil
from PIL import Image
import numpy as np

html_perfect = """<!DOCTYPE html>
<html>
<head>
<script src="three.min.js"></script>
<style>* { margin: 0; padding: 0; } body { background: #fff; overflow: hidden; width: 1800px; height: 1800px; }</style>
</head>
<body>
<div id="c" style="width:1800px;height:1800px;"></div>
<script>
const width = 1800;
const height = 1800;
const scene = new THREE.Scene();
scene.background = new THREE.Color(0xFFFFFF);

const camera = new THREE.PerspectiveCamera(42, 1, 0.1, 100);
camera.position.set(-0.01, 1.86, -8.91);
camera.lookAt(3.30, 0, 0);

const renderer = new THREE.WebGLRenderer({ antialias: true, preserveDrawingBuffer: true });
renderer.setSize(width, height);
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

// Solid white occluding material with polygonOffset
const whiteMat = new THREE.MeshBasicMaterial({
  color: 0xFFFFFF,
  polygonOffset: true,
  polygonOffsetFactor: 1.0,
  polygonOffsetUnits: 1.0
});

const blackTubeMat = new THREE.MeshBasicMaterial({ color: 0x000000 });
const thinEdgeMat = new THREE.LineBasicMaterial({ color: 0x000000, linewidth: 2 });

function createCylinderBetweenPoints(p1, p2, radius) {
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
}

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

  if (r.isMother) {
    // Build bold tubes for Mother Ring directly from EdgesGeometry!
    const posAttr = edgeGeo.attributes.position;
    const tubeR = 0.022; // bold
    for (let i = 0; i < posAttr.count; i += 2) {
      const p1 = new THREE.Vector3(posAttr.getX(i), posAttr.getY(i) + r.y, posAttr.getZ(i));
      const p2 = new THREE.Vector3(posAttr.getX(i+1), posAttr.getY(i+1) + r.y, posAttr.getZ(i+1));
      const cyl = createCylinderBetweenPoints(p1, p2, tubeR);
      if (cyl) scene.add(cyl);
    }
  } else {
    // Slender solid lines for other 4 rings
    const edges = new THREE.LineSegments(edgeGeo, thinEdgeMat);
    edges.position.y = r.y;
    scene.add(edges);
  }
});

renderer.render(scene, camera);
</script>
</body>
</html>"""

html_path = r'C:\Users\kqdx\.gemini\antigravity\brain\984f8f9b-1caf-4e5e-a827-7c48f241b73b\scratch\test_perfect.html'
with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html_perfect)

edge_exe = r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
raw_png = r'C:\Users\kqdx\.gemini\antigravity\brain\984f8f9b-1caf-4e5e-a827-7c48f241b73b\scratch\raw_perfect.png'
cmd = [edge_exe, '--headless', f'--screenshot={raw_png}', '--window-size=1800,1800', f'file:///{html_path.replace(os.sep, "/")}']
subprocess.run(cmd, check=True)
print('Raw render generated.')
