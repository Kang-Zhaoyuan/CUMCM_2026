# -*- coding: utf-8 -*-
import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MplPolygon
from matplotlib.collections import PatchCollection, LineCollection

# User configuration
r_small_in = 2.10
r_small_out = 3.25
width = 1.15
height = 1.10
gap = 0.30
angle_deg = 120.0
theta_half = np.radians(angle_deg / 2.0)

# Ring geometry parameters
r_mother_in = r_small_out + gap
r_mother_out = r_mother_in + width

r_large_in = r_mother_out + gap
r_large_out = r_large_in + width

y_far = height + gap
y_near = -(height + gap)

rings = [
    {'name': 'mother', 'r_in': r_mother_in, 'r_out': r_mother_out, 'y_pos': 0.0,    'is_mother': True},
    {'name': 'small',  'r_in': r_small_in,  'r_out': r_small_out,  'y_pos': 0.0,    'is_mother': False},
    {'name': 'large',  'r_in': r_large_in,  'r_out': r_large_out,  'y_pos': 0.0,    'is_mother': False},
    {'name': 'far',    'r_in': r_mother_in, 'r_out': r_mother_out, 'y_pos': y_far,  'is_mother': False},
    {'name': 'near',   'r_in': r_mother_in, 'r_out': r_mother_out, 'y_pos': y_near, 'is_mother': False},
]

# Camera setup from user
C = np.array([-0.01, 1.86, -8.91])
T = np.array([3.30, 0.00, 0.00])
up = np.array([0.0, 1.0, 0.0])

w = (T - C) / np.linalg.norm(T - C) # forward (camera Z)
u = np.cross(up, w)
u = u / np.linalg.norm(u)           # right (camera X)
v = np.cross(w, u)                  # up (camera Y)

fov = 42.0
f = 1.0 / np.tan(np.radians(fov / 2.0))

def project(pts):
    # pts: (..., 3)
    p_rel = pts - C
    xc = np.dot(p_rel, u)
    yc = np.dot(p_rel, v)
    zc = np.dot(p_rel, w)
    xp = f * xc / zc
    yp = f * yc / zc
    return xp, yp, zc

# Let's generate discretized mesh faces for each ring
# Each face will be a quad or polygon with 3D vertices, 2D projected coords, depth zc, normal, and edges
mesh_elements = []

n_theta = 40
theta_vals = np.linspace(-theta_half, theta_half, n_theta)

