# -*- coding: utf-8 -*-
"""
一键批量运行本目录下全部 5 大正式学术图件绘图脚本
"""
import subprocess
import sys
import os

scripts = [
    'plot_fig1_chamber_temp_humidity.py',
    'plot_fig5_radius_shrinkage_dynamics.py',
    'plot_result2_lines.py',
    'plot_fvm_multiscale_macro_micro.py',
    'plot_cylinder_geometry_symbols.py',
    'plot_moving_boundary_mesh_shrinkage.py',
    'plot_fig_q3_tail_sensitivity.py'
]

cur_dir = os.path.dirname(os.path.abspath(__file__))

print('=' * 70)
print(f'>>> 开始一键执行全部 {len(scripts)} 个正式学术绘图脚本...')
print('=' * 70)

env = dict(os.environ)
env['PYTHONUTF8'] = '1'

for idx, s in enumerate(scripts, start=1):
    script_path = os.path.join(cur_dir, s)
    print(f'[{idx}/{len(scripts)}] 正在执行: {s} ...')
    res = subprocess.run([sys.executable, s], cwd=cur_dir, env=env)
    if res.returncode != 0:
        print(f'[×] 执行失败: {s}, 退出码: {res.returncode}')
        sys.exit(res.returncode)

print('=' * 70)
print(f'>>> [SUCCESS] 全部 {len(scripts)} 张学术图件已成功生成并输出至 eda_figures 根目录！')
print('=' * 70)
