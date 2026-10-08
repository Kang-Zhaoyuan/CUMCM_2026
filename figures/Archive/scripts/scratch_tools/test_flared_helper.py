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

# Let's write the complete renderer for flared arrows
def build_flared_arrow_js():
    return """
    // 1D Gradient Texture for Flared Arrow (Standard Pure Red)
    const cGrad = document.createElement('canvas');
    cGrad.width = 256; cGrad.height = 16;
    const ctxG = cGrad.getContext('2d');
    const grad = ctxG.createLinearGradient(0, 0, 256, 0);
    // Tail is soft/translucent, head is opaque vibrant standard red (#FF1E1E)
    grad.addColorStop(0.00, 'rgba(255, 40, 40, 0.12)');
    grad.addColorStop(0.35, 'rgba(255, 25, 25, 0.55)');
    grad.addColorStop(0.70, 'rgba(250, 15, 15, 0.90)');
    grad.addColorStop(1.00, 'rgba(235, 0, 0, 1.0)');
    ctxG.fillStyle = grad;
    ctxG.fillRect(0, 0, 256, 16);
    const gradTex = new THREE.CanvasTexture(cGrad);

    // Cut plane basis vectors (theta = 60 deg)
    const th_cut = (60.0 * Math.PI) / 180.0;
    const e_r = new THREE.Vector3(Math.cos(th_cut), 0, -Math.sin(th_cut));
    const e_y = new THREE.Vector3(0, 1, 0);
    // Outward normal towards camera: (-sin(60), 0, -cos(60))
    const n_cam = new THREE.Vector3(-Math.sin(th_cut), 0, -Math.cos(th_cut)).normalize();

    // Helper to create 2D flared arrow mesh lying on cut face
    function addFlaredArrowCutPlane(pStart, pEnd, wTail, wNeck, wHead, headRatio = 0.35, power = 2.5, lift = 0.02, extrudeDepth = 0) {
      const dir = new THREE.Vector3().subVectors(pEnd, pStart);
      const L = dir.length();
      const u = dir.clone().normalize();
      // Perpendicular vector in cut plane: cross(n_cam, u)
      const v = new THREE.Vector3().crossVectors(n_cam, u).normalize();

      const Lhead = L * headRatio;
      const Lshaft = L - Lhead;

      const segs = 36;
      const vertices = [];
      const uvs = [];
      const indices = [];

      // We construct the 2D local profile:
      // Subdivide shaft into segs steps:
      // Top points and bottom points:
      const ptsTop = [];
      const ptsBot = [];
      const uCoords = [];

      for (let i = 0; i <= segs; i++) {
        const t = i / segs;
        const x = t * Lshaft;
        const w = (wNeck / 2) + ((wTail - wNeck) / 2) * Math.pow(1 - t, power);
        ptsTop.push(new THREE.Vector2(x, w));
        ptsBot.push(new THREE.Vector2(x, -w));
        uCoords.push(t * (Lshaft / L));
      }

      // Build 3D mesh directly with quad strip along shaft:
      // For each slice i: top vertex and bottom vertex
      // 3D position = pStart + x*u + w*v + lift*n_cam
      for (let i = 0; i <= segs; i++) {
        const x = ptsTop[i].x;
        const wT = ptsTop[i].y;
        const wB = ptsBot[i].y;
        const uVal = uCoords[i];

        const pT = pStart.clone().addScaledVector(u, x).addScaledVector(v, wT).addScaledVector(n_cam, lift);
        const pB = pStart.clone().addScaledVector(u, x).addScaledVector(v, wB).addScaledVector(n_cam, lift);

        vertices.push(pT.x, pT.y, pT.z);
        uvs.push(uVal, 1.0);

        vertices.push(pB.x, pB.y, pB.z);
        uvs.push(uVal, 0.0);
      }

      // Shaft indices (quads between slice i and i+1)
      for (let i = 0; i < segs; i++) {
        const i0 = 2 * i;
        const i1 = 2 * i + 1;
        const i2 = 2 * (i + 1);
        const i3 = 2 * (i + 1) + 1;

        indices.push(i0, i1, i2);
        indices.push(i2, i1, i3);
      }

      // Arrowhead base vertices and tip
      const baseIdx = vertices.length / 3;
      const pHeadTop = pStart.clone().addScaledVector(u, Lshaft).addScaledVector(v, wHead / 2).addScaledVector(n_cam, lift);
      const pHeadBot = pStart.clone().addScaledVector(u, Lshaft).addScaledVector(v, -wHead / 2).addScaledVector(n_cam, lift);
      const pTip = pStart.clone().addScaledVector(u, L).addScaledVector(n_cam, lift);

      vertices.push(pHeadTop.x, pHeadTop.y, pHeadTop.z);
      uvs.push(Lshaft / L, 1.0);

      vertices.push(pHeadBot.x, pHeadBot.y, pHeadBot.z);
      uvs.push(Lshaft / L, 0.0);

      vertices.push(pTip.x, pTip.y, pTip.z);
      uvs.push(1.0, 0.5);

      // Head triangle
      indices.push(baseIdx, baseIdx + 1, baseIdx + 2);

      const geom = new THREE.BufferGeometry();
      geom.setAttribute('position', new THREE.Float32BufferAttribute(vertices, 3));
      geom.setAttribute('uv', new THREE.Float32BufferAttribute(uvs, 2));
      geom.setIndex(indices);
      geom.computeVertexNormals();

      const mat = new THREE.MeshBasicMaterial({
        map: gradTex,
        transparent: true,
        side: THREE.DoubleSide,
        depthTest: true
      });

      const mesh = new THREE.Mesh(geom, mat);
      scene.add(mesh);
    }
    """

print("Helper ready.")
