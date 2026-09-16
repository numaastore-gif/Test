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
| Máscara Venom / Spider-Man | 40 € | 96 € | 4 |
| Casco de Power Ranger amarillo | 55 € | 132 € | 3 |

Los tres comparten el mismo escalón de acabado, que es como se vende de verdad
una pieza impresa: **raw** ×1 (sin postprocesar, con las capas a la vista),
**lijado e imprimado** ×1,55 (listo para pintar) y **pintado a mano** ×2,40. El
precio base de cada producto es el del raw; la tarjeta enseña el rango completo
y la ficha abre en el acabado de las fotos.

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

Ahora mismo solo el Batman lo tiene (**Yosh Studios**). Falta saber de quién son
los modelos del Venom y del Ranger — el campo está puesto y vacío.

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
