# -*- coding: utf-8 -*-
import os
import numpy as np
import matplotlib.pyplot as plt

# User configuration
r_small_in = 2.10
r_small_out = 3.25
width = 1.15
height = 1.10
gap = 0.30
angle_deg = 120.0
theta_half = np.radians(angle_deg / 2.0)

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

# Camera setup
C = np.array([-0.01, 1.86, -8.91])
T = np.array([3.30, 0.00, 0.00])
up = np.array([0.0, 1.0, 0.0])

w = (T - C) / np.linalg.norm(T - C)
u = np.cross(up, w)
u = u / np.linalg.norm(u)
v = np.cross(w, u)

fov = 42.0
f = 1.0 / np.tan(np.radians(fov / 2.0))

def project(pts):
    p_rel = pts - C
    xc = np.dot(p_rel, u)
    yc = np.dot(p_rel, v)
    zc = np.dot(p_rel, w)
    xp = f * xc / zc
    yp = f * yc / zc
    return xp, yp, zc

n_theta = 60
theta_vals = np.linspace(-theta_half, theta_half, n_theta)

elements = []

for ring in rings:
    rin = ring['r_in']
    rout = ring['r_out']
    y0 = ring['y_pos'] - height / 2.0
    y1 = ring['y_pos'] + height / 2.0
    is_m = ring['is_mother']
    
    # 1. Top face (normal [0, 1, 0] -> visible since camera Y > 0)
    for i in range(n_theta - 1):
        t0, t1 = theta_vals[i], theta_vals[i+1]
        v0 = np.array([rin * np.cos(t0),  y1, -rin * np.sin(t0)])
        v1 = np.array([rout * np.cos(t0), y1, -rout * np.sin(t0)])
        v2 = np.array([rout * np.cos(t1), y1, -rout * np.sin(t1)])
        v3 = np.array([rin * np.cos(t1),  y1, -rin * np.sin(t1)])
        
        edges = []
        # Outer arc
        edges.append((v1, v2, 'arc_out'))
        # Inner arc
        edges.append((v3, v0, 'arc_in'))
        if i == 0:
            edges.append((v0, v1, 'rad_start'))
        if i == n_theta - 2:
            edges.append((v2, v3, 'rad_end'))
            
        elements.append({
            'vertices': [v0, v1, v2, v3],
            'normal': np.array([0.0, 1.0, 0.0]),
            'is_mother': is_m,
            'edges': edges,
            'type': 'top'
        })
        
    # 2. Bottom face is strictly BACK-FACING from this camera height (y_cam = 1.86 > 0, looking down)
    # We do NOT add bottom faces or we mark them back-facing.
    
    # 3. Outer cylinder face
    for i in range(n_theta - 1):
        t0, t1 = theta_vals[i], theta_vals[i+1]
        t_mid = (t0 + t1) / 2.0
        norm = np.array([np.cos(t_mid), 0.0, -np.sin(t_mid)])
        
        v0 = np.array([rout * np.cos(t0), y0, -rout * np.sin(t0)])
        v1 = np.array([rout * np.cos(t1), y0, -rout * np.sin(t1)])
        v2 = np.array([rout * np.cos(t1), y1, -rout * np.sin(t1)])
        v3 = np.array([rout * np.cos(t0), y1, -rout * np.sin(t0)])
        
        # Check visibility
        cent = (v0 + v1 + v2 + v3) / 4.0
        if np.dot(norm, cent - C) < 0: # Front facing
            edges = []
            edges.append((v0, v1, 'arc_bot'))
            # Check if adjacent quad is back-facing (silhouette edge!)
            # If i == 0 or previous is back-facing, v0-v3 is silhouette!
            t_prev = t0 - (theta_vals[1] - theta_vals[0])
            norm_prev = np.array([np.cos(t_prev), 0.0, -np.sin(t_prev)])
            cent_prev = np.array([rout * np.cos(t_prev), (y0+y1)/2.0, -rout * np.sin(t_prev)])
            if np.dot(norm_prev, cent_prev - C) >= 0 or i == 0:
                edges.append((v0, v3, 'silh_out'))
            if i == n_theta - 2:
                edges.append((v1, v2, 'vert_cut_end'))
                
            elements.append({
                'vertices': [v0, v1, v2, v3],
                'normal': norm,
                'is_mother': is_m,
                'edges': edges,
                'type': 'outer'
            })

    # 4. Inner cylinder face
    for i in range(n_theta - 1):
        t0, t1 = theta_vals[i], theta_vals[i+1]
        t_mid = (t0 + t1) / 2.0
        norm = np.array([-np.cos(t_mid), 0.0, np.sin(t_mid)])
        
        v0 = np.array([rin * np.cos(t0), y0, -rin * np.sin(t0)])
        v1 = np.array([rin * np.cos(t1), y0, -rin * np.sin(t1)])
        v2 = np.array([rin * np.cos(t1), y1, -rin * np.sin(t1)])
        v3 = np.array([rin * np.cos(t0), y1, -rin * np.sin(t0)])
        
        cent = (v0 + v1 + v2 + v3) / 4.0
        if np.dot(norm, cent - C) < 0: # Front facing
            edges = []
            edges.append((v0, v1, 'arc_bot'))
            if i == 0:
                edges.append((v0, v3, 'vert_cut_start'))
            # Check if next is back-facing (silhouette)
            t_next = t1 + (theta_vals[1] - theta_vals[0])
            norm_next = np.array([-np.cos(t_next), 0.0, np.sin(t_next)])
            cent_next = np.array([rin * np.cos(t_next), (y0+y1)/2.0, -rin * np.sin(t_next)])
            if np.dot(norm_next, cent_next - C) >= 0 or i == n_theta - 2:
                edges.append((v1, v2, 'silh_in'))
                
            elements.append({
                'vertices': [v0, v3, v2, v1],
                'normal': norm,
                'is_mother': is_m,
                'edges': edges,
                'type': 'inner'
            })

    # 5. Front cut face (theta = +theta_half)
    t = theta_half
    norm = np.array([-np.sin(t), 0.0, -np.cos(t)])
    v0 = np.array([rin * np.cos(t),  y0, -rin * np.sin(t)])
    v1 = np.array([rout * np.cos(t), y0, -rout * np.sin(t)])
    v2 = np.array([rout * np.cos(t), y1, -rout * np.sin(t)])
    v3 = np.array([rin * np.cos(t),  y1, -rin * np.sin(t)])
    cent = (v0 + v1 + v2 + v3) / 4.0
    if np.dot(norm, cent - C) < 0:
        elements.append({
            'vertices': [v0, v1, v2, v3],
            'normal': norm,
            'is_mother': is_m,
            'edges': [(v0, v1, 'cut'), (v1, v2, 'cut'), (v2, v3, 'cut'), (v3, v0, 'cut')],
            'type': 'cut_end'
        })

    # 6. Back cut face (theta = -theta_half) is BACK-FACING, culled!

