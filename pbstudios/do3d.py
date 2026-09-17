"""Prepara los renders del pack de Do3D para la ficha del Venom.

Vienen a 560 px, con la marca del estudio sobre negro plano y un fondo apagado.
Aquí se limpia la esquina, se reescala con cuidado, se le da ambiente de
estudio —contraluz de color, bruma y bloom— y se oscurece la piel del maniquí,
para que la ficha no sea la imagen del pack tal cual.
"""
import cv2, numpy as np, base64, json

U='/root/.claude/uploads/6020d028-8fb4-5cc4-ad09-02e6a808b983/'
SP='/tmp/claude-0/-home-user-Test/6020d028-8fb4-5cc4-ad09-02e6a808b983/scratchpad/'
SRC=['10835edc','d33d640f','79a76934']
OUT=1200
AMBIENT=(44,22,128)          # BGR: el contraluz, del rojo del propio simbionte

# ── 1. limpieza ────────────────────────────────────────────────────────────
def unmark(img):
    """la marca del estudio va sobre negro plano: se localiza y se rellena"""
    box=img[:72,:120]                            # justo la esquina, ni un pixel más
    m=(box.max(2)>90).astype(np.uint8)*255
    if m.sum()==0: return img
    m=cv2.dilate(m,np.ones((5,5),np.uint8))
    full=np.zeros(img.shape[:2],np.uint8); full[:72,:120]=m
    return cv2.inpaint(img,full,7,cv2.INPAINT_TELEA)

def upscale(img,side):
    """El origen son 560 px: no hay detalle que inventar, pero sí se puede
       subir sin que se note el escalón. Dos pasos de Lanczos, un filtro que
       respeta bordes para quitar el churre del JPEG, y enfoque al final."""
    h=img.shape[0]
    for _ in range(2):
        if h>=side: break
        h=min(side,int(h*1.7))
        img=cv2.resize(img,(h,h),interpolation=cv2.INTER_LANCZOS4)
    img=cv2.resize(img,(side,side),interpolation=cv2.INTER_LANCZOS4)
    # nada de suavizar: es render limpio, no foto con ruido. Solo enfoque.
    img=cv2.addWeighted(img,1.24,cv2.GaussianBlur(img,(0,0),2.2),-0.24,0)
    return cv2.addWeighted(img,1.14,cv2.GaussianBlur(img,(0,0),0.9),-0.14,0)

# ── 2. máscaras ────────────────────────────────────────────────────────────
def subject(img):
    """la pieza y el maniquí contra el fondo, que es casi negro"""
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
    return cv2.GaussianBlur(m,(0,0),2.5).astype(np.float32)/255.0

def skin(img,sub):
    """El cuello y los hombros del maniquí. En YCrCb la piel cae en una
       ventana estrecha; el rojo del simbionte se va muy por encima de Cr,
       así que no se los come."""
    y=cv2.cvtColor(img,cv2.COLOR_BGR2YCrCb)
    cr,cb=y[:,:,1].astype(int), y[:,:,2].astype(int)
    sat=cv2.cvtColor(img,cv2.COLOR_BGR2HSV)[:,:,1].astype(int)
    # el rojo del simbionte cae en la misma ventana de Cr que la piel, pero va
    # muy saturado: el techo de saturación es lo que los separa
    m=((cr>131)&(cr<173)&(cb>74)&(cb<132)&(y[:,:,0]>26)&(sat<108)).astype(np.uint8)*255
    m[:int(m.shape[0]*0.45)]=0                   # arriba solo hay pieza
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((5,5),np.uint8))
    m=cv2.morphologyEx(m,cv2.MORPH_CLOSE,np.ones((25,25),np.uint8))
    n,lab,stats,_=cv2.connectedComponentsWithStats((m>0).astype(np.uint8),8)
    keep=np.zeros_like(m)
    for i in range(1,n):
        x,yy,w,h,a=stats[i]
        # cuello y hombros llegan al borde de abajo; los dientes claros, no
        if yy+h>=m.shape[0]-4 and a>m.size*0.004: keep[lab==i]=255
    return cv2.GaussianBlur(keep,(0,0),4.0).astype(np.float32)/255.0*sub

