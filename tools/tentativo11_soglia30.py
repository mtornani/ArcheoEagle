"""Raffinamento della soglia a 1" (GLO-30) nella finestra 9-11 N, 14-16 E.
Uso: python tentativo11_soglia30.py <t11_grids.npz> <cartella_tile_GLO30> <out.json>
Uscite = celle di bordo che nel run a 12" drenano sotto lo sfioro (lato Benue). Il resto del bordo e' muro."""
import json, sys
import numpy as np, rasterio

GRIDS, TILES30, OUT = sys.argv[1], sys.argv[2], sys.argv[3]   # t11_grids.npz, cartella tile GLO-30, json di uscita
from skimage.morphology import reconstruction
g=np.load(GRIDS); filled=g['filled']; mask=g['mask']; spill=float(filled[mask].max())
H=filled.shape[0]; per=H//15
def tile(lat,lon):
    return rasterio.open(f'{TILES30}/Copernicus_DSM_COG_10_N{lat:02d}_00_E{lon:03d}_00_DEM.tif').read(1).astype(np.float32)
dem=np.block([[tile(10,14),tile(10,15)],[tile(9,14),tile(9,15)]])
print(dem.shape)
# griglia coarse corrispondente (lat 9..11, lon 14..16)
r0=(21-11)*per; c0=(14-8)*per
cf=filled[r0:r0+2*per, c0:c0+2*per]; cm=mask[r0:r0+2*per, c0:c0+2*per]
k=dem.shape[0]//cf.shape[0]
up=lambda x: np.kron(x, np.ones((k,k),x.dtype))
out_c=up((cf<spill-0.5).astype(np.uint8)).astype(bool); lake=up(cm.astype(np.uint8)).astype(bool)
seed=np.full_like(dem, 9999.)
b=np.zeros_like(out_c); b[0,:]=b[-1,:]=b[:,0]=b[:,-1]=True
ex=b&out_c; seed[ex]=dem[ex]
print("celle d'uscita sul bordo:",ex.sum(), "celle lago nella finestra:",lake.sum())
res={}
for name,fp in (("conn4",np.array([[0,1,0],[1,1,1],[0,1,0]],bool)),("conn8",np.ones((3,3),bool))):
    f=reconstruction(seed, dem, method='erosion', footprint=fp)
    v=f[lake]; res[name]={"sill_m":round(float(np.median(v)),2),"p05":round(float(np.percentile(v,5)),2),"p95":round(float(np.percentile(v,95)),2)}
    print(name,res[name])
    if name=="conn4":
        # dove sta la soglia: celle con dem==f==sill adiacenti a zona che drena sotto
        s=np.median(v); cand=(np.abs(dem-s)<1e-3)&(np.abs(f-s)<1e-3)
        from scipy import ndimage
        cand&=ndimage.binary_dilation(f<s-1e-3)
        rr,cc=np.nonzero(cand); print("celle soglia:",len(rr))
        if len(rr): res["sill_latlon"]=[round(11-(rr.mean()+.5)/3600,4), round(14+(cc.mean()+.5)/3600,4)]; print(res["sill_latlon"])
json.dump(res,open(OUT,'w'))
