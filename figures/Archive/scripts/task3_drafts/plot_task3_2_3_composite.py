import os
import shutil
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrowPatch
from PIL import Image

SCRATCH = r"C:\Users\kqdx\.gemini\antigravity\brain\ce5f745e-eae3-4eca-9e3f-87c5c965cace\scratch"
OUTPUT_DIR = r"d:\HIT\数模2026\eda_figures\task3_candidates"
ARTIFACT_DIR = r"C:\Users\kqdx\.gemini\antigravity\brain\ce5f745e-eae3-4eca-9e3f-87c5c965cace"

def generate_right_subfigure(output_path):
    raw_png = os.path.join(SCRATCH, 'task3_2_3_raw.png')
    img = Image.open(raw_png)
    arr = np.array(img.convert('L'))
    non_white = arr < 250
    y_idx, x_idx = np.where(non_white)
    cx = int((np.min(x_idx) + np.max(x_idx)) / 2)
    cy = int((np.min(y_idx) + np.max(y_idx)) / 2)
    span = max(np.max(x_idx) - np.min(x_idx), np.max(y_idx) - np.min(y_idx))
    pad = int(span * 0.44)
    R_crop = int(span / 2 + pad)

    crop_box = (cx - R_crop, cy - R_crop, cx + R_crop, cy + R_crop)
    base_img = img.crop(crop_box).transpose(Image.FLIP_LEFT_RIGHT)
    cw, ch = base_img.size

    plt.rcParams['mathtext.fontset'] = 'cm'
    plt.rcParams['font.serif'] = ['Times New Roman', 'DejaVu Serif']
    plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'DejaVu Sans']

    m = 0.178
    th = np.arctan(m)
    u = np.array([np.cos(th), np.sin(th)])
    v = np.array([-u[1], u[0]])

    fig, ax = plt.subplots(figsize=(10, 10), dpi=300)
    ax.imshow(base_img, extent=[0, cw, ch, 0])
    ax.set_xlim(0, cw)
    ax.set_ylim(ch, 0)
    ax.axis('off')

    # 1. Coordinate axes (+z, +r)
    orig_x = cw * 0.10
    orig_y = ch * 0.68
    axis_len = cw * 0.090

    z_top = np.array([orig_x, orig_y - axis_len * 1.15])
    r_tip = np.array([orig_x + axis_len * u[0], orig_y + axis_len * u[1]])
    p_orig = np.array([orig_x, orig_y])

    lw_axis = 2.2
    ax.plot([p_orig[0], z_top[0]], [p_orig[1], z_top[1]], color='#111111', lw=lw_axis, solid_capstyle='butt', zorder=20)
    ax.plot([p_orig[0], r_tip[0]], [p_orig[1], r_tip[1]], color='#111111', lw=lw_axis, solid_capstyle='butt', zorder=20)
    ax.plot(orig_x, orig_y, 'o', color='#111111', markersize=2.2, zorder=25)

    hl = 14.0
    hw = 6.5
    fontsize = 17

    # +z arrow
    ax.plot([z_top[0] - hw, z_top[0], z_top[0] + hw],
            [z_top[1] + hl, z_top[1], z_top[1] + hl],
            color='#111111', lw=lw_axis, solid_joinstyle='miter', solid_capstyle='round', zorder=22)
    ax.text(z_top[0], z_top[1] - 16, r'$+z$', fontsize=fontsize, fontweight='bold', color='#111111', ha='center', va='bottom')

    # +r arrow
    p_w1 = r_tip - hl * u + hw * v
    p_w2 = r_tip - hl * u - hw * v
    ax.plot([p_w1[0], r_tip[0], p_w2[0]],
            [p_w1[1], r_tip[1], p_w2[1]],
            color='#111111', lw=lw_axis, solid_joinstyle='miter', solid_capstyle='round', zorder=22)
    ax.text(r_tip[0] + 16, r_tip[1] + 4, r'$+r$', fontsize=fontsize, fontweight='bold', color='#111111', ha='left', va='center')

    # 2. Time labels & collinear arrow (Modification 1)
    # p1 for t + Delta t, p2 for t
    dy = 45.0
    p1 = np.array([444.0, 950.0 + dy])
    p2 = np.array([910.0, 1040.0 + dy])

    ax.text(p1[0], p1[1], r'$t + \Delta t$', fontsize=fontsize, color='#111111', ha='center', va='center', zorder=30)
    ax.text(p2[0], p2[1], r'$t$', fontsize=fontsize, color='#111111', ha='center', va='center', zorder=30)

    # Collinear vector
    dp = p2 - p1
    dist_p = np.linalg.norm(dp)
    up = dp / dist_p

    # Optical center between text boundaries is around x = 696
    t_param = (696.0 - p1[0]) / dp[0]
    p_arrow_center = p1 + t_param * dp

    arrow_len = 150.0
    half_L = arrow_len / 2.0
    p_start = p_arrow_center + half_L * up # tail near t (on the right)
    p_end = p_arrow_center - half_L * up   # tip pointing to t + Delta t (on the left)

    arr_fine = FancyArrowPatch(p_start, p_end,
                               connectionstyle='arc3,rad=0',
                               arrowstyle='-|>,head_length=6.5,head_width=3.8',
                               color='#111111', lw=1.35, zorder=30)
    ax.add_patch(arr_fine)

    temp_path = os.path.join(SCRATCH, 'micro_collinear_temp.png')
    fig.savefig(temp_path, dpi=300, bbox_inches='tight', pad_inches=0.05)
    plt.close(fig)

    c_img = Image.open(temp_path)
    c_arr = np.array(c_img.convert('L'))
    ys, xs = np.where(c_arr < 250)
    pad_x = int((xs.max() - xs.min()) * 0.06)
    pad_y = int((ys.max() - ys.min()) * 0.08)
    final_cropped = c_img.crop((xs.min() - pad_x, ys.min() - pad_y, xs.max() + pad_x, ys.max() + pad_y))
    final_cropped.save(output_path)
    print(f"Generated right subfigure: {output_path}")

