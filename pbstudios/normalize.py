"""Lleva todas las fotos de producto a la misma estética:
   encuadre cuadrado sobre la pieza, luz igualada y fondo de estudio común."""
from PIL import Image, ImageOps, ImageEnhance, ImageFilter, ImageChops
import base64, io, json, os

U='/root/.claude/uploads/6020d028-8fb4-5cc4-ad09-02e6a808b983/'
SP='/tmp/claude-0/-home-user-Test/6020d028-8fb4-5cc4-ad09-02e6a808b983/scratchpad/'
STUDIO=(238,235,228)          # el mismo tono que --sunk del sitio
OUT=1000

SETS={
 'batman':['ee82fcc5','553f9807','89026594'],
 'venom' :['35b513c2','6dcdc262','7194c110','423b76bd','f52b6341'],
 'ranger':['726be8c9','d16f09c8','ab5f4c77','d76d8bf5','febc04e7'],
}

def photo_band(im):
    """quita la interfaz del móvil: busca la franja que no es color plano"""
    W,H=im.size; chrome=im.getpixel((5,300))
    def flat(y):
        return all(sum(abs(a-b) for a,b in zip(im.getpixel((x,y)),chrome))<26 for x in range(0,W,60))
    ys=[y for y in range(0,H,4) if not flat(y)]
    best=(0,H); run=None
    for y in ys:
        if run is None or y-run[1]>12: run=[y,y]
        else: run[1]=y
        if run[1]-run[0]>best[1]-best[0]: best=(run[0],run[1])
    return im.crop((0,best[0],W,best[1]))

def bg_color(im):
    w,h=im.size; s=24
    pts=[(s,s),(w-s,s),(s,h-s),(w-s,h-s),(w//2,s)]
    px=[im.getpixel(p) for p in pts]
    return tuple(sum(c[i] for c in px)//len(px) for i in range(3))

def obj_mask(im,bg,tol=42,blur=3):
    """máscara suave del objeto: cuánto se aleja cada píxel del fondo"""
    r,g,b=im.split()
    diff=ImageChops.add(ImageChops.add(
        ImageChops.difference(r,Image.new('L',im.size,bg[0])),
        ImageChops.difference(g,Image.new('L',im.size,bg[1]))),
        ImageChops.difference(b,Image.new('L',im.size,bg[2])))
    m=diff.point(lambda v:0 if v<tol else min(255,int((v-tol)*255/38)))
    return m.filter(ImageFilter.GaussianBlur(blur))

def bbox_from(mask,frac=.020):
    w,h=mask.size
    small=mask.resize((w//5,h//5))
    px=small.load(); W,H=small.size
    rows=[y for y in range(H) if sum(1 for x in range(W) if px[x,y]>60)>W*frac]
    cols=[x for x in range(W) if sum(1 for y in range(H) if px[x,y]>60)>H*frac]
    if not rows or not cols: return (0,0,w,h)
    return (cols[0]*5,rows[0]*5,(cols[-1]+1)*5,(rows[-1]+1)*5)

def vignette(size,strength=.16):
    w,h=size
    v=Image.new('L',(w,h),255)
    grad=Image.radialgradient=None
    # degradado radial hecho a mano, más barato que dibujar elipses
    small=Image.new('L',(160,160))
    px=small.load()
    for y in range(160):
        for x in range(160):
            dx=(x-79.5)/79.5; dy=(y-79.5)/79.5
            d=min(1.0,(dx*dx+dy*dy)**.5/1.32)
            px[x,y]=int(255*(1-strength*d*d))
    return small.resize((w,h),Image.BICUBIC)

def process(path):
    im=Image.open(path).convert('RGB')
    im=photo_band(im)
    w,h=im.size; im=im.crop((6,6,w-6,h-6))      # bordes sucios de la captura
    bg=bg_color(im)
    dark_bg = sum(bg)/3 < 110
    mask=obj_mask(im,bg,tol=22 if dark_bg else 42)
    x0,y0,x1,y1=bbox_from(mask)

    # Fondo de estudio: en vez de sustituirlo por un color plano (que canta si la
    # máscara falla), se desenfoca la propia foto, se aclara y se tira hacia el
    # mismo tono en todas. Así los tres productos comparten fondo y los errores
    # de recorte no se ven.
    # Con fondo oscuro la máscara no es fiable y el remiendo se nota más que el
    # problema: esas fotos solo se reencuadran. Hay que rehacerlas con cámara.
    if not dark_bg:
        soft=im.filter(ImageFilter.GaussianBlur(16))
        soft=ImageEnhance.Brightness(soft).enhance(1.12)
        soft=ImageEnhance.Color(soft).enhance(0.18)
        studio=Image.blend(soft,Image.new('RGB',im.size,STUDIO),0.62)
        im=Image.composite(im,studio,mask)

    # encuadre cuadrado sobre la pieza, con aire alrededor
    cx=(x0+x1)//2; cy=(y0+y1)//2
    side=int(max(x1-x0,y1-y0)*1.16)
    W,H=im.size; side=min(side,min(W,H))
    left=max(0,min(W-side,cx-side//2)); top=max(0,min(H-side,cy-side//2))
    im=im.crop((left,top,left+side,top+side)).resize((OUT,OUT),Image.LANCZOS)

    # misma luz para todas
    if not dark_bg:
        im=ImageOps.autocontrast(im,cutoff=(0.4,0.2))
        im=ImageEnhance.Color(im).enhance(1.06)
        im=ImageEnhance.Contrast(im).enhance(1.04)
    im=Image.composite(im,Image.new('RGB',im.size,(0,0,0)),vignette(im.size).point(lambda v:v))
    im=Image.merge('RGB',[c.point(lambda v:v) for c in im.split()])
    return im

def enc(im,q=80):
    buf=io.BytesIO(); im.save(buf,'JPEG',quality=q,optimize=True,progressive=True)
    return buf.getvalue()

photos={}; total=0
sheet=Image.new('RGB',(OUT//4*5,OUT//4*3),(255,255,255))
for row,(key,files) in enumerate(SETS.items()):
    photos[key]=[]
    for col,f in enumerate(files):
        im=process(U+f+'-image.png')
        b=enc(im); total+=len(b)
        photos[key].append('data:image/jpeg;base64,'+base64.b64encode(b).decode())
        sheet.paste(im.resize((OUT//4,OUT//4)),(col*(OUT//4),row*(OUT//4)))
        print(f'{key:7} {f} {len(b)/1024:5.0f} KB')
sheet.save(SP+'contactos.png')
open(SP+'photos.json','w').write(json.dumps(photos))
print(f'TOTAL {total/1024:.0f} KB · base64 ≈ {total*1.34/1024:.0f} KB')
