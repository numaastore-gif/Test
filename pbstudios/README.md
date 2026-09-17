# PB Studios — tienda de impresión 3D

Primer ejemplo de tienda para **@_PBStudios**. Un solo archivo (`index.html`),
sin build, sin backend y sin dependencias: solo Google Fonts.

## La idea

Un cliente entra, ve las piezas, las gira en 3D, elige material, color y tamaño,
ve el precio cambiar y cierra el pedido por Instagram. Y si lo que quiere no está
en el catálogo, **sube su propio archivo** y la web se lo presupuesta sola.

## Solo máscaras y cascos

El catálogo son las tres piezas reales y nada más. Las doce piezas de ejemplo
generadas por código (jarrones, macetas, portalápices…) están fuera, y con
ellas el motor de mallas paramétricas que las dibujaba: `lathe`, `prism`,
`gear`, `torus`, `merge` y el pintor por caras ordenadas. Eran unas 150 líneas
que ya no pintaban nada. Lo que se dibuja en 3D hoy sale siempre de un archivo
de verdad —el holograma del hero y la vista previa del presupuesto—, y para eso
están `buildMesh` y `rasterize`.

Las categorías pasan a ser **Cascos** y **Máscaras**, que es un filtro que
significa algo, en vez de un único «Cosplay».

## Qué hace

| Módulo | Detalle |
|---|---|
| **Hero** | Banda oscura, y dentro flota un **holograma de una máscara** rebanado en capas de verdad. Tres fases —Archivo, Capas, Pieza— que el visitante elige, o que van solas hasta que las toca. Se gira arrastrando y se inclina sola hacia el ratón. |
| **Logo** | Redibujado como vector (`#pbMark` / `#pbLockup`), sin fondo, así que sirve igual en claro y en oscuro y escala sin pixelarse. Su pieza interior (`#pbPart`) crece con el mismo barrido que el holograma en la fase *Capas*: el logo no es un adorno, está contando lo que hace el taller. |
| **Confianza** | Tira de cuatro compromisos bajo el hero: licencia comercial, foto antes de enviar, si sale mal se repite, entrega 24–48 h. |
| **Presupuesto por archivo** | El cliente **suelta su STL** y la web lo lee en el navegador: triángulos, volumen real, caja envolvente y previsualización 3D arrastrable. Con eso, más material, relleno, altura de capa, soportes y unidades, sale el precio con el desglose. Avisa si la pieza no cabe en 250 mm. |
| **Escala** | En las fichas con foto, un esquema compara la altura de la pieza con una cabeza adulta (22 cm). Responde a la pregunta que de verdad frena la compra. |
| **Catálogo** | 12 piezas con filtro por categoría, buscador y orden por ventas, precio o novedad. Cada tarjeta lleva su render 3D. |
| **Ficha de producto** | Visor 3D que gira solo y se puede arrastrar. Color, material y tamaño cambian el render, el peso, el tiempo de impresión y el precio al momento. |
| **Carrito** | Panel lateral, persistente en el navegador. El pedido se genera como texto listo para mandar por Instagram o WhatsApp. |
| **Medidas a mano** | Alternativa plegada dentro del módulo anterior, para quien todavía no tiene el archivo: medidas de la caja, material y relleno. Descuento automático por tanda a partir de 10 unidades. |
| **Materiales** | PLA, PLA Silk, PETG y TPU, cada uno con para qué sirve, densidad y precio por gramo. |
| **Resto** | Cómo funciona en cuatro pasos, preguntas frecuentes, contacto, tema claro/oscuro y barra de progreso. |

## Cómo se calcula el precio

- **Catálogo:** `precio base × (0,35 + 0,65 × escala³) × (1 + (coste material − 1) × 0,45)`.
  En PLA y talla M da exactamente el precio anunciado en la tarjeta.
- **A medida:** con archivo, el volumen es el **real de la malla** (suma de
  tetraedros con signo sobre cada triángulo) y el área sirve para estimar la
  pared de 1,2 mm; el resto del volumen va al relleno elegido. Sin archivo se
  parte del volumen de la caja. De ahí los gramos, y de los gramos las horas.
  Precio = preparación + material + máquina + soportes.

Las constantes están al principio del `<script>`: `SETUP` (preparación) y `HOUR`
(coste de máquina por hora).

## Productos reales ya cargados

Tres, con sus fotos incrustadas en el archivo como data URI (recortadas de las
capturas, sin la interfaz del móvil, a 820 px y JPEG: unos 900 KB en total):

| Producto | Raw | Pintado | Fotos |
|---|---|---|---|
| Casco de Batman | 65 € | 156 € | 3, recortadas de tus capturas |
| Máscara Venom / Spider-Man | 40 € | 96 € | 3, del pack de Do3D |
| Casco de Power Ranger amarillo | 55 € | 132 € | 3, recortadas de tus capturas |

