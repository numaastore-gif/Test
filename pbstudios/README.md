# PB Studios — tienda de impresión 3D

Primer ejemplo de tienda para **@_PBStudios**. Un solo archivo (`index.html`),
sin build, sin backend y sin dependencias: solo Google Fonts.

## La idea

Un cliente entra, ve las piezas, las gira en 3D, elige material, color y tamaño,
ve el precio cambiar y cierra el pedido por Instagram. Y si lo que quiere no está
en el catálogo, se calcula él mismo el presupuesto de su pieza.

## Sin fotos: las piezas se dibujan en 3D

No hay ni una imagen en el sitio. Cada producto es una **malla generada por
código y renderizada en canvas**: se rota, se proyecta en perspectiva, se ordenan
las caras de atrás hacia delante y se iluminan con luz plana. Encima se pintan
las **líneas de capa**, que es lo que delata una pieza impresa de verdad.

Eso resuelve tres cosas de golpe: no hace falta sesión de fotos para lanzar la
web, el color del producto cambia en vivo al elegirlo, y el cliente puede girar
la pieza para verla por detrás.

Generadores de malla disponibles en el código: `lathe` (revolución, con torsión
opcional), `prism`, `box`, `gear`, `torus` y `merge` para combinarlos.

## Qué hace

| Módulo | Detalle |
|---|---|
| **Catálogo** | 12 piezas con filtro por categoría, buscador y orden por ventas, precio o novedad. Cada tarjeta lleva su render 3D. |
| **Ficha de producto** | Visor 3D que gira solo y se puede arrastrar. Color, material y tamaño cambian el render, el peso, el tiempo de impresión y el precio al momento. |
| **Carrito** | Panel lateral, persistente en el navegador. El pedido se genera como texto listo para mandar por Instagram o WhatsApp. |
| **Presupuesto a medida** | Metes medidas, material, relleno, acabado y unidades, y calcula gramos, horas de máquina y precio **con el desglose a la vista**. Descuento automático por tanda a partir de 10 unidades. |
| **Materiales** | PLA, PLA Silk, PETG y TPU, cada uno con para qué sirve, densidad y precio por gramo. |
| **Resto** | Cómo funciona en cuatro pasos, preguntas frecuentes, contacto, tema claro/oscuro y barra de progreso. |

## Cómo se calcula el precio

- **Catálogo:** `precio base × (0,35 + 0,65 × escala³) × (1 + (coste material − 1) × 0,45)`.
  En PLA y talla M da exactamente el precio anunciado en la tarjeta.
- **A medida:** del volumen de la caja que ocupa la pieza se estima el material
  real (paredes + relleno), de ahí los gramos, y de los gramos las horas. Precio =
  preparación + material + máquina + postprocesado.

Las constantes están al principio del `<script>`: `SETUP` (preparación) y `HOUR`
(coste de máquina por hora).

## Productos reales ya cargados

Tres, con sus fotos incrustadas en el archivo como data URI (recortadas de las
capturas, sin la interfaz del móvil, a 820 px y JPEG: unos 900 KB en total):

| Producto | Raw | Pintado | Fotos |
|---|---|---|---|
| Casco de Batman | 65 € | 156 € | 3 |
| Máscara Venom / Spider-Man | 40 € | 96 € | 5 |
| Casco de Power Ranger amarillo | 55 € | 132 € | 5 |

Los tres comparten el mismo escalón de acabado, que es como se vende de verdad
una pieza impresa: **raw** ×1 (sin postprocesar, con las capas a la vista),
**lijado e imprimado** ×1,55 (listo para pintar) y **pintado a mano** ×2,40. El
precio base de cada producto es el del raw; la tarjeta enseña el rango completo
y la ficha abre en el acabado de las fotos.

## Tratamiento de las fotos

`normalize.py` (en el scratchpad de la sesión) lleva todas las fotos a la misma
estética: recorta la interfaz del móvil, detecta la pieza, encuadra en cuadrado
con el mismo aire alrededor, iguala luz y saturación, y sustituye el fondo por
uno de estudio construido desenfocando y aclarando la propia foto hacia un tono
común. Salida a 1000 × 1000 y JPEG de calidad 80.

Las fotos con **fondo oscuro se dejan sin tocar el fondo**: ahí la máscara no es
fiable y el remiendo se nota más que el problema.

**Los precios me los he inventado** — hacen falta los tuyos. Están en el campo
`p` de cada entrada de `REAL`, y los multiplicadores en `opts`.

Cada producto declara sus propias opciones: un casco no se vende por «material y
talla» como un portalápices, se vende por acabado, que es donde está el trabajo.
Las piezas de catálogo siguen usando material y talla por defecto.

Los 12 productos generados en 3D siguen ahí marcados con la etiqueta **Ejemplo**,
para que el catálogo no se vea vacío mientras llegan los tuyos. Se borran
quitando `DEMO` de la línea `const PRODUCTS=REAL.concat(DEMO);`.

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

Además hay un número de WhatsApp de relleno (`34600000000`) en tres sitios, y las
medidas del hero (volumen máximo, alturas de capa, plazos) están en el marcado.

## Siguiente paso natural

Cuando tengas fotos reales, la ficha puede mostrar **foto y render 3D** a la vez:
la foto para la confianza, el 3D para ver el color elegido. El renderizador ya
está montado para eso.