def tan(img,sk):
    """más moreno: baja la luminancia y empuja el tono a tierra"""
    img=np.clip(img,0,255).astype(np.uint8)
    lab=cv2.cvtColor(img,cv2.COLOR_BGR2LAB).astype(np.float32)
    lab[:,:,0]*=0.66; lab[:,:,1]+=7; lab[:,:,2]+=17
    warm=cv2.cvtColor(np.clip(lab,0,255).astype(np.uint8),cv2.COLOR_LAB2BGR).astype(np.float32)
    return img.astype(np.float32)*(1-sk[...,None])+warm*sk[...,None]

# ── 3. luz ─────────────────────────────────────────────────────────────────
def grade(img):
    """Contraste fotográfico, sin la crudeza del contraste local exagerado."""
    lab=cv2.cvtColor(np.clip(img,0,255).astype(np.uint8),cv2.COLOR_BGR2LAB).astype(np.float32)
    L=lab[:,:,0]/255.0
    s=1/(1+np.exp(-4.0*(L-0.48)))                # curva suave
    s=(s-1/(1+np.exp(4.0*0.48)))/((1/(1+np.exp(-4.0*0.52)))-(1/(1+np.exp(4.0*0.48))))
    L2=np.clip(255*(0.58*L+0.42*np.clip(s,0,1)),0,255)
    L2=255*(1-np.exp(-2.1*L2/255))/(1-np.exp(-2.1))          # freno arriba
    L2=L2*0.985+4                                            # los negros respiran, poco
    L2=np.clip(L2+(L2-cv2.GaussianBlur(L2,(0,0),3.0))*0.16,0,255)   # nitidez, no claridad
    lab[:,:,0]=L2
    out=cv2.cvtColor(lab.astype(np.uint8),cv2.COLOR_LAB2BGR).astype(np.float32)
    t=(L2/255.0)[...,None]
    return np.clip(out+(1-t)*np.array([9,1,-5],np.float32)+t*np.array([-4,0,6],np.float32),0,255)

def ambient(h,w,m):
    """Fondo de estudio con contraluz de color y bruma: es lo que hace que
       apetezca. El halo sale por detrás de la silueta, no por delante."""
    yy,xx=np.mgrid[0:h,0:w].astype(np.float32)
    d=np.sqrt(((xx-w*0.5)/(w*0.80))**2+((yy-h*0.40)/(h*0.86))**2)
    base=np.array([10,9,8],np.float32)+np.array([26,23,20],np.float32)*np.clip(1-d,0,1)[...,None]**1.7
    halo=cv2.GaussianBlur(m,(0,0),w*0.055)                   # el resplandor de detrás
    halo=np.clip(halo-m,0,1)
    halo=halo/(halo.max() or 1)
    bg=base+halo[...,None]*np.array(AMBIENT,np.float32)*0.62
    # bruma: una franja de luz en diagonal, muy floja
    haze=np.clip(1-np.abs((xx*0.55+yy*0.45)/(w*0.85)-0.42)*3.0,0,1)**2
    return bg+haze[...,None]*np.array([11,10,9],np.float32)

def bloom(img,amount=0.22):
    hi=np.clip(img-176,0,None)
    return np.clip(img+cv2.GaussianBlur(hi,(0,0),26)*amount,0,255)

def run(f):
    img=upscale(unmark(cv2.imread(U+f+'-image.jpg')),OUT)
    m=subject(img)
    sk=skin(img,m)
    g=tan(grade(img),sk)          # primero la luz, luego el tono: si no, la
                                  # curva vuelve a aclarar lo que acabas de bajar
    bg=ambient(OUT,OUT,m)
    out=bg*(1-m[...,None])+g*m[...,None]
    out=out*(1-np.clip(cv2.GaussianBlur(m,(0,0),34)*0.5-m,0,1)[...,None]*0.45)   # sombra
    return bloom(out).astype(np.uint8)

if __name__=='__main__':
    outs=[]; data=[]
    for f in SRC:
        o=run(f); outs.append(o)
        ok,buf=cv2.imencode('.jpg',o,[cv2.IMWRITE_JPEG_QUALITY,88])
        b=buf.tobytes(); data.append('data:image/jpeg;base64,'+base64.b64encode(b).decode())
        print(f, f'{o.shape[0]} px  {len(b)/1024:.0f} KB')
    cv2.imwrite(SP+'do3d.png',np.hstack([cv2.resize(o,(540,540)) for o in outs]))
    open(SP+'venom.json','w').write(json.dumps(data))
