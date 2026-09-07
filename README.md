# Full Padel Club — web interactiva

Rediseño interactivo de la web del **Full Padel Club** (La Pobla de Vallbona, València)
en un único archivo: `index.html`. Sin dependencias, sin build, sin backend.
Solo Google Fonts como recurso externo.

## Cómo usarlo

Abre `index.html` en el navegador, o sírvelo con cualquier servidor estático:

```bash
python3 -m http.server 8000   # http://localhost:8000
```

## Funcionalidades

**Del sitio original, conservadas**
- Presentación del club, instalaciones y servicios
- Reservas de pista
- Escuela de pádel por niveles
- Torneos: SNP 2025|2026, Full Pro Series FIP, Full Padel Fest
- Cafetería, contacto, ubicación, Instagram, WhatsApp
- Versión en inglés

**Scripts añadidos**
| Módulo | Qué hace |
|---|---|
| Motor de reservas | 14 días × 7 pistas × turnos de 60/90/120 min entre 08:00 y 23:30. Tarifa PRIME automática (18–22 h y fines de semana), descuento de socio y de alumno, carrito de hasta 6 reservas persistido en `localStorage` y confirmación por WhatsApp con el resumen ya escrito. |
| Plano de la nave | SVG interactivo fiel a la distribución real: pistas 5-4-3-2-1 en la fila superior, aseos de mujeres y hombres a la derecha, y pistas 6 y 7 en horizontal abajo junto a la cafetería. Cada pista muestra su red y sus líneas de saque a escala, con estado libre/ocupada, acceso por teclado y salto directo a la reserva. |
| Marcador de pádel | Puntuación real 15/30/40, ventajas **o punto de oro**, tie-break a 7, rotación de saque, sets al mejor de 3, deshacer, historial del partido, atajos `A`/`L`/`Z` y copia del resultado. |
| Generador de torneo | Torneo rotatorio: cambian parejas y rivales cada ronda, reparto por pistas, descansos (BYE) automáticos y cuadro copiable al portapapeles. |
| Pizarra táctica | Pista a escala real (20 × 10 m) con cinco jugadas animadas paso a paso —saque y subida, globo y contraataque, bandeja, salida de pared y remate x3—, fichas arrastrables y modo lápiz para dibujar trayectorias. |
| Selector de pala | Cinco preguntas (nivel, estilo, fuerza, molestias de codo, frecuencia) que devuelven forma, balance, peso, dureza de goma y tipo de cara, con las tres formas dibujadas y la recomendada resaltada. |
| Test de nivel | 6 preguntas de pádel real (bandeja, salida de pared, saque y subida) que devuelven nivel 1–5 y enlazan con el grupo de la escuela correspondiente. |
| Ranking del club | Tabla ordenable por cualquier columna, buscador y filtro por categoría, con racha de forma. |
| Busco pareja | Publicación de anuncios con nivel y franja horaria, filtro y contacto por WhatsApp. |
| Cafetería | Carta filtrable con contador por plato y total en vivo. |
| Cuenta atrás | Temporizador en directo al torneo seleccionado, con ocupación de plazas. |
| Idioma ES/EN | Traducción completa en cliente, sin recargar, recordada entre visitas. |
| Tema claro/oscuro | Respeta `prefers-color-scheme` y recuerda la elección. |
| Hero en canvas | Bolas de pádel con física simple que huyen del cursor, sobre las líneas de una pista. |
| Extras | Barra de progreso, nav con sección activa, animaciones al hacer scroll, contadores, carrusel con swipe, acordeón FAQ, validación de formularios, modales, avisos, banner de cookies e indicador de "abierto ahora". |

## Accesibilidad y rendimiento

- Navegación completa por teclado (plano de pistas, eventos y galería incluidos), `aria-*` en controles y `:focus-visible` visible.
- `prefers-reduced-motion` desactiva el canvas animado y las transiciones.
- `localStorage` envuelto en `try/catch`: la web funciona en incógnito o con cookies bloqueadas.
- Sin imágenes externas: todo el apartado gráfico es SVG y CSS.

## Marca

El logotipo está reconstruido como **SVG vectorial** dentro del propio archivo
(símbolos `#fpcFigure` y `#fpcLockup`, al principio del `<body>`): tile negro
`#14181a`, figura y tipografía en el lima corporativo `#c8e832`, wordmark
*FullPadel* + `CLUB`. Ese lima es el token `--ball` de toda la paleta, así que
botones, acentos y gráficos van a juego.

Si quieres usar el archivo original en vez de la reconstrucción, deja el
`logo.svg` (o `.png`) junto al `index.html` y sustituye el `<use href="#fpcLockup"/>`
del pie por `<img src="logo.svg" alt="Full Padel Club">`; el resto del sitio no
necesita cambios.

## Nota sobre los datos

Precios, horarios de clases, ranking, carta y disponibilidad son **datos de ejemplo**
definidos en las constantes del principio del `<script>` (`CLUB`, `COURTS`, `CLASSES`,
`EVENTS`, `RANKING`, `MENU`, `TESTIMONIALS`, `FAQS`). Sustitúyelos por los reales del
club y toda la web se actualiza sola. Los datos de contacto (dirección, teléfono,
horario 08:00–23:30, Instagram) sí son los públicos del club.
