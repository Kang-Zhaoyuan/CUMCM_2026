import os
import subprocess
import shutil
import numpy as np
from PIL import Image

SCRATCH_DIR = r"C:\Users\kqdx\.gemini\antigravity\brain\984f8f9b-1caf-4e5e-a827-7c48f241b73b\scratch"
EDA_DIR = r"D:\HIT\数模2026\eda_figures"
edge_exe = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

def render_and_crop(scale_factor, name):
    W, H = 2600, 2600
    
    # Target and original camera position
    target = np.array([3.30, 0.00, 0.00])
    cam_orig = np.array([-0.01, 1.86, -8.91])
    cam_pos = target + (cam_orig - target) * scale_factor
    
    three_js_path = os.path.join(EDA_DIR, 'three.min.js').replace('\\', '/')
    html_content = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <script src="{three_js_path}"></script>
  <style>
    * {{ margin: 0; padding: 0; }}
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
    const sweepAngleDeg = 120.0;

    const r_mother_in = r_small_out + gap; // 3.55
    const r_mother_out = r_mother_in + delta_r; // 4.70
    const r_large_in = r_mother_out + gap; // 5.00
    const r_large_out = r_large_in + delta_r; // 6.15

    const y_far = delta_z + gap; // 1.40
    const y_near = -(delta_z + gap); // -1.40

    function createRingSectorGeometry(rIn, rOut, h, sweepDeg) {{
      const sweepRad = (sweepDeg * Math.PI) / 180.0;
      const startAngle = -sweepRad / 2.0;
      const endAngle = sweepRad / 2.0;

      const shape = new THREE.Shape();
      const segs = Math.max(32, Math.floor(96 * (sweepDeg / 360.0)));

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

    const ringSpecs = [
      {{ name: 'mother', rIn: r_mother_in, rOut: r_mother_out, y: 0.0, isMother: true }},
      {{ name: 'small',  rIn: r_small_in,  rOut: r_small_out,  y: 0.0, isMother: false }},
      {{ name: 'large',  rIn: r_large_in,  rOut: r_large_out,  y: 0.0, isMother: false }},
      {{ name: 'far',    rIn: r_mother_in, rOut: r_mother_out, y: y_far, isMother: false }},
      {{ name: 'near',   rIn: r_mother_in, rOut: r_mother_out, y: y_near, isMother: false }}
    ];

    ringSpecs.forEach(spec => {{
      const geo = createRingSectorGeometry(spec.rIn, spec.rOut, delta_z, sweepAngleDeg);
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

    renderer.render(scene, camera);
  </script>
</body>
</html>
"""
    html_file = os.path.join(SCRATCH_DIR, f"scale_{name}.html")
    raw_png = os.path.join(SCRATCH_DIR, f"scale_{name}_raw.png")
    final_png = os.path.join(SCRATCH_DIR, f"scale_{name}_final.png")
    
    with open(html_file, "w", encoding="utf-8") as f:
        f.write(html_content)
        
    norm_url = f"file:///{html_file.replace(os.sep, '/')}"
    cmd = [
        edge_exe,
        "--headless",
        f"--screenshot={raw_png}",
        f"--window-size={W},{H}",
        norm_url
    ]
    subprocess.run(cmd, capture_output=True)
    
    # Centering projection
    C = cam_pos
    T = target
    up = np.array([0.0, 1.0, 0.0])
    w_vec = (T - C) / np.linalg.norm(T - C)
    u_vec = np.cross(up, w_vec)
    u_vec = u_vec / np.linalg.norm(u_vec)
    v_vec = np.cross(w_vec, u_vec)
    fov = 42.0
    f_proj = 1.0 / np.tan(np.radians(fov / 2.0))

    def to_screen(P):
        p_rel = P - C
        xc = np.dot(p_rel, u_vec)
        yc = np.dot(p_rel, v_vec)
        zc = np.dot(p_rel, w_vec)
        ndc_x = f_proj * xc / zc
        ndc_y = f_proj * yc / zc
        sx = (ndc_x + 1.0) * 0.5 * W
        sy = (1.0 - ndc_y) * 0.5 * H
        return sx, sy

    rin_m = 3.55
    rout_m = 4.70
    h_m = 1.10
    t_half = np.radians(60.0)
    mother_pts = []
    for t in np.linspace(-t_half, t_half, 50):
        for r in [rin_m, rout_m]:
            for y in [-h_m / 2.0, h_m / 2.0]:
                P = np.array([r * np.cos(t), y, -r * np.sin(t)])
                mother_pts.append(to_screen(P))

    mother_pts = np.array(mother_pts)
    m_xmin, m_ymin = np.min(mother_pts, axis=0)
    m_xmax, m_ymax = np.max(mother_pts, axis=0)
    cx_mother = (m_xmin + m_xmax) / 2.0
    cy_mother = (m_ymin + m_ymax) / 2.0

    img = Image.open(raw_png).convert("RGBA")
    arr = np.array(img.convert("L"))
    non_white = arr < 250
    y_idx, x_idx = np.where(non_white)
    
    x_min_all, x_max_all = int(np.min(x_idx)), int(np.max(x_idx))
    y_min_all, y_max_all = int(np.min(y_idx)), int(np.max(y_idx))
    print(f"[{name}] scale={scale_factor:.2f} Raw extent: X=[{x_min_all}, {x_max_all}], Y=[{y_min_all}, {y_max_all}] (Frame: {W}x{H})")
    
    dx1 = abs(x_min_all - cx_mother)
    dx2 = abs(x_max_all - cx_mother)
    dy1 = abs(y_min_all - cy_mother)
    dy2 = abs(y_max_all - cy_mother)
    padding = 120
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
    square_img.paste(cropped_part, (src_x1 - crop_box[0], src_y1 - crop_box[1]))
    
    final_img = square_img.transpose(Image.FLIP_LEFT_RIGHT)
    final_img.save(final_png)
    print(f"[{name}] Saved square image size: {final_img.size}")

if __name__ == "__main__":
    for s, name in [(1.30, "130"), (1.40, "140"), (1.50, "150")]:
        render_and_crop(s, name)
