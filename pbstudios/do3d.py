"""Prepara los renders del pack de Do3D para la ficha del Venom.

Vienen con la marca del estudio en la esquina, sobre negro plano, y con el
fondo completamente apagado. Aquí se limpia la esquina, se le da fondo de
estudio en vez de negro liso, y se trabaja luz y sombra de la pieza: curva
de contraste suave, claridad y un poco de color.
"""
import cv2, numpy as np, base64, json

U='/root/.claude/uploads/6020d028-8fb4-5cc4-ad09-02e6a808b983/'
SP='/tmp/claude-0/-home-user-Test/6020d028-8fb4-5cc4-ad09-02e6a808b983/scratchpad/'
SRC=['10835edc','d33d640f','79a76934']
OUT=900

def unmark(img):
    """la marca del estudio va sobre negro plano: se localiza y se rellena"""
    box=img[:110,:190]
    m=(box.max(2)>90).astype(np.uint8)*255
    if m.sum()==0: return img
    m=cv2.dilate(m,np.ones((7,7),np.uint8))
    full=np.zeros(img.shape[:2],np.uint8); full[:110,:190]=m
    return cv2.inpaint(img,full,7,cv2.INPAINT_TELEA)

def subject(img):
    """la pieza contra el fondo: el fondo es casi negro y toca el marco"""
    g=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    m=(g>16).astype(np.uint8)*255
    m=cv2.morphologyEx(m,cv2.MORPH_CLOSE,np.ones((9,9),np.uint8))
    n,lab,stats,_=cv2.connectedComponentsWithStats((m>0).astype(np.uint8),8)
    if n>1:
        big=1+np.argmax(stats[1:,cv2.CC_STAT_AREA])
        m=((lab==big)*255).astype(np.uint8)
    # los negros internos de la máscara son pieza, no fondo
    inv=cv2.bitwise_not(m)
    n,lab,stats,_=cv2.connectedComponentsWithStats((inv>0).astype(np.uint8),8)
    for i in range(1,n):
        x,y,w,h,a=stats[i]
        if x>0 and y>0 and x+w<m.shape[1] and y+h<m.shape[0]: m[lab==i]=255
    return cv2.GaussianBlur(m,(0,0),2.0).astype(np.float32)/255.0

def studio(h,w):
    """fondo de estudio: no negro plano, un degradado con algo de aire"""
    yy,xx=np.mgrid[0:h,0:w].astype(np.float32)
    d=np.sqrt(((xx-w*0.5)/(w*0.72))**2+((yy-h*0.36)/(h*0.78))**2)
    k=np.clip(1-d,0,1)**1.8
    top=np.array([48,42,36],np.float32)          # BGR, gris azulado
    bot=np.array([8,7,6],np.float32)
    return bot+ (top-bot)*k[...,None]

def grade(img,m):
    f=img.astype(np.float32)
    lab=cv2.cvtColor(np.clip(f,0,255).astype(np.uint8),cv2.COLOR_BGR2LAB).astype(np.float32)
    L=lab[:,:,0]
    # curva en S suave: negros más limpios y medios más abiertos
    x=L/255.0
    s=1/(1+np.exp(-5.0*(x-0.46)))
    s=(s-1/(1+np.exp(5.0*0.46)))/((1/(1+np.exp(-5.0*0.54)))-(1/(1+np.exp(5.0*0.46))))
    L2=np.clip(255*(0.42*x+0.58*np.clip(s,0,1)),0,255)
    L2=L2*0.94+16                              # los negros no se cierran del todo
    # claridad: contraste local, que es lo que saca el relieve del simbionte
    blur=cv2.GaussianBlur(L2,(0,0),14)
    L2=np.clip(L2+(L2-blur)*0.42,0,255)
    # y un micro-realce para el diente y la costura
    L2=np.clip(L2+(L2-cv2.GaussianBlur(L2,(0,0),2.2))*0.30,0,255)
    L2=255*(1-np.exp(-1.9*L2/255))/(1-np.exp(-1.9))   # freno en altas luces
    lab[:,:,0]=L2
    out=cv2.cvtColor(lab.astype(np.uint8),cv2.COLOR_LAB2BGR).astype(np.float32)
    hsv=cv2.cvtColor(np.clip(out,0,255).astype(np.uint8),cv2.COLOR_BGR2HSV).astype(np.float32)
    hsv[:,:,1]=np.clip(hsv[:,:,1]*1.10,0,255)
    out=cv2.cvtColor(hsv.astype(np.uint8),cv2.COLOR_HSV2BGR).astype(np.float32)
    # las sombras, un punto más frías; las luces, un punto más cálidas
    t=(L2/255.0)[...,None]
    out=out+ (1-t)*np.array([7,1,-4],np.float32) + t*np.array([-3,0,5],np.float32)
    return np.clip(out,0,255)

def rim(m):
    """contraluz: un filo de luz donde la silueta da la espalda al foco"""
    e=cv2.Sobel(m,cv2.CV_32F,1,0,ksize=5)
    r=np.clip(-e,0,None)                          # solo el borde derecho
    r=cv2.GaussianBlur(r,(0,0),3.0)
    r=r/ (r.max() or 1)
    return r*m

def run(f):
    img=unmark(cv2.imread(U+f+'-image.jpg'))
    m=subject(img)
    g=grade(img,m)
    bg=studio(*img.shape[:2])
    out=bg*(1-m[...,None])+g*m[...,None]
    # sombra de la pieza sobre el fondo, para que no flote
    sh=cv2.GaussianBlur(m,(0,0),30)*0.40
    out=out*(1-np.clip(sh-m,0,1)[...,None]*0.55)
    out=out+ rim(m)[...,None]*np.array([40,44,46],np.float32)
    out=cv2.resize(np.clip(out,0,255).astype(np.uint8),(OUT,OUT),interpolation=cv2.INTER_CUBIC)
    return cv2.addWeighted(out,1.18,cv2.GaussianBlur(out,(0,0),1.6),-0.18,0)

if __name__=='__main__':
    outs=[]; data=[]
    for f in SRC:
        o=run(f); outs.append(o)
        ok,buf=cv2.imencode('.jpg',o,[cv2.IMWRITE_JPEG_QUALITY,86])
        b=buf.tobytes(); data.append('data:image/jpeg;base64,'+base64.b64encode(b).decode())
        print(f, f'{len(b)/1024:.0f} KB')
    cv2.imwrite(SP+'do3d.png',np.hstack([cv2.resize(o,(520,520)) for o in outs]))
    open(SP+'venom.json','w').write(json.dumps(data))
