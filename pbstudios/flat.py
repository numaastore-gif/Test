"""Deja los renders del pack como vienen: sin marca y en cuadrado.

Nada de maniquí dibujado ni camiseta: el render del pack ya trae su figura y
su luz. Lo único que se hace es quitar la marca del estudio, partir las
láminas que traen dos vistas, y encuadrar en cuadrado sobre negro para que
todas las fichas midan lo mismo. Cuando el pack solo trae dos vistas, la
tercera es una de ellas espejada: en una pieza simétrica, el otro lado.
"""
import cv2, numpy as np, base64, json
import do3d

U=do3d.U; SP=do3d.SP
SIDE=560

# clave -> [(fichero, mitad de la lámina, espejar), ...]
SETS={
 'venom'  :[('10835edc','',False),('d33d640f','',False),('79a76934','',False)],
 'batman2':[('850e419e','L',False),('850e419e','L',True),('850e419e','R',False)],
 'redbat' :[('f2545ca9','',False),('f2545ca9','',True),('4aeaa1d6','',False)],
}
# Las piezas que solo tienen foto tuya no pueden salir como un render del pack,
# pero sí pueden compartir fondo: se recomponen sobre el mismo negro.
PHOTO={'batman':['batman'],'ranger':['ranger']}

def half(img,which):
    """las láminas con dos vistas se parten por la columna más vacía"""
    g=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    col=(g>18).sum(0); w=img.shape[1]
    cut=int(w*0.35)+int(np.argmin(col[int(w*0.35):int(w*0.65)]))
    return img[:,:cut] if which=='L' else img[:,cut:]

def square(img):
    """Media lámina a cuadrado. Se recorta solo de lado —la figura al centro—
       y se deja el alto tal cual: el encuadre vertical del render ya está
       bien, y recortarlo dejaría la camiseta del maniquí cortada en recto."""
    g=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    xs=np.where((g>16).any(0))[0]
    if not len(xs): return cv2.resize(img,(SIDE,SIDE))
    cx=(xs.min()+xs.max())//2
    h=img.shape[0]
    x0=cx-h//2
    out=np.zeros((h,h,3),np.uint8)
    sx0,sx1=max(0,x0),min(img.shape[1],x0+h)
    out[:,sx0-x0:sx1-x0]=img[:,sx0:sx1]
    return cv2.resize(out,(SIDE,SIDE),interpolation=cv2.INTER_AREA)

def on_black(key):
    """el recorte de tu foto, centrado sobre el mismo negro que los renders"""
    r=cv2.imread(SP+'cut-'+key+'.png',cv2.IMREAD_UNCHANGED)
    a=cv2.GaussianBlur(cv2.erode(r[:,:,3],np.ones((3,3),np.uint8)),(0,0),1.0)
    a=a.astype(np.float32)/255.0
    h,w=r.shape[:2]
    k=SIDE*0.86/max(h,w)
    rgb=cv2.resize(r[:,:,:3],(int(w*k),int(h*k)),interpolation=cv2.INTER_AREA)
    a=cv2.resize(a,(int(w*k),int(h*k)),interpolation=cv2.INTER_AREA)[...,None]
    h,w=rgb.shape[:2]
    yy,xx=np.mgrid[0:SIDE,0:SIDE].astype(np.float32)
    d=np.sqrt(((xx-SIDE*0.5)/(SIDE*0.8))**2+((yy-SIDE*0.4)/(SIDE*0.85))**2)
    out=(np.clip(1-d,0,1)[...,None]**1.7*np.array([13,12,11],np.float32))
    y,x=(SIDE-h)//2,(SIDE-w)//2
    sub=out[y:y+h,x:x+w]
    out[y:y+h,x:x+w]=rgb.astype(np.float32)*a+sub*(1-a)
    return np.clip(out,0,255).astype(np.uint8)

def view(f,which,flip):
    img=do3d.unmark(cv2.imread(U+f+'-image.jpg'))
    if which: img=square(half(img,which))
    return img[:,::-1].copy() if flip else img

if __name__=='__main__':
    out={}
    for key,views in SETS.items():
        out[key]=[]
        for f,which,flip in views:
            im=view(f,which,flip)
            ok,buf=cv2.imencode('.jpg',im,[cv2.IMWRITE_JPEG_QUALITY,92])
            out[key].append('data:image/jpeg;base64,'+base64.b64encode(buf.tobytes()).decode())
            print(f'{key:8} {f} {which or "-"}{" espejada" if flip else ""}  {len(buf)/1024:.0f} KB')
        cv2.imwrite(SP+'flat-'+key+'.png',
                    np.hstack([cv2.resize(view(*v),(300,300)) for v in views]))
    for key in PHOTO:
        im=on_black(key)
        ok,buf=cv2.imencode('.jpg',im,[cv2.IMWRITE_JPEG_QUALITY,92])
        out[key]=['data:image/jpeg;base64,'+base64.b64encode(buf.tobytes()).decode()]
        cv2.imwrite(SP+'flat-'+key+'.png',im)
        print(f'{key:8} recorte sobre negro  {len(buf)/1024:.0f} KB')
    open(SP+'flat.json','w').write(json.dumps(out))
