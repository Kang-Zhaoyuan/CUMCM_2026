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

# Base template function
def generate_html(arrow_config_js):
    return f"""<!DOCTYPE html>
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

    // 3D Arrow Helper Builder
    function addArrow3D(pStart, pEnd, shaftR, headR, headLen, hexColor) {{
      const dir = new THREE.Vector3().subVectors(pEnd, pStart);
      const totalLen = dir.length();
      const actualHeadLen = Math.min(headLen, totalLen * 0.45);
      const shaftLen = totalLen - actualHeadLen;

      const mat = new THREE.MeshBasicMaterial({{ color: hexColor }});

      // Shaft
      const shaftGeo = new THREE.CylinderGeometry(shaftR, shaftR, shaftLen, 20);
      shaftGeo.translate(0, shaftLen / 2, 0);
      shaftGeo.rotateX(Math.PI / 2);
      const shaftMesh = new THREE.Mesh(shaftGeo, mat);
      shaftMesh.position.copy(pStart);
      shaftMesh.lookAt(pEnd);
      scene.add(shaftMesh);

      // Head cone
      const headGeo = new THREE.ConeGeometry(headR, actualHeadLen, 20);
      headGeo.translate(0, actualHeadLen / 2, 0);
      headGeo.rotateX(Math.PI / 2);
      const headMesh = new THREE.Mesh(headGeo, mat);
      const headPos = new THREE.Vector3().copy(pStart).addScaledVector(dir.clone().normalize(), shaftLen);
      headMesh.position.copy(headPos);
      headMesh.lookAt(pEnd);
      scene.add(headMesh);
    }}

    // Inject custom arrows
    {arrow_config_js}

    renderer.render(scene, camera);
  </script>
</body>
</html>
"""

print("Generator script loaded.")