Los tres comparten el mismo escalón de acabado, que es como se vende de verdad
una pieza impresa: **raw** ×1 (sin postprocesar, con las capas a la vista),
**lijado e imprimado** ×1,55 (listo para pintar) y **pintado a mano** ×2,40. El
precio base de cada producto es el del raw; la tarjeta enseña el rango completo
y la ficha abre en el acabado de las fotos.

## Leer el archivo en el navegador

No hay backend, así que el STL se parsea en el propio navegador. Se detecta si es
binario comprobando que `byteLength === 84 + nº_triángulos × 50`; si no cuadra,
se lee como ASCII con una expresión regular sobre los `vertex`. Después:

- **volumen**: suma del volumen con signo de los tetraedros que forma cada
  triángulo con el origen — vale para cualquier malla cerrada, con concavidades
  y agujeros incluidos;
- **área** y **caja envolvente** en la misma pasada;
- para la vista previa la malla se pasa de Z-arriba (convenio CAD) a Y-arriba y
  se normaliza por la **diagonal** de la caja, para que no se salga del marco al
  girarla.

## El holograma del hero

El hero es una sala de proyección: fondo casi negro y una máscara flotando
dentro, dibujada **en capas**, que es exactamente lo que hace un laminador
antes de mandar nada a la impresora.

Las capas no son un efecto. Cada triángulo que cruza un plano horizontal deja
un segmento; el conjunto de segmentos de un plano es el contorno de esa capa.
Se calcula una sola vez al cargar (`sliceMesh`) y luego cada fotograma solo
proyecta y dibuja. Los segmentos se reparten en seis franjas de profundidad y
cada franja se pinta de una vez con su propio grosor y transparencia, así que
los contornos de atrás se ven detrás sin ordenar nada ni ralentizar nada.

Tres fases, en pestañas, que van solas hasta que el visitante toca una:

| Fase | Qué enseña |
|---|---|
| **Archivo** | contornos separados y la caja de la pieza a rayas: la malla tal cual llega |
| **Capas** | contornos finos, y una cabeza de impresión que sube dejando capas detrás y el resto en fantasma |
| **Pieza** | el render sólido, el mismo rasterizador que usa el visor del presupuesto |

Interactivo de verdad: se gira arrastrando, con inercia, y si solo pasas el
ratón por encima la máscara se inclina un poco hacia ti. El HUD canta los
triángulos, las capas a 0,20 mm y la altura real en milímetros.

**La máscara es provisional.** Está generada por código (`maskMesh`): una
cáscara de cara con nariz, ceja y mandíbula, y los huecos de ojos y boca
recortados limpiamente — los vértices que caen dentro del hueco se empujan
justo a su borde, por eso el contorno del ojo es una elipse y no una escalera.
En cuanto haya un STL de máscara de verdad, se sustituye y ya está: pasa por el
mismo `measure` + `buildMesh` que el archivo que sube un cliente, así que el
rebanado, el holograma y el render sólido funcionan igual sin tocar nada más.

## Por qué la pieza se ve sólida y no como una maraña de triángulos

La primera versión se quedaba con uno de cada N triángulos para que el visor
fuese rápido. Eso abre agujeros en la superficie, se ve el interior de la pieza y
el modelo parece roto — justo lo contrario de lo que tiene que transmitir la web.
Ahora entra la malla entera y se dibuja así:

1. **Vértices únicos**: los tres vértices de cada triángulo se funden con los de
   sus vecinos, que es lo que permite promediar normales.
2. **Normales suavizadas con arista viva**: la normal de cada vértice es la media
   de las caras que lo tocan, pesada por área. Cuando una cara se aparta más de
   unos 57° de esa media, el vértice se **duplica** con la normal de su cara: así
   una esfera sale lisa pero un chaflán sigue siendo un chaflán.
3. **Rasterizador con z-buffer** escrito a mano sobre un `ImageData`: cada píxel
   se queda con el triángulo más cercano. No hay que ordenar caras, no se cuela
   nada por dentro y no quedan costuras entre triángulos. Se descartan antes las
   caras que miran hacia atrás, que es la mitad del trabajo.
4. **Luz**: clave + relleno + un realce de silueta para despegarla del fondo, más
   un brillo especular corto. El sombreado se interpola entre los tres vértices
   (Gouraud), así que no se ven las facetas.
5. Encima, las líneas de capa a un 5 % de intensidad. Ahí sí interesa que se
   note: es una pieza impresa, no un render de catálogo.

Se dibuja a doble resolución y se escala a la mitad en pantalla, que hace de
antialiasing. Mientras arrastras baja a resolución simple y vuelve a la buena al
soltar.

**Archivos grandes**: por encima de 200.000 triángulos no se tiran triángulos —
se **agrupan vértices por rejilla**, que baja la cuenta sin abrir la superficie.
Probado con una esfera de 577.600 triángulos (28 MB): la lee en 1,2 s, la dibuja
sin un solo agujero y gira a unos 30 ms por fotograma. El volumen y las medidas
se miden siempre sobre la malla original, no sobre la simplificada.

