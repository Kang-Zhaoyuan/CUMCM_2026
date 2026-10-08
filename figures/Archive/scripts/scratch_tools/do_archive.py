import os
import shutil

SCRATCH = r"C:\Users\kqdx\.gemini\antigravity\brain\984f8f9b-1caf-4e5e-a827-7c48f241b73b\scratch"
EDA_DIR = r"D:\HIT\数模2026\eda_figures"
ARCH_DIR = os.path.join(EDA_DIR, "Archive")
ARCH_IMG = os.path.join(ARCH_DIR, "images")
ARCH_SCR = os.path.join(ARCH_DIR, "scripts")

os.makedirs(ARCH_IMG, exist_ok=True)
os.makedirs(ARCH_SCR, exist_ok=True)

# 1. Intermediate images in eda_figures to archive
img_files = [
    "flared_c1_balanced.png",
    "flared_c2_wide_flare.png",
    "flared_c3_slender.png",
    "flared_c4_3d_extruded.png",
    "flared_c5_bold_chunky.png",
    "fvm_5rings_lineart.png",
    "raw_fvm_lineart.png",
    "fvm_flux_flared_c2_refined.png",
    "fvm_flux_v1_weight.png",
    "fvm_flux_v2_dual_gradient.png",
    "fvm_flux_v2_updated.png",
    "fvm_flux_v3_triple_gradient.png",
    "fvm_flux_enriched_preview.png",
    "fvm_flux_annotated_v2_beside.png",
    "fvm_flux_annotated_v2_fraction.png",
    "variant_1_shift_moderate.png",
    "variant_2_shift_strong.png",
    "variant_3_scale_110.png",
    "variant_4_scale_118.png",
    "fvm_flux_step2_review.png",
    "fvm_flux_step2_grid.png",
    "fvm_flux_final_grid.png",
]

for f in img_files:
    src = os.path.join(EDA_DIR, f)
    dst = os.path.join(ARCH_IMG, f)
    if os.path.exists(src):
        shutil.move(src, dst)
        print(f"Moved image: {f} -> Archive/images/")

# 2. Intermediate scripts/webgl files in eda_figures to archive
script_files = [
    "OrbitControls.js",
    "three.min.js",
    "render_fvm_lineart.html",
    "fvm_5rings_interactive.html",
    "render_fvm_annotated_v2.py",
]

for f in script_files:
    src = os.path.join(EDA_DIR, f)
    dst = os.path.join(ARCH_SCR, f)
    if os.path.exists(src):
        shutil.move(src, dst)
        print(f"Moved script: {f} -> Archive/scripts/")

# 3. Move plot_fvm_5rings_lineart.py from eda_figures/scripts/
old_lineart_script = os.path.join(EDA_DIR, "scripts", "plot_fvm_5rings_lineart.py")
if os.path.exists(old_lineart_script):
    shutil.move(old_lineart_script, os.path.join(ARCH_SCR, "plot_fvm_5rings_lineart.py"))
    print("Moved plot_fvm_5rings_lineart.py -> Archive/scripts/")

# 4. Copy all scratch exploration scripts to Archive/scripts/scratch_tools/
scratch_tools_dir = os.path.join(ARCH_SCR, "scratch_tools")
os.makedirs(scratch_tools_dir, exist_ok=True)
for item in os.listdir(SCRATCH):
    if item.endswith(('.py', '.html')) and not item.startswith('.'):
        src = os.path.join(SCRATCH, item)
        dst = os.path.join(scratch_tools_dir, item)
        shutil.copy(src, dst)
print("Copied scratch exploration scripts to Archive/scripts/scratch_tools/")

# 5. Remove __pycache__ in eda_figures
pycache = os.path.join(EDA_DIR, "__pycache__")
if os.path.exists(pycache):
    shutil.rmtree(pycache)
    print("Removed __pycache__")

print("Archival file movements complete!")
