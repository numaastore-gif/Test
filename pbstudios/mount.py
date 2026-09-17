"""Monta cada pieza sobre el mismo maniquí, con camiseta de marca.

Regla del catálogo: toda máscara se enseña igual. Fondo de estudio oscuro, la
pieza arriba, y debajo el torso con la camiseta en el verde de PB Studios y el
logo en el pecho. Del render original se conserva la cabeza y el cuello —que
traen la luz buena— y se corta justo por encima de la ropa, que la pone esto.

Genera los SVG; los rasteriza el navegador (rast.js) y `pack()` los deja en
base64 listos para incrustar en index.html.
"""
import cv2, numpy as np, base64, json
import do3d

U=do3d.U; SP=do3d.SP
W=H=900
TEAL='#0E8C86'

# clave -> (fichero, mitad de la lámina, corte por el cuello, alto de la
#           cabeza en el lienzo). La altura sale sola: el corte del cuello
#           tiene que caer dentro del escote.
NECK=670
SRC={
 'batman2-front':('850e419e','L',0.900,0.62),
 'batman2-close':('850e419e','L',0.900,0.72),
 'batman2-back' :('850e419e','R',0.880,0.62),
 'venom-front'  :('10835edc','' ,0.925,0.64),
 'venom-3q'     :('d33d640f','' ,0.925,0.64),
 'venom-side'   :('79a76934','' ,0.925,0.64),
 # estas vienen de foto recortada, no de render: no traen cuello
 'batman-worn'  :('cut:batman','',1.0,0.66),
 'ranger-worn'  :('cut:ranger','',1.0,0.66),
}

def sheet(f,half):
    img=do3d.unmark(cv2.imread(U+f+'-image.jpg'))
    if not half: return img
    g=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    col=(g>18).sum(0); w=img.shape[1]
    cut=int(w*0.35)+int(np.argmin(col[int(w*0.35):int(w*0.65)]))
    return img[:,:cut] if half=='L' else img[:,cut:]

def subject(img):
    """la figura contra el fondo, que en estos renders es negro puro"""
    g=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    m=(g>16).astype(np.uint8)*255
    m=cv2.morphologyEx(m,cv2.MORPH_CLOSE,np.ones((13,13),np.uint8))
    n,lab,stats,_=cv2.connectedComponentsWithStats((m>0).astype(np.uint8),8)
    if n>1:
        big=1+np.argmax(stats[1:,cv2.CC_STAT_AREA])
        m=((lab==big)*255).astype(np.uint8)
    inv=cv2.bitwise_not(m)                       # los negros de dentro son pieza
    n,lab,stats,_=cv2.connectedComponentsWithStats((inv>0).astype(np.uint8),8)
    for i in range(1,n):
        x,y,w,h,a=stats[i]
        if x>0 and y>0 and x+w<m.shape[1] and y+h<m.shape[0]: m[lab==i]=255
    return cv2.GaussianBlur(m,(0,0),2.0).astype(np.float32)/255.0

def head(key):
    """cabeza y cuello, con alfa, cortados justo antes de la ropa"""
    f,half,cut,_=SRC[key]
    if f.startswith('cut:'):
        r=cv2.imread(SP+'cut-'+f[4:]+'.png',cv2.IMREAD_UNCHANGED)
        a=cv2.erode(r[:,:,3],np.ones((3,3),np.uint8),iterations=2)
        r[:,:,3]=cv2.GaussianBlur(a,(0,0),1.0)
        h=r.shape[0]                       # la base entra en sombra
        ramp=np.ones(h,np.float32); ramp[int(h*0.70):]=np.linspace(1,0.45,h-int(h*0.70))
        r[:,:,:3]=np.clip(r[:,:,:3].astype(np.float32)*0.95*ramp[:,None,None],0,255).astype(np.uint8)
        return r
    img=sheet(f,half)
    m=(subject(img)*255).astype(np.uint8)
    # fuera la ropa del render: la camiseta la pone el montaje. Es lo blanco
    # sin saturar del tercio de abajo, no el cuello ni la pieza.
    hsv=cv2.cvtColor(img,cv2.COLOR_BGR2HSV)
    low=np.zeros(m.shape,bool); low[int(m.shape[0]*0.82):]=True
    m[low & (hsv[:,:,1]<28) & (hsv[:,:,2]>205)]=0
    n,lab,stats,_=cv2.connectedComponentsWithStats((m>0).astype(np.uint8),8)
    if n>1:
        big=1+np.argmax(stats[1:,cv2.CC_STAT_AREA])
        m=((lab==big)*255).astype(np.uint8)
    y=int(img.shape[0]*cut)
    m[y:,:]=0
    fade=np.linspace(1,0,max(1,int(img.shape[0]*0.05)))    # que el corte no se vea
    for i,k in enumerate(fade):
        yy=y-len(fade)+i
        if 0<=yy<m.shape[0]: m[yy]=(m[yy]*k).astype(np.uint8)
    ys,xs=np.where(m>4)
    y0,y1,x0,x1=ys.min(),ys.max(),xs.min(),xs.max()
    return np.dstack([img,m])[y0:y1+1,x0:x1+1]

