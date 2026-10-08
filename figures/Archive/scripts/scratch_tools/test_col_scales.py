import os
import subprocess
from PIL import Image
import numpy as np

SCRATCH = r"C:\Users\kqdx\.gemini\antigravity\brain\984f8f9b-1caf-4e5e-a827-7c48f241b73b\scratch"
three_js = "D:/HIT/数模2026/eda_figures/three.min.js"
edge_exe = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

for scale in [1.30, 1.40, 1.50]:
    target = np.array([3.30, 0.0, 0.0])
    cam_orig = np.array([-0.01, 1.86, -8.91])
    cam_pos = target + (cam_orig - target) * scale
    
    html = f"""<!DOCTYPE html>
<html>
<head>
  <script src="{three_js}"></script>
  <style> * {{ margin: 0; padding: 0; }} body {{ background: #fff; overflow: hidden; }} </style>
</head>
<body>
  <script>
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0xFFFFFF);
    const camera = new THREE.PerspectiveCamera(42, 1, 0.1, 100);
    camera.position.set({cam_pos[0]:.4f}, {cam_pos[1]:.4f}, {cam_pos[2]:.4f});
    camera.lookAt(new THREE.Vector3(3.30, 0, 0));
    const renderer = new THREE.WebGLRenderer({{ antialias: true, preserveDrawingBuffer: true }});
    renderer.setSize(1200, 1200);
    document.body.appendChild(renderer.domElement);

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

    const colors = {{ mother: 0xff0000, small: 0x00ff00, large: 0x0000ff, far: 0xffaa00, near: 0x00ffff }};
    [
      {{ n: 'mother', r1: 3.55, r2: 4.70, y: 0 }},
      {{ n: 'small',  r1: 2.10, r2: 3.25, y: 0 }},
      {{ n: 'large',  r1: 5.00, r2: 6.15, y: 0 }},
      {{ n: 'far',    r1: 3.55, r2: 4.70, y: 1.40 }},
      {{ n: 'near',   r1: 3.55, r2: 4.70, y: -1.40 }}
    ].forEach(spec => {{
      const g = geo(spec.r1, spec.r2, 1.10);
      const m = new THREE.Mesh(g, new THREE.MeshBasicMaterial({{ color: colors[spec.n] }}));
      m.position.y = spec.y;
      scene.add(m);
    }});

    renderer.render(scene, camera);
  </script>
</body>
</html>"""
    hpath = os.path.join(SCRATCH, f"col_{scale}.html")
    rpath = os.path.join(SCRATCH, f"col_{scale}_raw.png")
    fpath = os.path.join(SCRATCH, f"col_{scale}_flip.png")
    with open(hpath, "w", encoding="utf-8") as f:
        f.write(html)
    norm_url = f"file:///{hpath.replace(os.sep, '/')}"
    subprocess.run([edge_exe, "--headless", f"--screenshot={rpath}", "--window-size=1200,1200", norm_url])
    im = Image.open(rpath).transpose(Image.FLIP_LEFT_RIGHT)
    im.save(fpath)
    
    arr = np.array(im)
    blue_mask = (arr[:, :, 2] > 200) & (arr[:, :, 0] < 50) & (arr[:, :, 1] < 50)
    y_idx, x_idx = np.where(blue_mask)
    print(f"Scale {scale}: Blue visible X=[{np.min(x_idx)}, {np.max(x_idx)}], Y=[{np.min(y_idx)}, {np.max(y_idx)}]")
