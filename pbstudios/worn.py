"""Monta cada máscara puesta sobre una figura dibujada.

No hay ningún modelo de imagen en este entorno (sin acceso de red a los
pesos), así que la persona no es una foto: es una ilustración plana dibujada
por código —busto de estudio— sobre la que se compone el recorte de la
máscara real. La pieza es la de verdad; la figura es un maniquí dibujado.
"""
import cv2, numpy as np, base64, json
import extract as E                      # reutiliza el recorte ya afinado

U=E.U; SP=E.SP
# foto frontal de cada máscara y hasta dónde se conserva (el resto es mano)
# foto, radio de apertura, recorte por abajo, limpiar grises del borde
PICK={'batman':('ee82fcc5',  0,0.97,False),
      'venom' :('35b513c2',120,0.80,False),
      'ranger':('726be8c9',185,0.78,True)}

def small_holes(m,frac=0.02):
    """rellena los huecos internos pequeños y deja pasar los grandes: entre las
    aletas del casco y la barbilla se ve el fondo, y ahí no hay pieza."""
    inv=cv2.bitwise_not(m)
    n,lab,stats,_=cv2.connectedComponentsWithStats((inv>0).astype(np.uint8),8)
    out=m.copy(); area=(m>0).sum()
    for i in range(1,n):
        x,y,w,h,a=stats[i]
        if x==0 or y==0 or x+w==m.shape[1] or y+h==m.shape[0]: continue   # es el exterior
        if a<area*frac: out[lab==i]=255
    return out

def cutout(key):
    f,radius,keep,edges=PICK[key]
    img=cv2.imread(U+f+'-image.png'); img=E.photo_band(img)
    m,_=E.coarse_mask(img)
    if radius: m=E.drop_limbs(m,radius)
    m=E.refine(img,m)
    m=small_holes(m)                       # solo los agujeros pequeños
    ys,xs=np.where(m>0)
    y0,y1,x0,x1=ys.min(),ys.max(),xs.min(),xs.max()
    cut=y0+int((y1-y0)*keep)               # fuera lo que cuelga por debajo
    m[cut:,:]=0
    n,lab,stats,_=cv2.connectedComponentsWithStats((m>0).astype(np.uint8),8)
    if n>1:                                 # y fuera los restos sueltos
        big=1+np.argmax(stats[1:,cv2.CC_STAT_AREA])
        m=((lab==big)*255).astype(np.uint8)
    ys,xs=np.where(m>0)
    y0,y1,x0,x1=ys.min(),ys.max(),xs.min(),xs.max()
    img=img[y0:y1+1,x0:x1+1]; m=m[y0:y1+1,x0:x1+1]
    if edges:
        # en los bordes laterales, lo gris oscuro es fondo o mano en sombra
        hsv=cv2.cvtColor(img,cv2.COLOR_BGR2HSV)
        band=np.zeros(m.shape,bool); w=m.shape[1]; e=int(w*0.27)
        band[:,:e]=True; band[:,w-e:]=True
        m[band & (hsv[:,:,1]<46)]=0      # ni fondo claro ni mano en sombra
    n,lab,stats,_=cv2.connectedComponentsWithStats((m>0).astype(np.uint8),8)
    if n>1:
        big=1+np.argmax(stats[1:,cv2.CC_STAT_AREA])
        m=((lab==big)*255).astype(np.uint8)
    m=cv2.morphologyEx(m,cv2.MORPH_CLOSE,np.ones((9,9),np.uint8))
    ys,xs=np.where(m>0)
    y0,y1,x0,x1=ys.min(),ys.max(),xs.min(),xs.max()
    img=img[y0:y1+1,x0:x1+1]; m=m[y0:y1+1,x0:x1+1]
    a=cv2.GaussianBlur(m,(0,0),1.2)
    return np.dstack([img,a])              # BGRA


# ── El montaje "puesta" ────────────────────────────────────────────────────
# Fondo oscuro de estudio y, de la persona, solo el cuello y el arranque de
# los hombros entrando por abajo: el resto lo tapa la propia máscara. Es como
# fotografían los estudios de cosplay y perdona que la figura sea dibujada,
# porque aquí no hay ningún modelo de imagen con el que generar una persona.
W=H=1000
FIT={'batman':(812,408),'venom':(742,418),'ranger':(796,412)}   # alto, centro Y