def generate_composite_task3_2_3_2(left_img_path, right_img_path, output_name, box_x2=764.0):
    im_left = Image.open(left_img_path).convert('RGBA')
    im_right = Image.open(right_img_path).convert('RGBA')

    W_l, H_l = im_left.size
    W_r, H_r = im_right.size

    target_H_l = 2300.0
    scale_l = target_H_l / float(H_l)
    disp_W_l = W_l * scale_l

    target_H_r = 1750.0
    scale_r = target_H_r / float(H_r)
    disp_W_r = W_r * scale_r
    disp_H_r = target_H_r

    gap = 230.0
    margin_left = 80.0
    margin_right = 80.0
    margin_top = 80.0
    margin_bottom = 80.0

    canvas_H = margin_top + target_H_l + margin_bottom
    canvas_W = margin_left + disp_W_l + gap + disp_W_r + margin_right

    fig = plt.figure(figsize=(canvas_W / 300.0, canvas_H / 300.0), dpi=300)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, canvas_W)
    ax.set_ylim(canvas_H, 0)
    ax.axis('off')

    # 1. Left macro cylinder
    x_l0 = margin_left
    y_l0 = margin_top
    ax.imshow(im_left, extent=[x_l0, x_l0 + disp_W_l, y_l0 + target_H_l, y_l0], zorder=10)

    # 2. Left framing box (Modification 3:
    # Fully encloses the rightmost tip of the red ring at x=753, while leaving clear
    # whitespace before the inner cylinder generatrix at x in [774, 781])
    # Box size: 160 x 160 px
    box_w_raw = 160.0
    box_h_raw = 160.0
    src_x2_raw = box_x2
    src_x1_raw = src_x2_raw - box_w_raw
    src_y1_raw = 1324.0
    src_y2_raw = src_y1_raw + box_h_raw

    src_x1 = x_l0 + src_x1_raw * scale_l
    src_x2 = x_l0 + src_x2_raw * scale_l
    src_y1 = y_l0 + src_y1_raw * scale_l
    src_y2 = y_l0 + src_y2_raw * scale_l
    src_w = src_x2 - src_x1
    src_h = src_y2 - src_y1
    src_cy = (src_y1 + src_y2) / 2.0

    ax.add_patch(Rectangle(
        (src_x1, src_y1), src_w, src_h,
        fill=False, edgecolor='#000000',
        linestyle='-', linewidth=2.2, zorder=15
    ))

    # 3. Right micro card
    x_r0 = margin_left + disp_W_l + gap
    card_pad = 28.0
    y_r0 = src_cy - disp_H_r / 2.0

    card_x = x_r0 - card_pad
    card_y = y_r0 - card_pad
    card_w = disp_W_r + 2 * card_pad
    card_h = disp_H_r + 2 * card_pad

    # 4. Magnifying dashed lines
    line_top_src = (src_x2, src_y1)
    line_top_tgt = (card_x, card_y)
    line_bot_src = (src_x2, src_y2)
    line_bot_tgt = (card_x, card_y + card_h)

    ax.plot([line_top_src[0], line_top_tgt[0]],
            [line_top_src[1], line_top_tgt[1]],
            color='#000000', linestyle=(0, (6, 5)), linewidth=1.8, zorder=12)

    ax.plot([line_bot_src[0], line_bot_tgt[0]],
            [line_bot_src[1], line_bot_tgt[1]],
            color='#000000', linestyle=(0, (6, 5)), linewidth=1.8, zorder=12)

    # 5. Right micro card border
    ax.add_patch(Rectangle(
        (card_x, card_y), card_w, card_h,
        facecolor='#ffffff', edgecolor='#000000',
        linewidth=2.4, zorder=14
    ))

    # 6. Place right micro image
    ax.imshow(im_right, extent=[x_r0, x_r0 + disp_W_r, y_r0 + disp_H_r, y_r0], zorder=16)

    out_file = os.path.join(OUTPUT_DIR, f"{output_name}.png")
    plt.savefig(out_file, dpi=300, facecolor='white', edgecolor='none')
    plt.close()
    aspect = canvas_W / canvas_H
    print(f"Saved {output_name}: canvas={canvas_W:.0f}x{canvas_H:.0f}, aspect={aspect:.2f}, gap={gap}, H_r={target_H_r}")
    return out_file

if __name__ == '__main__':
    clean_micro = os.path.join(SCRATCH, "task3_2_2_arrow_collinear_clean.png")
    macro_left = os.path.join(OUTPUT_DIR, "macro_cylinder_shrinkage_style_c.png")

    generate_right_subfigure(clean_micro)
    
    # Test box_x2 = 764.0 (and 762, 766)
    out1 = generate_composite_task3_2_3_2(macro_left, clean_micro, "task3_2_3_2_final", box_x2=764.0)
    out2 = generate_composite_task3_2_3_2(macro_left, clean_micro, "task3_2_3_2_x2_766", box_x2=766.0)

    # Copy to artifact dir
    shutil.copy2(out1, os.path.join(ARTIFACT_DIR, "task3_2_3_2_final.png"))
    shutil.copy2(out2, os.path.join(ARTIFACT_DIR, "task3_2_3_2_x2_766.png"))
    print("Done building Task 3.2.3.2!")
