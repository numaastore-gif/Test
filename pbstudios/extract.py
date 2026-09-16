"""Extrae la pieza del fondo de cada foto y la monta sobre fondo de estudio.

Sin modelos de IA (no hay acceso de red a los pesos), así que:
  1. se estima el fondo por las esquinas y se hace una máscara gruesa,
  2. una apertura por reconstrucción se come el brazo y la mano, que son
     más estrechos que la pieza, y deja solo el casco,
  3. GrabCut afina el borde,
  4. se compone sobre fondo claro con una sombra de contacto.
"""
import cv2, numpy as np, base64, io, json, os
from PIL import Image

U='/root/.claude/uploads/6020d028-8fb4-5cc4-ad09-02e6a808b983/'
SP='/tmp/claude-0/-home-user-Test/6020d028-8fb4-5cc4-ad09-02e6a808b983/scratchpad/'
OUT=1000
BG=(243,241,236)            # el --paper del sitio

# Solo las que el recorte deja limpias. Descartadas por arrastrar fondo:
# venom 6dcdc262, ranger ab5f4c77 y febc04e7.
SETS={
 'batman':['ee82fcc5','553f9807','89026594'],
 'venom' :['35b513c2','7194c110','423b76bd','f52b6341'],
 'ranger':['726be8c9','d16f09c8','d76d8bf5'],
}

def photo_band(img):
    """recorta la interfaz del móvil"""
    H,W=img.shape[:2]; chrome=img[300,5].astype(int)
    def flat(y):
        row=img[y,::60].astype(int)
        return np.all(np.abs(row-chrome).sum(1)<26)
    ys=[y for y in range(0,H,4) if not flat(y)]
    best=(0,0); run=None
    for y in ys:
        if run is None or y-run[1]>12: run=[y,y]
        else: run[1]=y
        if run[1]-run[0]>best[1]-best[0]: best=(run[0],run[1])
    return img[best[0]+6:best[1]-6]

def fill_holes(m):
    h,w=m.shape
    ff=m.copy()
    mask=np.zeros((h+2,w+2),np.uint8)
    cv2.floodFill(ff,mask,(0,0),255)          # inunda el exterior
    return cv2.bitwise_or(m,cv2.bitwise_not(ff))

def coarse_mask(img):
    """lo que se aleja del color del fondo, con Otsu en vez de un percentil"""
    H,W=img.shape[:2]; s=26
    corners=np.array([img[s,s],img[s,W-s],img[H-s,s],img[H-s,W-s],img[s,W//2]],dtype=float)
    bg=corners.mean(0)
    lab=cv2.cvtColor(img,cv2.COLOR_BGR2LAB).astype(float)
    bglab=cv2.cvtColor(np.uint8([[bg.astype(np.uint8)]]),cv2.COLOR_BGR2LAB)[0,0].astype(float)
    d=np.linalg.norm(lab-bglab,axis=2)
    d=np.clip(d/d.max()*255,0,255).astype(np.uint8)
    d=cv2.GaussianBlur(d,(0,0),3)
    _,m=cv2.threshold(d,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)

    # si lo marcado toca casi todo el marco, es el fondo: se invierte
    border=np.concatenate([m[0],m[-1],m[:,0],m[:,-1]])
    if (border>0).mean()>0.55: m=cv2.bitwise_not(m)

    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((7,7),np.uint8))
    m=cv2.morphologyEx(m,cv2.MORPH_CLOSE,np.ones((15,15),np.uint8))
    m=fill_holes(m)
    return m, bg.mean()

def drop_limbs(m,radius):
    """apertura por reconstrucción: el brazo es más fino que la pieza y cae"""
    k=cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(radius*2+1,)*2)
    seed=cv2.erode(m,k)
    n,lab,stats,_=cv2.connectedComponentsWithStats((seed>0).astype(np.uint8),8)
    if n<2: return m
    big=1+np.argmax(stats[1:,cv2.CC_STAT_AREA])
    seed=((lab==big)*255).astype(np.uint8)
    prev=None; cur=seed
    k3=np.ones((3,3),np.uint8)
    for _ in range(400):                       # reconstrucción geodésica
        cur=cv2.bitwise_and(cv2.dilate(cur,k3),m)
        if prev is not None and np.array_equal(cur,prev): break
        prev=cur.copy()
    return cur

def refine(img,m):
    gm=np.where(m>0,cv2.GC_PR_FGD,cv2.GC_PR_BGD).astype(np.uint8)
    k=cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(41,41))
    gm[cv2.erode(m,k)>0]=cv2.GC_FGD
    gm[cv2.dilate(m,k)==0]=cv2.GC_BGD
    bgd=np.zeros((1,65),np.float64); fgd=np.zeros((1,65),np.float64)
    try:
        cv2.grabCut(img,gm,None,bgd,fgd,3,cv2.GC_INIT_WITH_MASK)
    except Exception:
        return m
    out=np.where((gm==cv2.GC_FGD)|(gm==cv2.GC_PR_FGD),255,0).astype(np.uint8)
    n,lab,stats,_=cv2.connectedComponentsWithStats((out>0).astype(np.uint8),8)
    if n>1:
        big=1+np.argmax(stats[1:,cv2.CC_STAT_AREA])
        out=((lab==big)*255).astype(np.uint8)
    out=cv2.morphologyEx(out,cv2.MORPH_CLOSE,np.ones((15,15),np.uint8))
    return out