for ring in rings:
    rin = ring['r_in']
    rout = ring['r_out']
    y0 = ring['y_pos'] - height / 2.0
    y1 = ring['y_pos'] + height / 2.0
    is_m = ring['is_mother']
    
    # 1. Top face (y = y1)
    # Divided into (n_theta - 1) quads
    for i in range(n_theta - 1):
        t0, t1 = theta_vals[i], theta_vals[i+1]
        v0 = np.array([rin * np.cos(t0),  y1, -rin * np.sin(t0)])
        v1 = np.array([rout * np.cos(t0), y1, -rout * np.sin(t0)])
        v2 = np.array([rout * np.cos(t1), y1, -rout * np.sin(t1)])
        v3 = np.array([rin * np.cos(t1),  y1, -rin * np.sin(t1)])
        
        # edges to draw:
        # inner arc edge: v0-v3
        # outer arc edge: v1-v2
        # radial edge: v0-v1 if i==0, v2-v3 if i==n_theta-2
        edges = []
        edges.append((v0, v3, 'arc'))
        edges.append((v1, v2, 'arc'))
        if i == 0:
            edges.append((v0, v1, 'cut'))
        if i == n_theta - 2:
            edges.append((v3, v2, 'cut'))
            
        mesh_elements.append({
            'vertices': [v0, v1, v2, v3],
            'normal': np.array([0.0, 1.0, 0.0]),
            'is_mother': is_m,
            'edges': edges,
            'type': 'top'
        })

    # 2. Bottom face (y = y0)
    for i in range(n_theta - 1):
        t0, t1 = theta_vals[i], theta_vals[i+1]
        v0 = np.array([rin * np.cos(t0),  y0, -rin * np.sin(t0)])
        v1 = np.array([rout * np.cos(t0), y0, -rout * np.sin(t0)])
        v2 = np.array([rout * np.cos(t1), y0, -rout * np.sin(t1)])
        v3 = np.array([rin * np.cos(t1),  y0, -rin * np.sin(t1)])
        
        edges = []
        edges.append((v0, v3, 'arc'))
        edges.append((v1, v2, 'arc'))
        if i == 0:
            edges.append((v0, v1, 'cut'))
        if i == n_theta - 2:
            edges.append((v3, v2, 'cut'))
            
        mesh_elements.append({
            'vertices': [v0, v3, v2, v1], # reversed normal (downward)
            'normal': np.array([0.0, -1.0, 0.0]),
            'is_mother': is_m,
            'edges': edges,
            'type': 'bottom'
        })

    # 3. Outer cylinder face (r = rout)
    for i in range(n_theta - 1):
        t0, t1 = theta_vals[i], theta_vals[i+1]
        t_mid = (t0 + t1) / 2.0
        norm = np.array([np.cos(t_mid), 0.0, -np.sin(t_mid)])
        
        v0 = np.array([rout * np.cos(t0), y0, -rout * np.sin(t0)])
        v1 = np.array([rout * np.cos(t1), y0, -rout * np.sin(t1)])
        v2 = np.array([rout * np.cos(t1), y1, -rout * np.sin(t1)])
        v3 = np.array([rout * np.cos(t0), y1, -rout * np.sin(t0)])
        
        edges = []
        edges.append((v0, v1, 'arc'))
        edges.append((v3, v2, 'arc'))
        if i == 0:
            edges.append((v0, v3, 'vertical'))
        if i == n_theta - 2:
            edges.append((v1, v2, 'vertical'))
            
        mesh_elements.append({
            'vertices': [v0, v1, v2, v3],
            'normal': norm,
            'is_mother': is_m,
            'edges': edges,
            'type': 'outer'
        })

    # 4. Inner cylinder face (r = rin)
    for i in range(n_theta - 1):
        t0, t1 = theta_vals[i], theta_vals[i+1]
        t_mid = (t0 + t1) / 2.0
        norm = np.array([-np.cos(t_mid), 0.0, np.sin(t_mid)]) # inward normal
        
        v0 = np.array([rin * np.cos(t0), y0, -rin * np.sin(t0)])
        v1 = np.array([rin * np.cos(t1), y0, -rin * np.sin(t1)])
        v2 = np.array([rin * np.cos(t1), y1, -rin * np.sin(t1)])
        v3 = np.array([rin * np.cos(t0), y1, -rin * np.sin(t0)])
        
        edges = []
        edges.append((v0, v1, 'arc'))
        edges.append((v3, v2, 'arc'))
        if i == 0:
            edges.append((v0, v3, 'vertical'))
        if i == n_theta - 2:
            edges.append((v1, v2, 'vertical'))
            
        mesh_elements.append({
            'vertices': [v0, v3, v2, v1],
            'normal': norm,
            'is_mother': is_m,
            'edges': edges,
            'type': 'inner'
        })

    # 5. Start cut face (theta = -theta_half)
    t = -theta_half
    norm = np.array([np.sin(t), 0.0, np.cos(t)]) # tangent pointing outward
    v0 = np.array([rin * np.cos(t),  y0, -rin * np.sin(t)])
    v1 = np.array([rout * np.cos(t), y0, -rout * np.sin(t)])
    v2 = np.array([rout * np.cos(t), y1, -rout * np.sin(t)])
    v3 = np.array([rin * np.cos(t),  y1, -rin * np.sin(t)])
    mesh_elements.append({
        'vertices': [v0, v1, v2, v3],
        'normal': norm,
        'is_mother': is_m,
        'edges': [(v0, v1, 'cut'), (v1, v2, 'cut'), (v2, v3, 'cut'), (v3, v0, 'cut')],
        'type': 'cut_start'
    })

    # 6. End cut face (theta = +theta_half)
    t = theta_half
    norm = np.array([-np.sin(t), 0.0, -np.cos(t)])
    v0 = np.array([rin * np.cos(t),  y0, -rin * np.sin(t)])
    v1 = np.array([rout * np.cos(t), y0, -rout * np.sin(t)])
    v2 = np.array([rout * np.cos(t), y1, -rout * np.sin(t)])
    v3 = np.array([rin * np.cos(t),  y1, -rin * np.sin(t)])
    mesh_elements.append({
        'vertices': [v0, v3, v2, v1],
        'normal': norm,
        'is_mother': is_m,
        'edges': [(v0, v1, 'cut'), (v1, v2, 'cut'), (v2, v3, 'cut'), (v3, v0, 'cut')],
        'type': 'cut_end'
    })

