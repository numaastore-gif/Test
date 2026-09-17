"""Prepara los renders del pack de Do3D para la ficha del Venom.

Vienen con la marca del estudio en la esquina, sobre negro plano. Se quita y
ya está: el render es del pack, va con su licencia, y tocarle luz y color solo
lo alejaba de lo que el cliente va a recibir.
"""
import cv2, numpy as np, base64, json

U='/root/.claude/uploads/6020d028-8fb4-5cc4-ad09-02e6a808b983/'
SP='/tmp/claude-0/-home-user-Test/6020d028-8fb4-5cc4-ad09-02e6a808b983/scratchpad/'
SRC=['10835edc','d33d640f','79a76934']

# ── 1. limpieza ────────────────────────────────────────────────────────────
def unmark(img):
    """la marca del estudio va sobre negro plano: se localiza y se rellena"""
    box=img[:72,:120]                            # justo la esquina, ni un pixel más
    m=(box.max(2)>90).astype(np.uint8)*255
    if m.sum()==0: return img
    m=cv2.dilate(m,np.ones((5,5),np.uint8))
    full=np.zeros(img.shape[:2],np.uint8); full[:72,:120]=m
    return cv2.inpaint(img,full,7,cv2.INPAINT_TELEA)

def run(f):
    return unmark(cv2.imread(U+f+'-image.jpg'))

if __name__=='__main__':
    outs=[]; data=[]
    for f in SRC:
        o=run(f); outs.append(o)
        ok,buf=cv2.imencode('.jpg',o,[cv2.IMWRITE_JPEG_QUALITY,92])
        b=buf.tobytes(); data.append('data:image/jpeg;base64,'+base64.b64encode(b).decode())
        print(f, f'{o.shape[0]} px  {len(b)/1024:.0f} KB')
    cv2.imwrite(SP+'do3d.png',np.hstack(outs))
    open(SP+'venom.json','w').write(json.dumps(data))
