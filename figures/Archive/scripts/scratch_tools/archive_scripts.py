# -*- coding: utf-8 -*-
import os
import shutil

eda_dir = r"D:\HIT\数模2026\eda_figures"
scripts_dir = os.path.join(eda_dir, "scripts")
os.makedirs(scripts_dir, exist_ok=True)

files_to_move = [
    "plot_fig1_chamber_temp_humidity.py",
    "plot_fig2_chamber_change_rates.py",
    "plot_fig3_boundary_interpolation_inset.py",
    "plot_fig4_chamber_phase_portrait.py",
    "plot_fig5_radius_shrinkage_dynamics.py",
    "plot_fig6_volume_shrinkage_geometry.py",
    "plot_fig7_problem_timescale_timeline.py",
    "plot_eda_figures.py"
]

for f in files_to_move:
    src = os.path.join(eda_dir, f)
    dst = os.path.join(scripts_dir, f)
    if os.path.exists(src):
        shutil.move(src, dst)
        print(f"[Moved] {f} -> scripts/{f}")

# Copy run_all.py to scripts/
src_run_all = os.path.join(eda_dir, "run_all.py")
dst_run_all = os.path.join(scripts_dir, "run_all.py")
if os.path.exists(src_run_all):
    shutil.copy2(src_run_all, dst_run_all)

# Replace root run_all.py with a delegation script
root_run_all_content = '''# -*- coding: utf-8 -*-
"""
快捷批处理启动脚本：自动调用 scripts/run_all.py
"""
import subprocess
import sys
import os

scripts_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "scripts")
script_path = os.path.join(scripts_dir, "run_all.py")

if __name__ == "__main__":
    res = subprocess.run([sys.executable, script_path], cwd=scripts_dir)
    sys.exit(res.returncode)
'''

with open(src_run_all, "w", encoding="utf-8") as f:
    f.write(root_run_all_content.strip() + "\n")

print("[OK] Migration complete")
