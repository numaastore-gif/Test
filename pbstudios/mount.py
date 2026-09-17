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

# Cada vista: de qué fichero sale, qué mitad de la lámina, dónde cortar el
# cuello, qué alto ocupa la cabeza, si se espeja y desde dónde quitar la piel
# desnuda del render (los hombros al aire, que aquí van tapados por la
# camiseta). La altura sale sola de NECK.
NECK=670
def V(f,half='',cut=0.90,k=0.62,flip=False,skin=None,collar=True):
    # collar=False para las capuchas que bajan hasta el hombro: ahí el ribete
    # de la camiseta sobra, porque la propia pieza tapa el cuello
    return dict(f=f,half=half,cut=cut,k=k,flip=flip,skin=skin,collar=collar)

SRC={
 'batman2-front':V('850e419e','L',0.900,0.62),
 'batman2-close':V('850e419e','L',0.900,0.72),
 'batman2-back' :V('850e419e','R',0.880,0.62),
 'venom-front'  :V('10835edc','' ,0.925,0.64),
 'venom-3q'     :V('d33d640f','' ,0.925,0.64),
 'venom-side'   :V('79a76934','' ,0.925,0.64),
 # el casco rojo solo vino en dos vistas: la tercera es la primera espejada,
 # que en una pieza simétrica es el otro lado, no un invento
 'redbat-3q'    :V('f2545ca9','' ,0.920,0.66,skin=0.70,collar=False),
 'redbat-alt'   :V('f2545ca9','' ,0.920,0.66,flip=True,skin=0.70,collar=False),
 'redbat-back'  :V('4aeaa1d6','' ,0.940,0.66,skin=0.72,collar=False),
 # estas vienen de foto recortada, no de render: no traen cuello
 'batman-worn'  :V('cut:batman','',1.0,0.66),
 'ranger-worn'  :V('cut:ranger','',1.0,0.66),
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
    v=SRC[key]; f,half,cut=v['f'],v['half'],v['cut']
    if f.startswith('cut:'):
        r=cv2.imread(SP+'cut-'+f[4:]+'.png',cv2.IMREAD_UNCHANGED)
        a=cv2.erode(r[:,:,3],np.ones((3,3),np.uint8),iterations=2)
        r[:,:,3]=cv2.GaussianBlur(a,(0,0),1.0)
        h=r.shape[0]                       # la base entra en sombra
        ramp=np.ones(h,np.float32); ramp[int(h*0.70):]=np.linspace(1,0.45,h-int(h*0.70))
        r[:,:,:3]=np.clip(r[:,:,:3].astype(np.float32)*0.95*ramp[:,None,None],0,255).astype(np.uint8)
        return r[:,::-1] if v['flip'] else r
    img=sheet(f,half)
    m=(subject(img)*255).astype(np.uint8)
    # fuera la ropa del render: la camiseta la pone el montaje. Es lo blanco
    # sin saturar del tercio de abajo, no el cuello ni la pieza.
    hsv=cv2.cvtColor(img,cv2.COLOR_BGR2HSV)
    low=np.zeros(m.shape,bool); low[int(m.shape[0]*0.82):]=True
    m[low & (hsv[:,:,1]<28) & (hsv[:,:,2]>205)]=0
    if v['skin'] is not None:
        # y fuera los hombros al aire: debajo de esa altura ya no hay cara,
        # así que todo lo que sea piel es lo que va a tapar la camiseta
        y2=cv2.cvtColor(img,cv2.COLOR_BGR2YCrCb)
        cr,cb=y2[:,:,1].astype(int), y2[:,:,2].astype(int)
        sat=hsv[:,:,1].astype(int)
        bare=np.zeros(m.shape,bool); bare[int(m.shape[0]*v['skin']):]=True
        m[bare & (cr>131)&(cr<176)&(cb>74)&(cb<132)&(sat<126)]=0
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
    out=np.dstack([img,m])[y0:y1+1,x0:x1+1]
    return out[:,::-1] if v['flip'] else out

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

COLLAR='''<!-- el ribete del escote va encima de la cabeza: tapa el corte del cuello -->
<path d="M346 656 C 364 706, 404 730, 450 730 C 496 730, 536 706, 554 656
         C 516 645, 384 645, 346 656 Z" fill="#0C8A83"/>
<path d="M346 656 C 364 706, 404 730, 450 730 C 496 730, 536 706, 554 656"
      fill="none" stroke="#49E7D8" stroke-width="4" opacity="0.6"/>
<path d="M338 660 C 360 720, 402 748, 450 748 C 498 748, 540 720, 562 660"
      fill="none" stroke="#04413E" stroke-width="10" opacity="0.6"/>
<ellipse cx="450" cy="690" rx="104" ry="26" fill="#000" opacity="0.38" filter="url(#soft)"/>'''

SVG='''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<defs>
  <radialGradient id="bg" cx="0.5" cy="0.40" r="0.80">
    <stop offset="0" stop-color="#0C0E0F"/><stop offset="0.6" stop-color="#040506"/>
    <stop offset="1" stop-color="#000000"/>
  </radialGradient>
  <!-- la tela: base, y encima el volumen del cuerpo -->
  <linearGradient id="tee" x1="0.1" y1="0" x2="0.9" y2="1">
    <stop offset="0" stop-color="#0D8079"/><stop offset="0.45" stop-color="#11A79D"/>
    <stop offset="1" stop-color="#075E5A"/>
  </linearGradient>
  <radialGradient id="chest" cx="0.5" cy="0.30" r="0.52">
    <stop offset="0" stop-color="#3FE0D0" stop-opacity="0.34"/>
    <stop offset="0.55" stop-color="#3FE0D0" stop-opacity="0.08"/>
    <stop offset="1" stop-color="#3FE0D0" stop-opacity="0"/>
  </radialGradient>
  <linearGradient id="flanks" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="#000" stop-opacity="0.66"/>
    <stop offset="0.16" stop-color="#000" stop-opacity="0.24"/>
    <stop offset="0.40" stop-color="#000" stop-opacity="0"/>
    <stop offset="0.66" stop-color="#000" stop-opacity="0.06"/>
    <stop offset="0.86" stop-color="#000" stop-opacity="0.34"/>
    <stop offset="1" stop-color="#000" stop-opacity="0.70"/>
  </linearGradient>
  <linearGradient id="hem" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#000" stop-opacity="0"/>
    <stop offset="0.72" stop-color="#000" stop-opacity="0"/>
    <stop offset="1" stop-color="#000" stop-opacity="0.45"/>
  </linearGradient>
  <filter id="soft" x="-40%" y="-40%" width="180%" height="180%">
    <feGaussianBlur stdDeviation="22"/>
  </filter>
  <filter id="soft2" x="-60%" y="-60%" width="220%" height="220%">
    <feGaussianBlur stdDeviation="38"/>
  </filter>
  <filter id="drop" x="-30%" y="-40%" width="160%" height="180%">
    <feDropShadow dx="0" dy="18" stdDeviation="18" flood-color="#000" flood-opacity="0.72"/>
  </filter>
  <!-- el torso, que es lo que lleva la camiseta puesta -->
  <clipPath id="body">
    <path d="M52 {H} C 56 830, 92 782, 148 756 C 210 728, 272 694, 336 678
             C 376 668, 524 668, 564 678 C 628 694, 690 728, 752 756
             C 808 782, 844 830, 848 {H} Z"/>
  </clipPath>
</defs>
<rect width="{W}" height="{H}" fill="url(#bg)"/>

<g clip-path="url(#body)">
  <rect width="{W}" height="{H}" fill="url(#tee)"/>
  <rect width="{W}" height="{H}" fill="url(#flanks)"/>
  <rect y="600" width="{W}" height="300" fill="url(#hem)"/>
  <!-- el pecho, que es lo que levanta la tela -->
  <ellipse cx="450" cy="792" rx="230" ry="170" fill="url(#chest)"/>
  <!-- los hombros, redondos -->
  <ellipse cx="228" cy="806" rx="120" ry="150" fill="#3FE0D0" opacity="0.10" filter="url(#soft2)"/>
  <ellipse cx="672" cy="806" rx="120" ry="150" fill="#3FE0D0" opacity="0.07" filter="url(#soft2)"/>
  <!-- costuras de manga, siguiendo el hombro -->
  <path d="M196 742 C 236 790, 252 846, 248 {H}" fill="none" stroke="#04413E"
        stroke-width="5" opacity="0.42"/>
  <path d="M704 742 C 664 790, 648 846, 652 {H}" fill="none" stroke="#04413E"
        stroke-width="5" opacity="0.42"/>
  <path d="M196 742 C 236 790, 252 846, 248 {H}" fill="none" stroke="#5CEEDF"
        stroke-width="2" opacity="0.22" transform="translate(5,0)"/>
  <path d="M704 742 C 664 790, 648 846, 652 {H}" fill="none" stroke="#5CEEDF"
        stroke-width="2" opacity="0.18" transform="translate(-5,0)"/>
  <!-- pliegues sueltos, para que no parezca plástico -->
  <path d="M330 830 C 356 868, 372 890, 376 {H}" fill="none" stroke="#04413E"
        stroke-width="7" opacity="0.16"/>
  <path d="M570 830 C 544 868, 528 890, 524 {H}" fill="none" stroke="#04413E"
        stroke-width="7" opacity="0.14"/>
  <!-- la sombra que echa la cabeza sobre el pecho -->
  <ellipse cx="450" cy="700" rx="196" ry="74" fill="#000" opacity="0.55" filter="url(#soft)"/>
</g>

<image href="{SRC}" x="{MX}" y="{MY}" width="{MW}" height="{MH}" filter="url(#drop)"/>
{COLLAR}
{LOGO}
</svg>'''

def svg_for(key):
    r=head(key)
    ok,buf=cv2.imencode('.png',r)
    src='data:image/png;base64,'+base64.b64encode(buf.tobytes()).decode()
    k=SRC[key]['k']
    mh=int(H*k); mw=int(r.shape[1]*mh/r.shape[0])
    logo=LOGO.format(lx=450-0.5*300*0.44, ly=742, ls=0.44)
    return SVG.format(W=W,H=H,SRC=src,MW=mw,MH=mh,
                      MX=W//2-mw//2,MY=NECK-mh,LOGO=logo,
                      COLLAR=COLLAR if SRC[key]['collar'] else '')

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