def compose(img,alpha):
    """monta la pieza sobre fondo de estudio, con sombra de contacto"""
    ys,xs=np.where(alpha>40)
    if len(xs)==0: return None
    x0,x1,y0,y1=xs.min(),xs.max(),ys.min(),ys.max()
    side=int(max(x1-x0,y1-y0)*1.30)
    cx,cy=(x0+x1)//2,(y0+y1)//2
    pad=side
    img=cv2.copyMakeBorder(img,pad,pad,pad,pad,cv2.BORDER_REPLICATE)
    alpha=cv2.copyMakeBorder(alpha,pad,pad,pad,pad,cv2.BORDER_CONSTANT,value=0)
    cx+=pad; cy+=pad
    l,t=cx-side//2, cy-side//2
    img=img[t:t+side,l:l+side]; alpha=alpha[t:t+side,l:l+side]
    img=cv2.resize(img,(OUT,OUT),interpolation=cv2.INTER_AREA)
    alpha=cv2.resize(alpha,(OUT,OUT),interpolation=cv2.INTER_AREA)
    alpha=cv2.GaussianBlur(alpha,(0,0),1.6).astype(float)/255.0

    canvas=np.zeros((OUT,OUT,3),np.float32); canvas[:]= BG[::-1]
    # sombra: la silueta desplazada, desenfocada y aplastada
    sh_h=int(OUT*0.16)
    sh=cv2.resize((alpha*255).astype(np.uint8),(OUT,sh_h))
    shadow=np.zeros((OUT,OUT),np.uint8)
    y=int(OUT*0.845); h=min(sh_h,OUT-y)
    shadow[y:y+h,:]=sh[:h]
    shadow=cv2.GaussianBlur(shadow,(0,0),26).astype(float)/255.0*0.30
    canvas*= (1-shadow[...,None])
    a=alpha[...,None]
    out=(img.astype(np.float32)*a + canvas*(1-a)).astype(np.uint8)
    return out

def run(path,limb_radius):
    img=cv2.imread(path); img=photo_band(img)
    m,bgl=coarse_mask(img)
    if limb_radius: m=drop_limbs(m,limb_radius)
    else:
        n,lab,stats,_=cv2.connectedComponentsWithStats((m>0).astype(np.uint8),8)
        if n>1:
            big=1+np.argmax(stats[1:,cv2.CC_STAT_AREA])
            m=((lab==big)*255).astype(np.uint8)
    m=fill_holes(refine(img,m))
    return compose(img,m)

photos={}; total=0
cell=OUT//4
sheet=np.full((cell*3,cell*5,3),255,np.uint8)
for r,(key,files) in enumerate(SETS.items()):
    photos[key]=[]
    radius=0 if key=='batman' else 120       # el render no tiene manos
    for c,f in enumerate(files):
        out=run(U+f+'-image.png',radius)
        if out is None: print('FALLO',f); continue
        sheet[r*cell:(r+1)*cell, c*cell:(c+1)*cell]=cv2.resize(out,(cell,cell))
        ok,buf=cv2.imencode('.jpg',out,[cv2.IMWRITE_JPEG_QUALITY,82])
        b=buf.tobytes(); total+=len(b)
        photos[key].append('data:image/jpeg;base64,'+base64.b64encode(b).decode())
        print(f'{key:7} {f} {len(b)/1024:5.0f} KB')
cv2.imwrite(SP+'extraidas.png',sheet)
open(SP+'photos.json','w').write(json.dumps(photos))
print(f'TOTAL {total/1024:.0f} KB · base64 ≈ {total*1.34/1024:.0f} KB')
