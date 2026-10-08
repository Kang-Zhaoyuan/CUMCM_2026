from PIL import Image

fpath = r"C:\Users\kqdx\.gemini\antigravity\brain\984f8f9b-1caf-4e5e-a827-7c48f241b73b\scratch\test_var3_cutplane_gradient_final.png"
img = Image.open(fpath)
W, H = img.size

# Center crop of the mother ring and arrows
cx, cy = W // 2, H // 2
crop_size = 500
box = (cx - crop_size, cy - crop_size, cx + crop_size, cy + crop_size)
cropped = img.crop(box)
cropped.save(r"C:\Users\kqdx\.gemini\antigravity\brain\984f8f9b-1caf-4e5e-a827-7c48f241b73b\scratch\crop_var3_detail.png")
print("Saved crop_var3_detail.png")
