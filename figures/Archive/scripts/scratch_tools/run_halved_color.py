import os
import subprocess
import numpy as np
from PIL import Image

SCRATCH = r"C:\Users\kqdx\.gemini\antigravity\brain\984f8f9b-1caf-4e5e-a827-7c48f241b73b\scratch"
EDA_DIR = r"D:\HIT\数模2026\eda_figures"
three_js_path = os.path.join(EDA_DIR, "three.min.js").replace('\\', '/')
edge_exe = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

# 1. First test: Halved angle: startAngle = 0 deg, endAngle = 60 deg
# Let's render the colored version to see the exact silhouette boundaries of all 5 rings!
W, H = 2600, 2600
scale_factor = 1.45

target = np.array([3.30, 0.00, 0.00])
cam_orig = np.array([-0.01, 1.86, -8.91])
cam_pos = target + (cam_orig - target) * scale_factor

html_color = f"""<!DOCTYPE html>
<html>
<head>
  <script src="{three_js_path}"></script>
  <style> * {{ margin: 0; padding: 0; }} body {{ background: #fff; overflow: hidden; }} </style>
</head>
<body>
  <script>
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0xFFFFFF);
    const camera = new THREE.PerspectiveCamera(42, 1, 0.1, 100);
    camera.position.set({cam_pos[0]:.4f}, {cam_pos[1]:.4f}, {cam_pos[2]:.4f});
    camera.lookAt(new THREE.Vector3({target[0]:.4f}, {target[1]:.4f}, {target[2]:.4f}));
    const renderer = new THREE.WebGLRenderer({{ antialias: true, preserveDrawingBuffer: true }});
    renderer.setSize({W}, {H});
    document.body.appendChild(renderer.domElement);

    const delta_r = 1.15, delta_z = 1.10, gap = 0.30;
    const r_small_in = 2.10, r_small_out = 3.25;
    const r_mother_in = 3.55, r_mother_out = 4.70;
    const r_large_in = 5.00, r_large_out = 6.15;

    // Angle halved: start from 0 deg to 60 deg (near face at 60 deg kept fixed)
    function geo(rIn, rOut, h) {{
      const s = 0.0;
      const e = (60.0 * Math.PI) / 180.0;
      const sh = new THREE.Shape();
      sh.absarc(0, 0, rOut, s, e, false);
      sh.lineTo(rIn * Math.cos(e), rIn * Math.sin(e));
      sh.absarc(0, 0, rIn, e, s, true);
      sh.lineTo(rOut * Math.cos(s), rOut * Math.sin(s));
      const g = new THREE.ExtrudeGeometry(sh, {{ depth: h, bevelEnabled: false, curveSegments: 64 }});
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
      const g = geo(spec.r1, spec.r2, delta_z);
      const m = new THREE.Mesh(g, new THREE.MeshBasicMaterial({{ color: colors[spec.n] }}));
      m.position.y = spec.y;
      scene.add(m);
    }});

    renderer.render(scene, camera);
  </script>
</body>
</html>"""

hpath = os.path.join(SCRATCH, "test_halved_color.html")
rpath = os.path.join(SCRATCH, "test_halved_color_raw.png")
fpath = os.path.join(SCRATCH, "test_halved_color_flip.png")

with open(hpath, "w", encoding="utf-8") as f:
    f.write(html_color)

norm_url = f"file:///{hpath.replace(os.sep, '/')}"
subprocess.run([edge_exe, "--headless", f"--screenshot={rpath}", f"--window-size={W},{H}", norm_url])
im = Image.open(rpath).transpose(Image.FLIP_LEFT_RIGHT)
im.save(fpath)
print("Rendered halved color test successfully!")
