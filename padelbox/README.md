# PADELBOX — club de pádel & fitness

Sitio completo de un club de pádel **inventado desde cero**, en un solo archivo
(`index.html`). Sin build, sin backend, sin dependencias: solo Google Fonts.

## El nombre

**Padelbox.** La pista de pádel es una caja de cristal y *box* es como se llama
al gimnasio donde se entrena de verdad: las dos mitades del club en una palabra.

## La marca

Logo vectorial dentro del propio archivo (símbolos `#mark` y `#lockup`, al
principio del `<body>`): una caja con **la esquina cortada** y la bola saliendo
de ella. Esa esquina cortada es el gesto que se repite en toda la web —botones,
eyebrows, el panel del hero y las líneas del canvas— y también da el favicon.

## Sistema visual

| Rol | Valor |
|---|---|
| Marca | violeta eléctrico `#5A31E8` |
| Acento | ámbar `#FFB020` |
| Fondo oscuro | berenjena `#161327` |
| Neutro claro | `#F5F4FA` (frío, con sesgo violeta) |
| Estado | verde `#17A673` · ámbar `#E8940B` · rojo `#E23D53` |

Los colores de estado son independientes de los de marca, así que «pista libre»
y «acento» nunca se confunden. Tema claro y oscuro completos, con los tres
estados (`prefers-color-scheme`, `data-theme="light"` y `data-theme="dark"`).

Tipografía en tres papeles: **Bricolage Grotesque** (display), **DM Sans**
(texto) y **JetBrains Mono** (datos, horas y precios, con `tabular-nums`).

## La nave

Plano SVG interactivo con **4 pistas** en línea, **vestuarios** de mujeres y
hombres a la derecha, **gimnasio de 560 m²** y **cafetería** en la fila
inferior. Cada pista dibuja su red y sus líneas de saque a escala (20 × 10 m) y
lleva su estado libre/ocupada; al tocar una zona se salta a su sección.

## Funcionalidades

| Módulo | Qué hace |
|---|---|
| **Panel «el club ahora»** | La página abre mostrando estado real, no un formulario vacío: pistas libres, aforo del gimnasio, próxima clase dirigida y si está abierto. Se refresca cada 30 s. |
| **Reservas unificadas** | Un solo motor para **pista y gimnasio**. Cambias de modo y las dos cosas caen en el mismo carrito y el mismo total: pista a las 19:00 y funcional a las 20:30 en una sola confirmación. Tarifa punta automática, descuento por abono y persistencia en `localStorage`. |
| **Calculadora de cuota** | Mueves partidos, días de gimnasio, clases y cómo repartís la pista, y calcula los cuatro planes en vivo, marca el más barato y **encuentra el punto de cruce**: a partir de cuántos partidos al mes cambia la recomendación. |
| **Aforo del gimnasio** | Curva hora a hora por día de la semana con codificación semántica del color, la hora actual resaltada y cálculo de la franja más vacía a partir de ahora. |
| **Marcador de pádel** | 15/30/40, punto de oro o ventajas, tie-break, sets, saque rotando, **cronómetro de partido** y **estadísticas** (puntos jugados, % ganados, juegos, puntos de oro). Acta copiable y atajos `A`/`L`/`Z`. |
| **Torneos** | Dos formatos: **liguilla rotatoria** (cambian parejas y rivales cada ronda, reparto por pistas, descansos automáticos) y **cuadro eliminatorio clicable**, con siembra 1-vs-último, BYE automáticos y avance de ganadores al pinchar. |
| **Plan semanal** | Reparte la semana entre pista, gimnasio y descanso según días libres y objetivo, respetando 48 h entre sesiones de fuerza del mismo grupo. Explica la regla que ha aplicado. |
| **Pizarra táctica** | Pista a escala con cinco jugadas animadas paso a paso, fichas y bola arrastrables y modo lápiz. |
| **Escuela, ranking, busco pareja, cafetería** | Filtros por nivel, tabla ordenable con buscador, tablón de anuncios persistente y carta con contador y pedido por WhatsApp. |
| **Transversal** | ES/EN completo en cliente, tema claro/oscuro, barra de progreso, sección activa, validación de formularios, modales, avisos y banner de cookies. |

## Accesibilidad y rendimiento

- Navegación por teclado en plano, pizarra y cuadro de torneo; `aria-*` en todos los controles; `:focus-visible` visible.
- `prefers-reduced-motion` apaga el canvas y las transiciones.
- `localStorage` envuelto en `try/catch`: funciona en incógnito.
- Sin imágenes externas: todo el apartado gráfico es SVG y canvas.

## Datos

Todo el contenido —tarifas, cuotas, horarios, aforos, clases, ranking y carta—
son **datos de ejemplo** de un club ficticio, definidos en las constantes del
principio del `<script>`: `CLUB`, `COURTS`, `ZONES`, `GYM`, `PLANS`, `CLASSES`,
`RANKING`, `MENU`, `FAQ_ES` / `FAQ_EN`. Cambiándolas se actualiza toda la web.