LOGO='''<g transform="translate({lx},{ly}) scale({ls})" opacity="1">
  <g fill="none" stroke="#EAF6F3" stroke-width="7" stroke-linecap="round" opacity=".72">
    <path d="M96 268 L34 292"/><path d="M104 280 L58 300"/>
    <path d="M224 268 L286 292"/><path d="M216 280 L262 300"/>
  </g>
  <path d="M70 110 L190 80 L250 110 L130 140 Z" fill="#EAF6F3" opacity=".42"/>
  <path d="M190 80 L250 110 L250 260 L190 230 Z" fill="#EAF6F3" opacity=".26"/>
  <path d="M70 110 L190 80 L190 230 L70 260 Z" fill="#EAF6F3" opacity=".34"/>
  <path d="M96 244 L166 227 L166 235 L96 252 Z" fill="#EAF6F3" opacity=".75"/>
  <g fill="#EAF6F3" opacity=".8">
    <path d="M150 120 L170 115 L170 141 L150 146 Z"/>
    <path d="M157 146 L163 144 L160 156 Z"/>
  </g>
  <g stroke="#EAF6F3" stroke-width="5" stroke-linecap="round" opacity=".48">
    <path d="M210 118 L210 228"/><path d="M224 125 L224 235"/><path d="M238 132 L238 242"/>
  </g>
  <g fill="none" stroke="#EAF6F3" stroke-width="11" stroke-linejoin="round">
    <path d="M70 110 L190 80 L250 110 L250 260 L190 230 L70 260 Z"/>
    <path d="M190 80 L190 230" stroke-width="8"/>
    <path d="M70 110 L130 140 L250 110" stroke-width="8"/>
  </g>
</g>
'''

SVG='''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<defs>
  <radialGradient id="bg" cx="0.5" cy="0.40" r="0.80">
    <stop offset="0" stop-color="#0C0E0F"/><stop offset="0.6" stop-color="#040506"/>
    <stop offset="1" stop-color="#000000"/>
  </radialGradient>
  <linearGradient id="tee" x1="0.08" y1="0" x2="0.94" y2="1">
    <stop offset="0" stop-color="#0B6D68"/><stop offset="0.36" stop-color="#12A39A"/>
    <stop offset="0.72" stop-color="#0E8C86"/><stop offset="1" stop-color="#064B48"/>
  </linearGradient>
  <linearGradient id="teeShade" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#000" stop-opacity="0.55"/>
    <stop offset="0.34" stop-color="#000" stop-opacity="0.06"/>
    <stop offset="1" stop-color="#000" stop-opacity="0.32"/>
  </linearGradient>
  <filter id="soft" x="-40%" y="-40%" width="180%" height="180%">
    <feGaussianBlur stdDeviation="22"/>
  </filter>
  <filter id="drop" x="-30%" y="-40%" width="160%" height="180%">
    <feDropShadow dx="0" dy="18" stdDeviation="18" flood-color="#000" flood-opacity="0.72"/>
  </filter>
</defs>
<rect width="{W}" height="{H}" fill="url(#bg)"/>

<!-- el torso: hombros, mangas y cuello de la camiseta -->
<g>
  <path id="tor" d="M6 {H} L 96 800 C 160 726, 240 690, 336 678
        L 564 678 C 660 690, 740 726, 804 800 L 894 {H} Z"/>
  <use href="#tor" fill="url(#tee)"/>
  <use href="#tor" fill="url(#teeShade)"/>
  <!-- costuras de manga -->
  <path d="M206 724 C 244 772, 258 834, 254 {H}" fill="none" stroke="#05403D"
        stroke-width="4" opacity="0.45"/>
  <path d="M694 724 C 656 772, 642 834, 646 {H}" fill="none" stroke="#05403D"
        stroke-width="4" opacity="0.45"/>
</g>
<ellipse cx="450" cy="694" rx="140" ry="30" fill="#000" opacity="0.5" filter="url(#soft)"/>

<image href="{SRC}" x="{MX}" y="{MY}" width="{MW}" height="{MH}" filter="url(#drop)"/>

<!-- el ribete del escote va encima de la cabeza: tapa el corte del cuello -->
<path d="M348 660 C 366 706, 404 728, 450 728 C 496 728, 534 706, 552 660
         C 516 650, 384 650, 348 660 Z" fill="#0A7B75"/>
<path d="M348 660 C 366 706, 404 728, 450 728 C 496 728, 534 706, 552 660"
      fill="none" stroke="#2AD3C5" stroke-width="5" opacity="0.55"/>
<path d="M342 664 C 362 718, 402 744, 450 744 C 498 744, 538 718, 558 664"
      fill="none" stroke="#04413E" stroke-width="9" opacity="0.55"/>
<ellipse cx="450" cy="700" rx="118" ry="30" fill="#000" opacity="0.30" filter="url(#soft)"/>
{LOGO}
</svg>'''

def svg_for(key):
    r=head(key)
    ok,buf=cv2.imencode('.png',r)
    src='data:image/png;base64,'+base64.b64encode(buf.tobytes()).decode()
    k=SRC[key][3]
    mh=int(H*k); mw=int(r.shape[1]*mh/r.shape[0])
    logo=LOGO.format(lx=450-0.5*300*0.44, ly=742, ls=0.44)
    return SVG.format(W=W,H=H,SRC=src,MW=mw,MH=mh,
                      MX=W//2-mw//2,MY=NECK-mh,LOGO=logo)

def pack(keys=None):
    out={}
    for k in (keys or SRC):
        img=cv2.imread(SP+'mnt-'+k+'.png')
        if img is None: continue
        ok,buf=cv2.imencode('.jpg',img,[cv2.IMWRITE_JPEG_QUALITY,90])
        out[k]='data:image/jpeg;base64,'+base64.b64encode(buf.tobytes()).decode()
        print(k, f'{len(buf)/1024:.0f} KB')
    open(SP+'mount.json','w').write(json.dumps(out))
    return out

if __name__=='__main__':
    for k in SRC:
        open(SP+'mnt-'+k+'.svg','w').write(svg_for(k))
        print('svg',k)
