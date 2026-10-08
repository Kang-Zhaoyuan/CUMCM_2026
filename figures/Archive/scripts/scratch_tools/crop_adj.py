from PIL import Image

for name in ['adj_opt1', 'adj_opt2']:
    fpath = rf"C:\Users\kqdx\.gemini\antigravity\brain\984f8f9b-1caf-4e5e-a827-7c48f241b73b\scratch\{name}.png"
    img = Image.open(fpath)
    W, H = img.size
    cx, cy = W // 2, H // 2
    crop_size = 450
    box = (cx - crop_size, cy - crop_size, cx + crop_size, cy + crop_size)
    cropped = img.crop(box)
    cropped.save(rf"C:\Users\kqdx\.gemini\antigravity\brain\984f8f9b-1caf-4e5e-a827-7c48f241b73b\scratch\crop_{name}.png")

print("Cropped both!")