# Compute depth and projection for each element
render_list = []
for elem in mesh_elements:
    verts = np.array(elem['vertices'])
    centroid = np.mean(verts, axis=0)
    view_dir = centroid - C
    
    # Back-face culling:
    # If normal dot view_dir > 0, normal points away from camera -> back face
    # For open cylindrical sector, outer cylinder is convex, inner cylinder is concave
    # Let's keep all faces but sort them properly, or check dot product
    dot_prod = np.dot(elem['normal'], view_dir)
    
    # Calculate depth of centroid along camera forward axis w
    depth = np.dot(centroid - C, w)
    
    # Project vertices to 2D
    xp, yp, zc = project(verts)
    poly_2d = np.column_stack([xp, yp])
    
    # Project edges to 2D
    proj_edges = []
    for e0, e1, etype in elem['edges']:
        x0, y0, _ = project(e0)
        x1, y1, _ = project(e1)
        proj_edges.append(((x0, y0), (x1, y1), etype))
        
    render_list.append({
        'depth': depth,
        'poly_2d': poly_2d,
        'is_mother': elem['is_mother'],
        'edges': proj_edges,
        'back_facing': dot_prod > 0.05,
        'type': elem['type']
    })

# Sort back-to-front (largest depth first)
render_list.sort(key=lambda x: x['depth'], reverse=True)

# Now render with matplotlib
fig, ax = plt.subplots(figsize=(10, 10), dpi=300)
ax.set_facecolor('white')
fig.patch.set_facecolor('white')

# Render faces and edges back-to-front
for item in render_list:
    # Back facing faces can still occlude if inside concave shapes, but let's see
    poly_2d = item['poly_2d']
    is_m = item['is_mother']
    
    # Draw face polygon to occlude elements behind it
    # Mother ring has pure crisp white, other rings have very slightly shaded off-white or white
    face_col = '#FFFFFF'
    
    poly = plt.Polygon(poly_2d, closed=True, facecolor=face_col, edgecolor='none', zorder=1)
    ax.add_patch(poly)
    
    # Draw edges
    # For mother ring: solid bold black line
    # For other rings: dashed dark line
    for (p0, p1, etype) in item['edges']:
        if is_m:
            ax.plot([p0[0], p1[0]], [p0[1], p1[1]], color='#000000', linewidth=2.2, linestyle='-', solid_capstyle='round', zorder=2)
        else:
            ax.plot([p0[0], p1[0]], [p0[1], p1[1]], color='#4B5563', linewidth=1.2, linestyle=(0, (4, 3)), solid_capstyle='butt', zorder=2)

# Set axis limits with margin
all_x = [p[0] for item in render_list for p in item['poly_2d']]
all_y = [p[1] for item in render_list for p in item['poly_2d']]
x_min, x_max = min(all_x), max(all_x)
y_min, y_max = min(all_y), max(all_y)
dx = x_max - x_min
dy = y_max - y_min
pad = 0.08
ax.set_xlim(x_min - dx * pad, x_max + dx * pad)
ax.set_ylim(y_min - dy * pad, y_max + dy * pad)

ax.set_aspect('equal')
ax.axis('off')

out_path = r"C:\Users\kqdx\.gemini\antigravity\brain\984f8f9b-1caf-4e5e-a827-7c48f241b73b\test_fvm_lineart.png"
plt.tight_layout(pad=0)
plt.savefig(out_path, dpi=300, bbox_inches='tight', facecolor='white', edgecolor='none')
plt.close()
print("Line art rendered successfully to:", out_path)
