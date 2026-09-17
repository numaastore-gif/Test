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
        m[band & (hsv[:,:,1]<62)]=0      # ni fondo claro ni mano en sombra
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


# ── El maniquí común ───────────────────────────────────────────────────────
# Toda máscara va sobre el MISMO maniquí, para que el catálogo se lea de una
# pieza. La referencia es el render del pack de Do3D del Venom: fondo negro,
# la máscara llenando el encuadre y, abajo, solo el cuello y el arranque de
# los hombros. El tono de la piel está tomado del propio render.
W=H=800
FIT={'batman':(0.90,0.455),'ranger':(0.88,0.462)}   # alto relativo, centro Y

SVG = """<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<defs>
  <radialGradient id="bg" cx="0.5" cy="0.42" r="0.78">
    <stop offset="0" stop-color="#0B0C0D"/><stop offset="0.6" stop-color="#040405"/>
    <stop offset="1" stop-color="#000000"/>
  </radialGradient>
  <linearGradient id="skin" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="#3B302C"/><stop offset="0.22" stop-color="#6E5C54"/>
    <stop offset="0.5" stop-color="#A18579"/><stop offset="0.78" stop-color="#6A584F"/>
    <stop offset="1" stop-color="#342A26"/>
  </linearGradient>
  <linearGradient id="fall" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#000" stop-opacity="0.62"/>
    <stop offset="0.5" stop-color="#000" stop-opacity="0.06"/>
    <stop offset="1" stop-color="#000" stop-opacity="0.00"/>
  </linearGradient>
  <filter id="soft" x="-40%" y="-40%" width="180%" height="180%">
    <feGaussianBlur stdDeviation="26"/>
  </filter>
  <filter id="drop" x="-30%" y="-30%" width="160%" height="170%">
    <feDropShadow dx="0" dy="20" stdDeviation="20" flood-color="#000" flood-opacity="0.70"/>
  </filter>
</defs>
<rect width="{W}" height="{H}" fill="url(#bg)"/>

<!-- el maniquí: cuello y arranque de hombros, como en el render de referencia -->
<g>
  <path id="neck" d="M286 462 C 278 616, 288 706, 316 {H} L 484 {H} C 512 706, 522 616, 514 462 Z"/>
  <use href="#neck" fill="url(#skin)"/>
  <use href="#neck" fill="url(#fall)"/>
  <path d="M-30 {H} C 40 790, 206 730, 400 724 C 594 730, 760 790, 830 {H} Z" fill="url(#skin)"/>
  <path d="M-30 {H} C 40 790, 206 730, 400 724 C 594 730, 760 790, 830 {H} Z" fill="url(#fall)"/>
</g>
<ellipse cx="400" cy="736" rx="186" ry="36" fill="#000" opacity="0.62" filter="url(#soft)"/>

<image href="{SRC}" x="{MX}" y="{MY}" width="{MW}" height="{MH}" filter="url(#drop)"/>
</svg>"""

def svg_for(key):
    import base64 as b64
    r=cv2.imread(SP+'cut-'+key+'.png',cv2.IMREAD_UNCHANGED)
    a=cv2.erode(r[:,:,3],np.ones((3,3),np.uint8),iterations=2)
    r[:,:,3]=cv2.GaussianBlur(a,(0,0),1.0)
    # la pieza venía de fondo claro: se apaga un punto y se le hunde la base
    h=r.shape[0]
    ramp=np.ones(h,np.float32); ramp[int(h*0.66):]=np.linspace(1.0,0.40,h-int(h*0.66))
    r[:,:,:3]=np.clip(r[:,:,:3].astype(np.float32)*0.95*ramp[:,None,None],0,255).astype(np.uint8)
    ok,buf=cv2.imencode('.png',r)
    src='data:image/png;base64,'+b64.b64encode(buf.tobytes()).decode()
    k,cy=FIT[key]
    mh=int(H*k); mw=int(r.shape[1]*mh/r.shape[0])
    return SVG.format(W=W,H=H,SRC=src,MW=mw,MH=mh,MX=W//2-mw//2,MY=int(H*cy)-mh//2)

if __name__=='__main__':
    import json
    for k in FIT:
        cv2.imwrite(SP+'cut-'+k+'.png',cutout(k))
        open(SP+'worn-'+k+'.svg','w').write(svg_for(k))
    print('svg ok · rasterizar con el navegador y luego pack()')

def pack():
    """los PNG ya rasterizados, listos para incrustar en la página"""
    import json, base64 as b64
    out={}
    for k in FIT:
        img=cv2.imread(SP+'worn-'+k+'.png')
        ok,buf=cv2.imencode('.jpg',img,[cv2.IMWRITE_JPEG_QUALITY,90])
        out[k]='data:image/jpeg;base64,'+b64.b64encode(buf.tobytes()).decode()
        print(k, f'{len(buf)/1024:.0f} KB')
    open(SP+'worn.json','w').write(json.dumps(out))
