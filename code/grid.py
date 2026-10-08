"""四个问题共用的二维轴对称有限体积网格。"""
import numpy as np
from scipy.sparse import coo_matrix, bmat, diags, block_diag

R, Z, H, HM = .02, .125, 25., 8e-7
RHO_CP, K = 820*2600, .36


class Constant:
    def __init__(self,value): self.value=np.asarray(value)
    def __call__(self,t): return self.value


class DryEvent:
    terminal,direction=True,-1
    def __init__(self,offset): self.offset=offset
    def __call__(self,t,state): return np.max(state[self.offset:])-.15


class Grid:
    def __init__(self,nr=60,nz=60,stretch=2.,shrinking=False):
        self.shrinking=shrinking
        s,q=np.linspace(0,1,nr+1),np.linspace(0,1,nz+1)
        self.r,self.z=R*(1-(1-s)**stretch),Z*(1-(1-q)**stretch)
        rf,zf=(self.r[:-1]+self.r[1:])/2,(self.z[:-1]+self.z[1:])/2
        wr,wz=np.diff(np.r_[0,rf,R]**2)/2,np.diff(np.r_[0,zf,Z])
        self.v=(wr[:,None]*wz).ravel(); ids=np.arange(self.v.size).reshape(nr+1,nz+1)
        self.i=np.r_[ids[:-1].ravel(),ids[:,:-1].ravel()]
        self.j=np.r_[ids[1:].ravel(),ids[:,1:].ravel()]
        self.g=np.r_[((rf/np.diff(self.r))[:,None]*wz).ravel(),(wr[:,None]/np.diff(self.z)).ravel()]
        surface=np.zeros_like(ids,dtype=float); surface[-1]+=R*wz; surface[:,-1]+=wr
        self.surface,self.shape,self.n=surface.ravel(),ids.shape,self.v.size
        if shrinking:
            side=np.zeros_like(ids,dtype=float); side[-1]=R*wz
            self.r0,self.v0,self.g0=self.r.copy(),self.v.copy(),self.g.copy()
            self.side0,self.end0=side.ravel(),self.surface-side.ravel()
            self.radial_edges=nr*(nz+1)

    def geometry(self,radius):
        scale=radius/R; self.r=self.r0*scale; self.v=self.v0*scale**2; self.g=self.g0.copy()
        self.g[self.radial_edges:]*=scale**2; self.surface=self.side0*scale+self.end0*scale**2

    def diffusivity(self,u,moisture):
        if not moisture: return np.full(self.n,K/RHO_CP),np.zeros(self.n)
        if np.any(u<=0): raise ValueError('含水率出现非正值')
        d=7e-9*np.exp(-.89/u)
        return d,.89*d/u**2

    def rhs(self,u,air,moisture):
        d=self.diffusivity(u,moisture)[0]
        flux=self.g*(d[self.i]+d[self.j])/2*(u[self.j]-u[self.i])
        net=np.bincount(self.i,flux,minlength=self.n)-np.bincount(self.j,flux,minlength=self.n)
        beta=HM if moisture else H/RHO_CP
        return (net+beta*self.surface*(air-u))/self.v

    def jacobian(self,u,moisture):
        d,dp=self.diffusivity(u,moisture); i,j,v=self.i,self.j,self.v
        face,jump=(d[i]+d[j])/2,u[j]-u[i]
        left,right=self.g*(dp[i]*jump/2-face),self.g*(dp[j]*jump/2+face)
        beta,ids=(HM if moisture else H/RHO_CP),np.arange(self.n)
        return coo_matrix((np.r_[left/v[i],right/v[i],-left/v[j],-right/v[j],-beta*self.surface/v],
                           (np.r_[i,i,j,j,ids],np.r_[i,j,i,j,ids])),shape=(self.n,self.n)).tocsc()

    def independent(self,t,state,air,jac=False):
        temperature,moisture=state.reshape(2,self.n)
        if jac: return block_diag((self.jacobian(temperature,False),self.jacobian(moisture,True)),format='csc')
        boundary=air(t)
        return np.r_[self.rhs(temperature,boundary[0],False),self.rhs(moisture,boundary[1],True)]

    def balance(self,u,a,air,beta):
        flux=self.g*(a[self.i]+a[self.j])/2*(u[self.j]-u[self.i])
        return np.bincount(self.i,flux,minlength=self.n)-np.bincount(self.j,flux,minlength=self.n)+beta*self.surface*(air-u)

    def block(self,u,a,da,direct,beta,mass):
        i,j=self.i,self.j; jump,face=u[j]-u[i],(a[i]+a[j])/2
        left=self.g*(da[i]*jump/2-direct*face); right=self.g*(da[j]*jump/2+direct*face); ids=np.arange(self.n)
        return coo_matrix((np.r_[left/mass[i],right/mass[i],-left/mass[j],-right/mass[j],-beta*self.surface/mass],
                           (np.r_[i,i,j,j,ids],np.r_[i,j,i,j,ids])),shape=(self.n,self.n)).tocsc()

    def coupled(self,y,air,jac=False):
        t,c=y.reshape(2,self.n)
        if np.any(c<=0) or np.any(t<=-273.15): raise ValueError('物性计算超出定义域')
        r0,rc,c0,cc,k0,kk,d0,dc0=((760,90,1850,2150,.12,.20,4.2e-4,.30)
                                  if self.shrinking else (650,128,1450,2736,.21,.38,2.4e-3,.45))
        rho,cp=r0+rc*c,c0+cc*c/(c+1); cap=rho*cp
        cap_c=rc*cp+rho*cc/(c+1)**2; k,kc=k0+kk*c/(c+1),kk/(c+1)**2
        d=d0*np.exp(-dc0/c-3850/(t+273.15)); dt,dc=d*3850/(t+273.15)**2,d*dc0/c**2
        ft=self.balance(t,k,air[0],H)/(cap*self.v)
        if not jac: return np.r_[ft,self.balance(c,d,air[1],HM)/self.v]
        zero=np.zeros(self.n)
        return bmat([[self.block(t,k,zero,1,H,cap*self.v),self.block(t,k,kc,0,0,cap*self.v)-diags(ft*cap_c/cap)],
                     [self.block(c,d,dt,0,0,self.v),self.block(c,d,dc,1,HM,self.v)]],format='csc')

    def system(self,t,state,air,jac=False,radius=None):
        if radius is not None: self.geometry(float(radius(t)))
        return self.coupled(state,air(t),jac)

