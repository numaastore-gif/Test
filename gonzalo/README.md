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

Y los diez productos con su precio, IVA del 10 % incluido:

| Producto | Precio |
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

**Lo que no es dato, es invento y hay que revisarlo**: las descripciones de cada
producto, el reparto en las dos categorías (en la tienda real hay tres: «Las
bolas de Gonzalo», «Bolas y albacaos» y «Productos en unidades»), las preguntas
frecuentes, los cuatro pasos del obrador y el mínimo de 12 unidades para cerrar
caja. Nada de eso lo he podido comprobar.

## Sin fotos: todo está dibujado

No hay ni una imagen en el archivo. Cada producto se dibuja en canvas con su
baño, su brillo y su relleno, a partir de cuatro colores en los datos: `masa`,
`bano`, `relleno` y `veta`. Eso permite tener los diez productos sin sesión de
fotos y que el catálogo se vea de una pieza.

**El mordisco** no es un círculo pintado encima —eso parecía un ojo—: se le
quita el trozo a la silueta con `destination-out` y por el hueco se pintan el
canto de la masa y el relleno, recortados contra la bola para que nada se salga.

## Los scripts de chocolate

| Script | Qué hace |
|---|---|
| **El chorro** | Gotas con gravedad que caen desde cuatro puntos, se acumulan en un charco y hacen olas. Para que parezca líquido y no una lluvia de bolitas, se dibujan en un lienzo aparte y se componen con `blur(9px) contrast(22)`: las manchas que se tocan se funden en una sola. Encima, un filo de luz para que sea chocolate y no barro. |
| **El corte** | Lo que sale en los vídeos. Arrastras por encima y, pasado un umbral, la bola se abre: cada mitad es una cúpula más la cara del corte, que se dibuja como media elipse pegada al canto recto y se ensancha conforme se separan. Dentro, masa con sus alveolos, el relleno y un chorretón que escurre. |
| **Las gotas** | El relleno cae de verdad: cada gota lleva su velocidad y su gravedad, y al tocar el plato engorda la columna del charco donde cayó, repartiendo algo a los lados. El marcador cuenta cuántas han caído. |
| **El goteo del hero** | El borde inferior del hero es un `path` SVG generado al cargar con gotas de ancho y largo aleatorios, así que no hay dos cargas iguales. |
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

1. **Las fotos reales** de los productos. Los dibujos aguantan, pero una foto de
   una bola abierta vende más que cualquier script.
2. **Revisar las descripciones** y las categorías contra la tienda real.
3. **Alérgenos de verdad** por producto. Lo que hay ahora es genérico y en
   comida eso no vale.
4. **Condiciones de envío**: zonas, plazos y coste. Ahora mismo la web dice que
   se cierran con el obrador, que es lo único que puedo afirmar.
5. Teléfono, si lo hay, y el enlace al carrito real si se mantiene WooCommerce.
