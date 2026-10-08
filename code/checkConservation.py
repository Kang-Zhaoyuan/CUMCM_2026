"""检查问题1有限体积空间离散的瞬时全局守恒性。"""
import argparse, json
import numpy as np

from grid import Grid, R, H, HM, RHO_CP


def test_state(grid,seed):
    rng=np.random.default_rng(seed)
    return rng.uniform(28.,55.,grid.n),rng.uniform(.2,2.55,grid.n)


def balance_result(lhs,rhs,tolerance):
    absolute=abs(lhs-rhs); relative=absolute/max(abs(lhs),abs(rhs),np.finfo(float).tiny)
    return dict(volume_rate=float(lhs),boundary_inflow=float(rhs),absolute_residual=float(absolute),
                relative_residual=float(relative),passed=bool(relative<=tolerance))


def check(nr=120,nz=120,stretch=2.,seed=2026,tolerance=1e-10):
    grid=Grid(nr,nz,stretch); temperature,moisture=test_state(grid,seed); air=np.array([50.,.05])
    temperature_rate=grid.rhs(temperature,air[0],False)
    moisture_rate=grid.rhs(moisture,air[1],True)
    heat=balance_result(np.dot(RHO_CP*grid.v,temperature_rate),H*np.dot(grid.surface,air[0]-temperature),tolerance)
    mass=balance_result(np.dot(grid.v,moisture_rate),HM*np.dot(grid.surface,air[1]-moisture),tolerance)
    return dict(problem=1,nr=nr,nz=nz,stretch=stretch,seed=seed,tolerance=tolerance,radius_cm=R*100,
                heat=heat,moisture=mass,passed=heat['passed'] and mass['passed'])


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--nr',type=int,default=120); parser.add_argument('--nz',type=int,default=120)
    parser.add_argument('--stretch',type=float,default=2.); parser.add_argument('--seed',type=int,default=2026)
    parser.add_argument('--tolerance',type=float,default=1e-10)
    result=check(**vars(parser.parse_args())); print(json.dumps(result,ensure_ascii=False,indent=2))
    if not result['passed']: raise SystemExit(1)


if __name__=='__main__': main()

