import os
import subprocess
from PIL import Image

SCRATCH_DIR = r"C:\Users\kqdx\.gemini\antigravity\brain\984f8f9b-1caf-4e5e-a827-7c48f241b73b\scratch"
html_path = os.path.join(SCRATCH_DIR, "test_color.html")
raw_png = os.path.join(SCRATCH_DIR, "test_color_raw.png")
flip_png = os.path.join(SCRATCH_DIR, "test_color_flip.png")

html = """<!DOCTYPE html>
<html>
<head>
  <script src="D:/HIT/数模2026/eda_figures/three.min.js"></script>
  <style> * { margin: 0; padding: 0; } body { background: #fff; overflow: hidden; } </style>
</head>
<body>
  <script>
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0xFFFFFF);
    const camera = new THREE.PerspectiveCamera(42, 1, 0.1, 100);
    camera.position.set(-0.01, 1.86, -8.91);
    camera.lookAt(new THREE.Vector3(3.30, 0, 0));
    const renderer = new THREE.WebGLRenderer({ antialias: true, preserveDrawingBuffer: true });
    renderer.setSize(1000, 1000);
    document.body.appendChild(renderer.domElement);

    function geo(rIn, rOut, h) {
      const s = (-60 * Math.PI) / 180, e = (60 * Math.PI) / 180;
      const sh = new THREE.Shape();
      sh.absarc(0, 0, rOut, s, e, false);
      sh.lineTo(rIn * Math.cos(e), rIn * Math.sin(e));
      sh.absarc(0, 0, rIn, e, s, true);
      sh.lineTo(rOut * Math.cos(s), rOut * Math.sin(s));
      const g = new THREE.ExtrudeGeometry(sh, { depth: h, bevelEnabled: false, curveSegments: 48 });
      g.rotateX(-Math.PI / 2);
      g.translate(0, -h/2, 0);
      return g;
    }

    const colors = { mother: 0xff0000, small: 0x00ff00, large: 0x0000ff, far: 0xffaa00, near: 0x00ffff };
    [
      { n: 'mother', r1: 3.55, r2: 4.70, y: 0 },
      { n: 'small',  r1: 2.10, r2: 3.25, y: 0 },
      { n: 'large',  r1: 5.00, r2: 6.15, y: 0 },
      { n: 'far',    r1: 3.55, r2: 4.70, y: 1.40 },
      { n: 'near',   r1: 3.55, r2: 4.70, y: -1.40 }
    ].forEach(spec => {
      const g = geo(spec.r1, spec.r2, 1.10);
      const m = new THREE.Mesh(g, new THREE.MeshBasicMaterial({ color: colors[spec.n] }));
      m.position.y = spec.y;
      scene.add(m);
    });

    renderer.render(scene, camera);
  </script>
</body>
</html>"""

with open(html_path, "w", encoding="utf-8") as f:
    f.write(html)

subprocess.run([
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    "--headless",
    f"--screenshot={raw_png}",
    "--window-size=1000,1000",
    f"file:///{html_path.replace(os.sep, '/')}"
])

im = Image.open(raw_png)
im_flip = im.transpose(Image.FLIP_LEFT_RIGHT)
im_flip.save(flip_png)
print("Color test rendered!")
