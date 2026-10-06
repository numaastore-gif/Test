# Gonzalo el de las bolas

Página para **gonzaloeldelasbolas.com**, el obrador de Gonzalo Díaz Alba en
Coria del Río. Un solo archivo (`index.html`), sin build, sin backend y sin
dependencias: solo Google Fonts.

## De dónde salen los datos

**El proxy de red de este entorno bloquea `gonzaloeldelasbolas.com`**, así que
no pude abrir la tienda ni descargar una sola foto. Todo lo que hay aquí sale
de lo que devuelve el buscador sobre ese dominio:

| Dato | Valor |
|---|---|
| Obrador | Polígono La Estrella, C/ Pintor 8, 41100 Coria del Río, Sevilla |
| Correo | productosalba@productosalba.es |
| Horario | Lunes a jueves 10:00–17:00; viernes, sábado y domingo cerrado |
| Redes | @gonzaloeldelasbolas en Instagram y TikTok |
| Tradición | desde 1992 |

Y los productos. Doce encontrados, diez con precio:

| Producto | Precio (sin IVA) |
|---|---|
| Bolas sabor Kinder | 1,70 € |
| Bolas doble chocolate | 1,70 € |
| Bolas chocolate blanco | 1,60 € |
| Bolas con crema de vainilla y recubrimiento de chocolate | 1,70 € |
| Bolas de cacao y azúcar | 1,50 € |
| Bolas de pistacho | 2,23 € |
| Albacao Bombón Choco-Choco | 1,70 € |
| Albacao con crema de cacao | 1,50 € |
| Albacao relleno de chocolate blanco | 1,60 € |
| Albacao de pistacho | 2,10 € |
| Albacao sabor Kinder | sin confirmar |
| Cañón de chocolate relleno de crema de cacao | sin confirmar |

De las *Bolas de cacao y azúcar* sí está publicada la lista de ingredientes
completa, y está puesta tal cual en la sección de alérgenos.

**El IVA va aparte.** Las dos referencias que dan el detalle lo escriben como
«2,10 € + 10 % IVA», así que la web muestra el precio sin IVA y lo suma en el
resumen. Hay una fuente que decía lo contrario; es de las primeras cosas a
confirmar.

**Lo que sigue sin comprobar**: si faltan más productos (la tienda tiene una
categoría «Productos en unidades» que no he podido abrir), el reparto real en
sus tres categorías —«Las bolas de Gonzalo», «Bolas y albacaos» y «Productos en
unidades»—, las descripciones cortas, las preguntas frecuentes, los cuatro
pasos del obrador y el mínimo de 12 unidades por caja.

## Sin fotos: todo está dibujado

No hay ni una imagen en el archivo. Cada producto se dibuja en canvas con su
baño, su brillo y su relleno, a partir de cuatro colores en los datos: `masa`,
`bano`, `relleno` y `veta`. Eso permite tener los diez productos sin sesión de
fotos y que el catálogo se vea de una pieza.

**El mordisco** no es un círculo pintado encima —eso parecía un ojo—: se le
quita el trozo a la silueta con `destination-out` y por el hueco se pintan el
canto de la masa y el relleno, recortados contra la bola para que nada se salga.

## Los scripts

El chorro de chocolate del hero —gotas cayendo a un charco, fundidas con
`blur` y `contrast` para que parecieran líquido— se quitó: no gustó. El hero se
queda con una luz cálida quieta y la bola girando.


| Script | Qué hace |
|---|---|
| **El corte** | Lo que sale en los vídeos. Arrastras por encima y, pasado un umbral, la bola se abre: cada mitad es una cúpula más la cara del corte, que se dibuja como media elipse pegada al canto recto y se ensancha conforme se separan. Dentro, masa con sus alveolos, el relleno y un chorretón que escurre. |
| **Las gotas** | El relleno cae de verdad: cada gota lleva su velocidad y su gravedad, y al tocar el plato engorda la columna del charco donde cayó, repartiendo algo a los lados. El marcador cuenta cuántas han caído. |
| **El goteo del hero** | El borde inferior del hero es un `path` SVG generado al cargar con gotas de ancho y largo aleatorios, así que no hay dos cargas iguales. |
| **El cañón** | Se dibuja más alto que ancho, y el albacao más ancho que alto, para que las tres familias se distingan de un vistazo. |
| **La bola del hero** | Gira sola, se puede arrastrar con inercia y va cambiando de sabor cada cinco segundos. |

## Lo demás

- **Tienda** con filtro por categoría, buscador y cuatro órdenes. Al pulsar una
  tarjeta se añade a la caja.
- **Monta tu caja**: cantidades por sabor, subtotales, base imponible, IVA
  desglosado y total. Barra de progreso hasta las 12 unidades. El pedido se
  genera como texto para copiar o mandar por correo, con el asunto y el cuerpo
  ya rellenos.
- **Panel lateral** de pedido, persistente en el navegador.
- Tema claro y oscuro, barra de progreso de lectura, entradas al hacer scroll y
  respeto por `prefers-reduced-motion`.

Sobre el chocolate oscuro el texto va con `--sobre`, un claro fijo: `--crema`
gira con el tema y en modo oscuro dejaba texto oscuro sobre fondo oscuro.

## Lo que hace falta para publicarla

1. **Desbloquear el dominio** en la configuración de red del entorno. Sin eso
   no se puede leer su tienda entera ni bajar una sola foto, y lo que hay aquí
   seguirá siendo lo que devuelve el buscador.
2. **Las fotos reales** de los productos. Los dibujos aguantan, pero una foto de
   una bola abierta vende más que cualquier script.
3. **Revisar las descripciones** y las categorías contra la tienda real.
4. **Alérgenos del resto de sabores**. Solo uno los tiene publicados.
4. **Condiciones de envío**: zonas, plazos y coste. Ahora mismo la web dice que
   se cierran con el obrador, que es lo único que puedo afirmar.
5. Teléfono, si lo hay, y el enlace al carrito real si se mantiene WooCommerce.
