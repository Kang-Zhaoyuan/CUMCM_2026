import subprocess
import os

SCRATCH = r"C:\Users\kqdx\.gemini\antigravity\brain\984f8f9b-1caf-4e5e-a827-7c48f241b73b\scratch"
three_js = "D:/HIT/数模2026/eda_figures/three.min.js"

html = f"""<!DOCTYPE html>
<html>
<head><script src="{three_js}"></script></head>
<body>
<script>
  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(42, 1, 0.1, 100);
  const target = new THREE.Vector3(3.30, 0, 0);
  const cam_orig = new THREE.Vector3(-0.01, 1.86, -8.91);
  const C = target.clone().add(cam_orig.clone().sub(target).multiplyScalar(1.35));
  camera.position.copy(C);
  camera.lookAt(target);
  camera.updateMatrixWorld();

  const delta_z = 1.10;
  function geo(rIn, rOut, h) {{
    const s = (-60 * Math.PI) / 180, e = (60 * Math.PI) / 180;
    const sh = new THREE.Shape();
    sh.absarc(0, 0, rOut, s, e, false);
    sh.lineTo(rIn * Math.cos(e), rIn * Math.sin(e));
    sh.absarc(0, 0, rIn, e, s, true);
    sh.lineTo(rOut * Math.cos(s), rOut * Math.sin(s));
    const g = new THREE.ExtrudeGeometry(sh, {{ depth: h, bevelEnabled: false, curveSegments: 48 }});
    g.rotateX(-Math.PI / 2);
    g.translate(0, -h/2, 0);
    return g;
  }}

  const meshes = {{}};
  [
    {{ n: 'mother', r1: 3.55, r2: 4.70, y: 0 }},
    {{ n: 'small',  r1: 2.10, r2: 3.25, y: 0 }},
    {{ n: 'large',  r1: 5.00, r2: 6.15, y: 0 }},
    {{ n: 'far',    r1: 3.55, r2: 4.70, y: 1.40 }},
    {{ n: 'near',   r1: 3.55, r2: 4.70, y: -1.40 }}
  ].forEach(spec => {{
    const g = geo(spec.r1, spec.r2, delta_z);
    const m = new THREE.Mesh(g, new THREE.MeshBasicMaterial());
    m.position.y = spec.y;
    m.name = spec.n;
    scene.add(m);
    meshes[spec.n] = m;
  }});

  const raycaster = new THREE.Raycaster();
  const ndcX = (907 / 2600) * 2 - 1;
  const ndcY = 1 - (1018 / 2600) * 2;
  raycaster.setFromCamera(new THREE.Vector2(ndcX, ndcY), camera);
  const intersects = raycaster.intersectObjects(scene.children);
  console.log('RAYCAST_RESULT:' + JSON.stringify(intersects.map(i => i.object.name + ' dist=' + i.distance.toFixed(2))));
</script>
</body>
</html>"""

hpath = os.path.join(SCRATCH, "test_ray.html")
with open(hpath, "w", encoding="utf-8") as f:
    f.write(html)

norm_url = f"file:///{hpath.replace(os.sep, '/')}"
res = subprocess.run([
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    "--headless",
    "--enable-logging=stderr",
    "--v=1",
    norm_url
], capture_output=True, text=True)

for line in res.stderr.splitlines():
    if "RAYCAST_RESULT" in line:
        print(line)