SVG = """<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<defs>
  <radialGradient id="bg" cx="0.5" cy="0.34" r="0.78">
    <stop offset="0" stop-color="#20282C"/><stop offset="0.55" stop-color="#11171A"/>
    <stop offset="1" stop-color="#07090B"/>
  </radialGradient>
  <linearGradient id="skin" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="#241F1B"/><stop offset="0.18" stop-color="#4F473F"/>
    <stop offset="0.44" stop-color="#7E746A"/><stop offset="0.82" stop-color="#4A423B"/>
    <stop offset="1" stop-color="#1F1B17"/>
  </linearGradient>
  <linearGradient id="shade" x1="0.5" y1="0" x2="0.5" y2="1">
    <stop offset="0" stop-color="#000" stop-opacity="0.72"/>
    <stop offset="0.45" stop-color="#000" stop-opacity="0.10"/>
    <stop offset="1" stop-color="#000" stop-opacity="0.45"/>
  </linearGradient>
  <radialGradient id="shoulder" cx="0.5" cy="0.0" r="0.95">
    <stop offset="0" stop-color="#4B443C"/><stop offset="0.45" stop-color="#2A2622"/>
    <stop offset="1" stop-color="#121010"/>
  </radialGradient>
  <radialGradient id="vig" cx="0.5" cy="0.42" r="0.72">
    <stop offset="0.55" stop-color="#000" stop-opacity="0"/>
    <stop offset="1" stop-color="#000" stop-opacity="0.78"/>
  </radialGradient>
  <filter id="soft" x="-40%" y="-40%" width="180%" height="180%">
    <feGaussianBlur stdDeviation="30"/>
  </filter>
  <filter id="drop" x="-30%" y="-30%" width="160%" height="170%">
    <feDropShadow dx="0" dy="26" stdDeviation="26" flood-color="#000" flood-opacity="0.55"/>
  </filter>
</defs>
<rect width="{W}" height="{H}" fill="url(#bg)"/>

<!-- de la persona solo asoma el cuello y el arranque de los hombros -->
<g>
  <path id="neck" d="M348 520 C 340 690, 352 800, 386 870 L 614 870 C 648 800, 660 690, 652 520 Z"/>
  <use href="#neck" fill="url(#skin)"/>
  <use href="#neck" fill="url(#shade)"/>
</g>
<path d="M-40 {H} C 40 920, 236 856, 500 850 C 764 856, 960 920, 1040 {H} Z" fill="url(#shoulder)"/>
<ellipse cx="500" cy="860" rx="210" ry="44" fill="#000" opacity="0.55" filter="url(#soft)"/>

<image href="{SRC}" x="{MX}" y="{MY}" width="{MW}" height="{MH}" filter="url(#drop)"/>

<!-- viñeta, para que la pieza sea lo único que brilla -->
<rect width="{W}" height="{H}" fill="url(#vig)"/>
</svg>"""

def svg_for(key):
    import base64 as b64
    r=cv2.imread(SP+'cut-'+key+'.png',cv2.IMREAD_UNCHANGED)
    # el borde se come 2 px: en fondo oscuro, el halo claro de la foto canta
    a=cv2.erode(r[:,:,3],np.ones((3,3),np.uint8),iterations=2)
    r[:,:,3]=cv2.GaussianBlur(a,(0,0),1.0)
    # la pieza venía de fondo claro: se apaga y se le mete sombra por abajo
    h=r.shape[0]
    ramp=np.clip(np.linspace(1.0,1.0,h),0,1)
    ramp[int(h*0.62):]=np.linspace(1.0,0.46,h-int(h*0.62))
    rgb=r[:,:,:3].astype(np.float32)*0.93*ramp[:,None,None]
    r[:,:,:3]=np.clip(rgb,0,255).astype(np.uint8)
    ok,buf=cv2.imencode('.png',r)
    src='data:image/png;base64,'+b64.b64encode(buf.tobytes()).decode()
    mh,cy=FIT[key]
    mw=int(r.shape[1]*mh/r.shape[0])
    return SVG.format(W=W,H=H,SRC=src,MW=mw,MH=mh,MX=W//2-mw//2,MY=cy-mh//2)

if __name__=='__main__':
    for k in FIT:
        cv2.imwrite(SP+'cut-'+k+'.png',cutout(k))
        open(SP+'worn-'+k+'.svg','w').write(svg_for(k))
    print('svg ok')