# Process depth and 2D projection
render_list = []
for elem in elements:
    verts = np.array(elem['vertices'])
    cent = np.mean(verts, axis=0)
    depth = np.dot(cent - C, w)
    
    xp, yp, zc = project(verts)
    poly_2d = np.column_stack([xp, yp])
    
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
        'type': elem['type']
    })

# Sort back-to-front
render_list.sort(key=lambda x: x['depth'], reverse=True)

# Render
fig, ax = plt.subplots(figsize=(10, 10), dpi=300)
ax.set_facecolor('white')
fig.patch.set_facecolor('white')

for item in render_list:
    poly_2d = item['poly_2d']
    is_m = item['is_mother']
    
    # Fill face with pure white so it hides what's behind
    poly = plt.Polygon(poly_2d, closed=True, facecolor='#FFFFFF', edgecolor='none', zorder=1)
    ax.add_patch(poly)
    
    # Draw edges
    for (p0, p1, etype) in item['edges']:
        if is_m:
            ax.plot([p0[0], p1[0]], [p0[1], p1[1]], color='#000000', linewidth=2.4, linestyle='-', solid_capstyle='round', zorder=2)
        else:
            ax.plot([p0[0], p1[0]], [p0[1], p1[1]], color='#374151', linewidth=1.2, linestyle=(0, (4, 3)), solid_capstyle='butt', zorder=2)

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

out_path = r"C:\Users\kqdx\.gemini\antigravity\brain\984f8f9b-1caf-4e5e-a827-7c48f241b73b\test_fvm_lineart_culled.png"
plt.tight_layout(pad=0)
plt.savefig(out_path, dpi=300, bbox_inches='tight', facecolor='white', edgecolor='none')
plt.close()
print("Culled line art rendered successfully to:", out_path)
