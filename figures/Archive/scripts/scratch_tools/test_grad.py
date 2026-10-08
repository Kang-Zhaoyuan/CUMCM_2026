import os
import subprocess
import numpy as np

SCRATCH = r"C:\Users\kqdx\.gemini\antigravity\brain\984f8f9b-1caf-4e5e-a827-7c48f241b73b\scratch"
EDA_DIR = r"D:\HIT\数模2026\eda_figures"
three_js_path = os.path.join(EDA_DIR, "three.min.js").replace('\\', '/')
edge_exe = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

# Test generating a flared arrow shape in Three.js
test_html = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <script src="{three_js_path}"></script>
</head>
<body>
<canvas id="gradCanvas" width="256" height="32" style="display:none;"></canvas>
<div id="container"></div>
<script>
  // Create gradient texture: tail faded -> head solid red
  const canvas = document.getElementById('gradCanvas');
  const ctx = canvas.getContext('2d');
  const grad = ctx.createLinearGradient(0, 0, 256, 0);
  grad.addColorStop(0.0, 'rgba(255, 30, 30, 0.15)');
  grad.addColorStop(0.4, 'rgba(245, 25, 25, 0.65)');
  grad.addColorStop(0.85, 'rgba(230, 15, 15, 1.0)');
  grad.addColorStop(1.0, 'rgba(220, 10, 10, 1.0)');
  ctx.fillStyle = grad;
  ctx.fillRect(0, 0, 256, 32);

  const gradTexture = new THREE.CanvasTexture(canvas);

  console.log("Canvas texture created successfully");
</script>
</body>
</html>
"""

test_path = os.path.join(SCRATCH, "test_grad.html")
with open(test_path, "w", encoding="utf-8") as f:
    f.write(test_html)

print("Saved test_grad.html")