STEP y 3MF se aceptan en el selector pero no se miden aquí: para esos el aviso
dice que se revisan a mano. Un STEP es geometría paramétrica, no una malla, y
medirlo pide un kernel CAD completo.

Verificado con un cubo de 40 mm generado a propósito: lo lee como 64 cm³ exactos,
40 × 40 × 40 mm y 12 triángulos.

## Las fotos del Venom vienen del pack de Do3D

El modelo del Venom se compra a **Do3D** y el pack incluye sus renders de
producto, con licencia. `do3d.py` hace una sola cosa: la marca del estudio va
sobre negro plano, así que se localiza por luminancia en un recuadro pequeño de
la esquina —72 × 120 px, ni uno más, para no rozar la pieza— y se rellena por
inpainting. El resto se queda como viene.

Hubo una versión que les subía la resolución, les metía contraluz de color y
oscurecía la piel del maniquí. Fuera: el render del pack ya está iluminado por
quien diseñó la pieza, y retocarlo solo lo alejaba de lo que el cliente recibe.
Si algún día hace falta, está en el historial.

Salida a 560 × 560, que es el tamaño de origen, JPEG 92, unos 60 KB cada una.
En la ficha aparece el distintivo *«Modelo de Do3D, impreso bajo licencia
comercial»*, que es tanto la atribución como el argumento de venta.

## Tratamiento de las fotos

`extract.py` **recorta la pieza del fondo** y la monta sobre fondo de estudio.
Sin modelos de IA, porque este entorno no tiene acceso de red a los pesos
(HuggingFace y GitHub bloqueados), así que va con visión clásica:

1. recorta la interfaz del móvil buscando la franja que no es color plano;
2. estima el fondo por las esquinas y umbraliza la distancia en espacio LAB con
   Otsu, invirtiendo la máscara si lo marcado ocupa casi todo el marco;
3. una **apertura por reconstrucción** se come el brazo y la mano, que son más
   estrechos que la pieza, y deja solo el casco;
4. GrabCut afina el borde y se rellenan los huecos;
5. compone sobre el `--paper` del sitio con una sombra de contacto y encuadre
   cuadrado idéntico en todas. Salida 1000 × 1000, JPEG 82.

**Tres fotos se descartaron** porque el recorte arrastraba fondo: una del Venom y
dos del Ranger. Están listadas en el `SETS` del script.

La vía buena para las siguientes: recortar en el móvil (mantener pulsado sobre la
pieza → copiar sujeto) y pasar el PNG con transparencia. El compositor de
`extract.py` sirve igual y el borde sale perfecto.

`normalize.py` queda como alternativa: no recorta, solo uniforma encuadre y luz.

**Los precios me los he inventado** — hacen falta los tuyos. Están en el campo
`p` de cada entrada de `REAL`, y los multiplicadores en `opts`.

Cada producto declara sus propias opciones: un casco no se vende por «material y
talla» como un portalápices, se vende por acabado, que es donde está el trabajo.
Las piezas de catálogo siguen usando material y talla por defecto.

Los 12 productos generados en 3D siguen ahí marcados con la etiqueta **Ejemplo**,
para que el catálogo no se vea vacío mientras llegan los tuyos. Se borran
quitando `DEMO` de la línea `const PRODUCTS=REAL.concat(DEMO);`.

## Autoría de los modelos

Cada producto tiene un campo `designer`. Cuando está relleno, la ficha muestra
un distintivo: *«Modelo de X, impreso bajo licencia comercial»*. Es un argumento
de venta frente a quien vende lo mismo con archivos pirateados, y hay una
pregunta frecuente que lo explica.

El Batman es de **Yosh Studios** y el Venom de **Do3D**. Falta el del Ranger — el
campo está puesto y vacío.

## Lo que tienes que cambiar

Todo el contenido es **de ejemplo**, porque no pude ver tu Instagram: el proxy de
red de este entorno bloquea instagram.com y la cuenta no aparece indexada en
buscadores. Está todo junto en las constantes del principio del `<script>`:

| Constante | Qué es |
|---|---|
| `PRODUCTS` | las 12 piezas: nombre, categoría, precio, descripción, medidas, peso, colores y su malla |
| `MATS` | materiales, densidad y precio por gramo |
| `COLORS` | la carta de colores de filamento |
| `SIZES` | las tallas y su factor de escala |
| `FAQS` | las preguntas frecuentes |
| `SETUP`, `HOUR` | tus costes para el presupuesto a medida |
| `MAXMM` | el lado máximo que entra en tu cama (ahora 250 mm) |

Además hay un número de WhatsApp de relleno (`34600000000`) en tres sitios, y las
medidas del hero (volumen máximo, alturas de capa, plazos) están en el marcado.

## Siguiente paso natural

Cuando tengas fotos reales, la ficha puede mostrar **foto y render 3D** a la vez:
la foto para la confianza, el 3D para ver el color elegido. El renderizador ya
está montado para eso.
