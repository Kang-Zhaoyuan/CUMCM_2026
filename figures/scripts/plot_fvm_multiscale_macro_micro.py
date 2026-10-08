"""
Composite script: Stitch macro cylinder and micro 5-ring FVM topology into a single A4 full-width figure.
Includes:
- Left: fvm_macro_cylinder.png (Macro-scale cylindrical domain & mesh)
- Right: fvm_flux_annotated_v2.png (Micro-scale 5-ring FVM topology & heat flux vectors)
- Magnifier / Inset zoom callout effect connecting the red ring on the left to the right figure.
"""

import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Polygon, FancyBboxPatch, FancyArrowPatch
from PIL import Image

# TeX Computer Modern font settings & Chinese fonts
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'DejaVu Sans']
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['mathtext.fontset'] = 'cm'

def create_composite_figure(output_path,
                            left_img_path,
                            right_img_path,
                            conn_type='dashed',      # 默认 2A 风格
                            box_style='black_solid', # 黑色实线方框
                            arrow_target='center',
                            gap=520.0):              # 靠近左图与右图，画布总宽缩窄约 10%
    """
    conn_type:
      'arrow': Reference 1 (XRD style) - Single bold black arrow pointing to the magnified card
      'dashed': Reference 2 (Volcano style) - Two black dashed ray lines connecting corresponding corners
    box_style:
      'red_dashed': Sharp red dashed box (like Reference 1, highlighting the red ring)
      'black_solid': Sharp black solid box (like Reference 2 Volcano plot)
    """
    im_left = Image.open(left_img_path).convert('RGBA')
    im_right_raw = Image.open(right_img_path).convert('RGBA')
    
    # 紧密裁剪右图，去除多余白边 (原图 2334x2334，有效内容 x: 139~1963, y: 183~2210)
    # 裁切为 x: 60~2060 (宽 2000), y: 100~2260 (高 2160)
    im_right = im_right_raw.crop((60, 100, 2060, 2260))
    
    W_l, H_l = im_left.size
    W_r, H_r = im_right.size
    
    # 统一目标高度与画布布局 (针对 A4 横向通栏比例设计，高宽比约 1 : 1.85)
    target_H = 2200.0
    scale_l = target_H / float(H_l)
    scale_r = target_H / float(H_r)
    
    disp_W_l = W_l * scale_l   # ~ 1124 px
    disp_W_r = W_r * scale_r   # ~ 2037 px
    
    # 画布尺寸规划：纯净无文字，适度上下安全边距
    margin_left = 90.0
    margin_right = 90.0
    margin_top = 70.0
    margin_bottom = 70.0
    
    canvas_W = margin_left + disp_W_l + gap + disp_W_r + margin_right
    canvas_H = margin_top + target_H + margin_bottom
    
    # 使用 Matplotlib 创建超高分辨率合成画布 (300 DPI)
    fig = plt.figure(figsize=(canvas_W / 300.0, canvas_H / 300.0), dpi=300)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, canvas_W)
    ax.set_ylim(canvas_H, 0)   # Y 轴向下，符合图像坐标系
    ax.axis('off')
    
    # -------------------------------------------------------------
    # 1. 放置左侧宏观圆柱图件
    # -------------------------------------------------------------
    x_l0 = margin_left
    y_l0 = margin_top
    ax.imshow(im_left, extent=[x_l0, x_l0 + disp_W_l, y_l0 + target_H, y_l0], zorder=10)
    
    # -------------------------------------------------------------
    # 2. 放置右侧微观五环热通量图件 (棱角分明、边界为黑线的外框)
    # -------------------------------------------------------------
    x_r0 = margin_left + disp_W_l + gap
    y_r0 = margin_top
    
    # 右侧卡片背景与棱角分明的黑色实线外框 (Sharp 90-degree black rectangular border)
    card_pad = 28.0
    card_x = x_r0 - card_pad
    card_y = y_r0 - card_pad
    card_w = disp_W_r + 2 * card_pad
    card_h = target_H + 2 * card_pad
    
    # 纯白底衬 + 纯黑锐利实线矩形框 (严格按照用户要求：棱角分明、边界为黑线)
    ax.add_patch(Rectangle(
        (card_x, card_y), card_w, card_h,
        facecolor='#ffffff', edgecolor='#000000',
        linewidth=2.4, zorder=8
    ))
    
    ax.imshow(im_right, extent=[x_r0, x_r0 + disp_W_r, y_r0 + target_H, y_r0], zorder=10)
    
    # -------------------------------------------------------------
    # 3. 计算左图红色圆环右侧微元切片的精确定位框
    # -------------------------------------------------------------
    # 红色圆环右边缘弧段微元范围: x in [610, 735], y in [1275, 1418]
    src_x1_raw = 610.0
    src_x2_raw = 735.0
    src_y1_raw = 1275.0
    src_y2_raw = 1418.0
    
    src_x1 = x_l0 + src_x1_raw * scale_l
    src_x2 = x_l0 + src_x2_raw * scale_l
    src_y1 = y_l0 + src_y1_raw * scale_l
    src_y2 = y_l0 + src_y2_raw * scale_l
    
    src_w = src_x2 - src_x1
    src_h = src_y2 - src_y1
    
    # 棱角分明的局部源取景框 (Sharp rectangle)
    if box_style == 'red_dashed':
        # 参考图 1：红色虚线/点划线框 (突出显示局部微元，与红色物料环视觉呼应)
        ax.add_patch(Rectangle(
            (src_x1, src_y1), src_w, src_h,
            fill=False, edgecolor='#dc2626',
            linestyle=(0, (6, 4)), linewidth=2.5, zorder=15
        ))
    elif box_style == 'black_solid':
        # 参考图 2：黑色实线矩形方框 (经典火山图风格)
        ax.add_patch(Rectangle(
            (src_x1, src_y1), src_w, src_h,
            fill=False, edgecolor='#000000',
            linestyle='-', linewidth=2.2, zorder=15
        ))
    elif box_style == 'black_dashed':
        # 黑色虚线矩形方框
        ax.add_patch(Rectangle(
            (src_x1, src_y1), src_w, src_h,
            fill=False, edgecolor='#000000',
            linestyle=(0, (6, 4)), linewidth=2.2, zorder=15
        ))
    
    # -------------------------------------------------------------
    # 4. 连接过渡效果 (彻底移除任何浅蓝色图像或半透明面填充)
    # -------------------------------------------------------------
    if conn_type == 'arrow':
        # 【风格 1：参考图 1 (XRD 风格)】 使用实心黑色箭头连接两张图
        src_cx = src_x2 + 8.0
        src_cy = (src_y1 + src_y2) / 2.0
        
        if arrow_target == 'center':
            tgt_x = card_x - 18.0
            tgt_y = card_y + card_h / 2.0
        else: # horizontal
            tgt_x = card_x - 18.0
            tgt_y = src_cy
        
        # 优雅大气的科研黑色实心引导箭头 (与参考图 1 风格一致)
        arrow = FancyArrowPatch(
            (src_cx, src_cy), (tgt_x, tgt_y),
            arrowstyle='-|>,head_length=18,head_width=11',
            mutation_scale=1.0,
            color='#000000',
            linewidth=2.8,
            zorder=20
        )
        ax.add_patch(arrow)
        
    elif conn_type == 'dashed':
        # 【风格 2：参考图 2 (火山图风格)】 黑色细虚线透射连接，无任何背景色
        line_top_src = (src_x2, src_y1)
        line_top_tgt = (card_x, card_y)
        
        line_bot_src = (src_x2, src_y2)
        line_bot_tgt = (card_x, card_y + card_h)
        
        ax.plot([line_top_src[0], line_top_tgt[0]],
                [line_top_src[1], line_top_tgt[1]],
                color='#000000', linestyle=(0, (6, 5)), linewidth=1.8, zorder=15)
        
        ax.plot([line_bot_src[0], line_bot_tgt[0]],
                [line_bot_src[1], line_bot_tgt[1]],
                color='#000000', linestyle=(0, (6, 5)), linewidth=1.8, zorder=15)
    
    # 保存为 300 DPI 超高清晰度图件
    plt.savefig(output_path, dpi=300, facecolor='white', edgecolor='none')
    plt.close()
    print(f"[OK] 成功生成: {output_path}")

def find_image(eda_dir, filename):
    for d in [eda_dir, os.path.join(eda_dir, 'Archive', 'images')]:
        p = os.path.join(d, filename)
        if os.path.exists(p):
            return p
    raise FileNotFoundError(f"找不到子图: {filename}")

if __name__ == '__main__':
    eda_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    left_img = find_image(eda_dir, "fvm_macro_cylinder.png")
    right_img = find_image(eda_dir, "fvm_flux_annotated_v2.png")
    
    # 最终正式版 (2A 风格：黑实线框 + 经典黑色虚线投射 + 直角黑线外框，间距缩窄 10%)
    out_final = os.path.join(eda_dir, "fvm_multiscale_macro_micro.png")
    create_composite_figure(out_final, left_img, right_img, conn_type='dashed', box_style='black_solid', gap=520.0)




