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
        band=np.zeros(m.shape,bool); w=m.shape[1]; e=int(w*0.20)
        band[:,:e]=True; band[:,w-e:]=True
        m[band & (hsv[:,:,1]<52) & (hsv[:,:,2]<120)]=0
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
# Aquí no hay ningún modelo de imagen (sin acceso de red a los pesos), así que
# la persona no puede ser una foto. Se resuelve como lo hacen las guías de
# talla: una silueta de maniquí, plana y monocroma, con el recorte de la pieza
# real encima. Se dibuja en SVG y lo rasteriza el navegador.
W,H=1000,1200
FIT={'batman':(462,356),'venom':(404,374),'ranger':(454,360)}   # alto, centro Y

SVG = """<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<defs>
  <linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#F7F5F1"/><stop offset="1" stop-color="#E7E3DC"/>
  </linearGradient>
  <linearGradient id="skin" x1="0.15" y1="0" x2="0.9" y2="1">
    <stop offset="0" stop-color="#DAD3C9"/><stop offset="0.55" stop-color="#C8BFB3"/>
    <stop offset="1" stop-color="#A89E92"/>
  </linearGradient>
  <linearGradient id="shirt" x1="0.15" y1="0" x2="0.9" y2="1">
    <stop offset="0" stop-color="#3B424C"/><stop offset="0.55" stop-color="#2C323A"/>
    <stop offset="1" stop-color="#1D2228"/>
  </linearGradient>
  <radialGradient id="halo" cx="0.5" cy="0.30" r="0.55">
    <stop offset="0" stop-color="#FFFFFF" stop-opacity="0.85"/>
    <stop offset="1" stop-color="#FFFFFF" stop-opacity="0"/>
  </radialGradient>
  <filter id="soft" x="-30%" y="-30%" width="160%" height="160%">
    <feGaussianBlur stdDeviation="26"/>
  </filter>
  <filter id="drop" x="-30%" y="-30%" width="160%" height="160%">
    <feDropShadow dx="0" dy="16" stdDeviation="22" flood-color="#2A2620" flood-opacity="0.26"/>
  </filter>
</defs>
<rect width="{W}" height="{H}" fill="url(#bg)"/>
<rect width="{W}" height="{H}" fill="url(#halo)"/>

<!-- el maniquí: hombros, cuello, cabeza y orejas, todo del mismo tono -->
<g fill="url(#skin)">
  <path d="M424 470 L424 660 Q 500 706 576 660 L576 470 Z"/>
  <ellipse cx="500" cy="360" rx="148" ry="190"/>
  <ellipse cx="356" cy="378" rx="21" ry="33"/>
  <ellipse cx="644" cy="378" rx="21" ry="33"/>
</g>
<path d="M40 {H} C 44 1004, 106 848, 232 766 C 312 714, 384 692, 500 688
         C 616 692, 688 714, 768 766 C 894 848, 956 1004, 960 {H} Z" fill="url(#shirt)"/>
<!-- la sombra del cuello sobre los hombros -->
<ellipse cx="500" cy="700" rx="104" ry="30" fill="#11151A" opacity="0.45" filter="url(#soft)"/>

<image href="{SRC}" x="{MX}" y="{MY}" width="{MW}" height="{MH}" filter="url(#drop)"/>

<line x1="60" y1="{LY}" x2="{LX}" y2="{LY}" stroke="#0E8C86" stroke-width="2" opacity="0.5"/>
<text x="60" y="{TY}" font-family="ui-monospace,Menlo,Consolas,monospace" font-size="19"
      letter-spacing="2" fill="#6E6559">MONTAJE A ESCALA · CABEZA ADULTA DE 22 CM</text>
</svg>"""

def svg_for(key):
    import base64 as b64
    r=cv2.imread(SP+'cut-'+key+'.png',cv2.IMREAD_UNCHANGED)
    ok,buf=cv2.imencode('.png',r)
    src='data:image/png;base64,'+b64.b64encode(buf.tobytes()).decode()
    mh,cy=FIT[key]
    mw=int(r.shape[1]*mh/r.shape[0])
    return SVG.format(W=W,H=H,SRC=src,MW=mw,MH=mh,MX=W//2-mw//2,MY=cy-mh//2,
                      LY=H-96,LX=W-60,TY=H-62)

if __name__=='__main__':
    import os
    for k in FIT:
        cv2.imwrite(SP+'cut-'+k+'.png',cutout(k))
        open(SP+'worn-'+k+'.svg','w').write(svg_for(k))
    print('svg ok')
