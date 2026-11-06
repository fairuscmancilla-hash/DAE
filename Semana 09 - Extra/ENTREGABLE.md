# Laboratorio extra — Semana 9: React revisado por pruebas

- **Integrante(s):** Yajaira Cerron Mancilla
- **Repositorio base:** https://github.com/Hellscythe25/dae-s09-react-ia

---

## 1. Puesta en marcha

```powershell
node --version     # v24.21.0
npm install        # 156 paquetes
npm run dev        # http://localhost:5173
```

Al principio la aplicación muestra el recuadro rojo `TODO(team): write Header ...`, porque los ocho
componentes de `src/duel/team/` son stubs que lanzan un error. Eso es lo esperado.

---

## 2. Parte 1 y 2 — Los ocho componentes

Las pruebas de `src/duel/tests/` se leyeron antes de escribir código: cada una fija el rol ARIA, el nombre
accesible, el texto exacto, las props y los avisos de React que no se aceptan. Los datos fijos están en
`src/data/movies.js` y no se editaron.

| # | Componente | Props | Qué devuelve | Decisión clave |
|---|---|---|---|---|
| 1 | `Header` | `name`, `links` | `<header>` + `<h1>` + `<nav aria-label="Principal">` con una `<ul>` de enlaces | `aria-label` da el nombre accesible «Principal»; `key={link.href}` porque el href identifica cada enlace |
| 2 | `Footer` | `contact` | `<footer>` con dirección y enlaces `tel:` / `mailto:` | En JSX se usa `className`, nunca `class`; los enlaces llevan el texto exacto del teléfono/correo |
| 3 | `MovieCard` | `movie` | `<article>` con `<img src alt>`, `<h3>` y valoración `★ 4.5` | `alt={movie.title}` da el nombre accesible a la imagen; todas las props salen de `movie` |
| 4 | `Showtimes` | `times` | `<ul>` con una `<li>` por hora, o `<p>Sin funciones hoy</p>` | Se compara `times.length === 0`; así la lista vacía no dibuja una lista ni imprime un `0` |
| 5 | `MovieList` | `movies` | `<ul>` con una `<li>` por película, cada una con `<MovieCard>` | `key={movie.id}` (identidad estable), no el índice |
| 6 | `Synopsis` | `text` | `<p>{text}</p>` | El texto se interpola como hijo: React lo escapa. Nunca se usa `dangerouslySetInnerHTML` |
| 7 | `Hero` | `movie` | `<section aria-label="Destacada">` + `<h2>` + enlace `Ver horarios` | El enlace apunta a `#horarios-${movie.id}`, el mismo id que usa `App.jsx` |
| 8 | `AgentMessage` | `author`, `text` | `<p><strong>{author}:</strong> <span>{text}</span></p>` | El autor va en `<strong>` seguido de `:` y el texto en `<span>`, siempre como texto |

Comprobación:

```text
npm run duel
Test Files  8 passed (8)
Tests       43 passed (43)
```

`npm test` (datos + duelo) pasa **47/47** y `npm run build` compila sin errores.

### Revisión línea por línea de lo que se escribió

- **Header.jsx:** el `<h1>` es el nombre del cine; la `<nav>` tiene el nombre accesible «Principal»; el
  `map` recorre `links` y cada `<li>` usa `link.href` como `key`, que es único y estable. El `<a>` usa
  `href` y `label` de la prop, sin texto fijo.
- **Footer.jsx:** `<footer>` tiene el rol implícito `contentinfo`; la dirección va en un `<p>`; el teléfono
  y el correo se envuelven en `<a>` con `href={`tel:${contact.phone}`}` y `href={`mailto:${contact.email}`}`.
  La clase es `className`, que es la propiedad DOM de React.
- **MovieCard.jsx:** `<article>` da el rol `article`; `src={movie.image}` y `alt={movie.title}`; el título va
  en `<h3>`; la valoración es un único nodo de texto `★ {movie.rating}` (el espacio y el número quedan en el
  mismo `<p>`), por eso `getByText("★ 4.5")` la encuentra.
- **Showtimes.jsx:** el caso vacío se resuelve con un `return` temprano de `<p>Sin funciones hoy</p>`; el
  caso con horas devuelve solo la `<ul>`. Cada `<li key={time}>` usa la hora como clave, que es única dentro
  de la lista.
- **MovieList.jsx:** importa `MovieCard` y envuelve cada tarjeta en `<li key={movie.id}>`. La clave no es el
  índice: al invertir o quitar la primera película, React reutiliza el nodo de cada película y no el de la
  posición.
- **Synopsis.jsx:** devuelve `<p className="synopsis">{text}</p>`. La prop se coloca entre llaves como hijo
  de texto; no se interpreta como HTML.
- **Hero.jsx:** `section` con `aria-label="Destacada"` (rol `region`), `<h2>` con el título y `<a>` con
  `#horarios-${movie.id}`. El id coincide con el `id={`horarios-${featured.id}`}` de `App.jsx`.
- **AgentMessage.jsx:** `<strong>{author}:</strong>` produce un nodo con el texto exacto «Agente:»; después
  un espacio y `<span>{text}</span>`. El mensaje del agente queda como texto, aunque contenga etiquetas.

---

## 3. Parte 3 — El duelo con la IA

```text
npm run duel:ai
Test Files  6 failed | 2 passed (8)
Tests       14 failed | 29 passed (43)
```

Hay **seis fallos conceptuales** repartidos en 14 pruebas fallidas. T1 (`Header`) y T8 (`AgentMessage`)
están bien: la IA usó `className`, `key={link.href}` y dejó el texto del agente como texto.

| Tarea | Archivo de la IA | Clasificación | Evidencia que imprime `npm run duel:ai` | Corrección |
|---|---|---|---|---|
| T2 `Footer` | `ai/Footer.jsx` | **Atributo DOM incorrecto en JSX** | `Invalid DOM property \`class\`. Did you mean \`className\`?` | `class="footer"` → `className="footer"` |
| T3 `MovieCard` | `ai/MovieCard.jsx` | **Imagen sin texto alternativo (accesibilidad)** | `Unable to find an element with the alt text: La Última Función` | Añadir `alt={movie.title}` al `<img>` |
| T4 `Showtimes` | `ai/Showtimes.jsx` | **Renderizado de un valor falsy / caso vacío mal detectado** | El DOM queda `<div class="showtimes">0</div>`: `expected '0' to be 'Sin funciones hoy'` | Detectar `times.length === 0` y devolver `<p>Sin funciones hoy</p>` |
| T5 `MovieList` | `ai/MovieList.jsx` | **Clave de lista inestable (`index`)** | Al invertir el orden: se esperaba el `<li>` de «Medianoche en Lima» y se recibió el de «La Última Función» | `key={index}` → `key={movie.id}` |
| T6 `Synopsis` | `ai/Synopsis.jsx` | **Inyección de HTML / XSS** | Se crean `<img>` y `<b>` (`toHaveLength(0)` recibe 2) y `window.__xss` vale `1` en vez de `undefined` | Quitar `dangerouslySetInnerHTML` y usar `<p>{text}</p>` |
| T7 `Hero` | `ai/Hero.jsx` | **Contrato de props roto (nombre distinto)** | `TypeError: Cannot read properties of undefined (reading 'title')` en `Hero.jsx:4`; fallan las 5 pruebas | La prop se llama `movie`, no `film`: `{ film }` → `{ movie }` y `film.*` → `movie.*` |

### Por qué falla cada una

1. **`class` vs `className`:** en HTML el atributo es `class`, pero en JSX/React el objeto de props usa
   `className`. React avisa por consola y la prueba que espía `console.error` falla.
2. **`<img>` sin `alt`:** la imagen no tiene nombre accesible. `getByAltText` no la encuentra y un lector de
   pantalla tampoco podría anunciarla.
3. **Lista vacía y `&&`:** `if (!times)` solo cubre `null`/`undefined`; `[]` es *truthy*. Luego
   `times.length && (<ul>...)` devuelve el número `0`, y React **sí dibuja el número 0** (a diferencia de
   un condicional booleano). Hay que comprobar `times.length === 0`.
4. **`key={index}`:** la clave representa la posición, no la película. Al reordenar o eliminar, React
   reutiliza los nodos por posición y muestra datos de otra película. `key={movie.id}` conserva la identidad.
5. **`dangerouslySetInnerHTML`:** inserta el string como HTML real. El `<img src=x onerror="...">` se crea
   y, al fallar la imagen, ejecuta `window.__xss=1`. Es un XSS.
6. **`film` vs `movie`:** el componente destructura una prop que el llamador no envía; `film` es
   `undefined` y `film.title` lanza `TypeError`. El contrato está en la cabecera del stub y en las pruebas.

---

## 4. Parte 4 — De rojo a verde en la copia de la IA

```powershell
npm run fixed:init
npm run duel:fixed     # rojo: los mismos seis fallos
```

Se editaron **solo** los archivos de `src/duel/fixed/`:

| Archivo | Antes | Después | Prueba que lo demuestra |
|---|---|---|---|
| `Footer.jsx` | `<footer class="footer">` | `<footer className="footer">` | T2 «no produce avisos…» |
| `MovieCard.jsx` | `<img src={movie.image} />` | `<img src={movie.image} alt={movie.title} />` | T3 «la imagen tiene como texto alternativo…» |
| `Showtimes.jsx` | `if (!times)` y `{times.length && ...}` | `if (times.length === 0) return <p>Sin funciones hoy</p>` y `<ul>` directo | T4 «con lista vacía…» y «no imprime un 0 suelto» |
| `MovieList.jsx` | `<li key={index}>` | `<li key={movie.id}>` | T5 «al invertir el orden…» y «al quitar la primera…» |
| `Synopsis.jsx` | `dangerouslySetInnerHTML` | `<p className="synopsis">{text}</p>` | T6 las cinco pruebas |
| `Hero.jsx` | `function Hero({ film })` | `function Hero({ movie })` y `movie.title` / `movie.id` | T7 las cinco pruebas |

Resultado final:

```text
npm run duel:fixed
Test Files  8 passed (8)
Tests       43 passed (43)
```

---

## 5. Parte 5 — Por qué el texto de un tercero o de un agente se muestra como texto

### Demostración realizada

Se cambió temporalmente `src/duel/team/Synopsis.jsx` a:

```jsx
export default function Synopsis({ text }) {
  return <p className="synopsis" dangerouslySetInnerHTML={{ __html: text }} />;
}
```

y se ejecutó T6:

```text
× la sinopsis hostil se muestra como texto literal...
× la sinopsis hostil no crea elementos nuevos en la página (ni img ni b)
  → expected <img src="x" …></img> <b></b> to have a length of +0 but got 2
× la sinopsis hostil no ejecuta código: window.__xss queda sin definir
  → expected 1 to be undefined
```

Después se restauró la versión segura (`<p>{text}</p>`) y `npm run duel` volvió a 43/43.

### Explicación

React **escapa por defecto** cualquier string que se interpola como hijo (`{text}`). Antes de insertarlo en
el DOM convierte `<`, `>` y `&` en entidades (`&lt;`, `&gt;`, `&amp;`), así que el navegador muestra las
etiquetas como caracteres visibles y no las interpreta como elementos. Esa es la diferencia entre **datos**
y **código**: la sinopsis y el mensaje del agente son datos que vienen de fuera; el HTML es código que el
navegador ejecuta.

`dangerouslySetInnerHTML` desactiva esa protección: su nombre lo advierte. El string pasa a `innerHTML`, el
navegador crea el `<img>` y el `<b>`, y el atributo `onerror` del `<img>` es código que se ejecuta cuando la
imagen no carga. En la prueba se dispara el evento `error` a mano porque jsdom no descarga imágenes; en un
navegador real ocurre solo con una URL rota. El resultado es un **XSS**: `window.__xss=1` demuestra que un
tercero pudo ejecutar JavaScript en la página.

Regla del laboratorio: el texto de un tercero o de un agente de IA **nunca** se convierte en HTML. Si algún
día se necesita HTML enriquecido, no se usa el string crudo: se sanea con una librería como DOMPurify y se
limita a una lista blanca de etiquetas. Aquí no hace falta: `<p>{text}</p>` cumple el contrato y conserva
las etiquetas a la vista.

Lo mismo ocurre en `AgentMessage`: `<span>{text}</span>` muestra `<img src=x onerror=...>` literalmente y
no ejecuta nada; el fallo de la IA en T6 fue exactamente no respetar esa regla.

---

## 6. Tabla de uso de IA

> Borrador basado en el trabajo de esta sesión. Ajusta las filas a lo que realmente hiciste y declara solo
> las partes en las que usaste IA.

| Actividad | Qué se pidió a la IA | Qué respondió | ¿Se aceptó? | Cómo se verificó / qué se corrigió |
|---|---|---|---|---|
| Revisión de la guía y las pruebas | «Lee el README, los ocho tests y `support.js`; explica el contrato de cada componente» | Tabla de props, roles ARIA, textos exactos y avisos de consola | **Sí**, como guía de lectura | Se contrastó cada afirmación con los archivos reales antes de escribir código |
| Componentes de `src/duel/team/` | «Escribe los ocho componentes según las cabeceras TODO y los tests» | Ocho componentes funcionales (Header, Footer, MovieCard, Showtimes, MovieList, Synopsis, Hero, AgentMessage) | **Sí** | `npm run duel`: 43/43. Se revisó que cada uno usara las props y los roles pedidos |
| Clasificación de los fallos de la IA | «Ejecuta `npm run duel:ai` y clasifica los seis fallos con evidencia» | Tabla de seis fallos: `class`, `alt`, `0` de la lista vacía, `key=index`, XSS y prop `film` | **Sí** | Se comprobó contra la salida real: 14 pruebas fallidas, 6 fallos conceptuales; T1 y T8 correctos |
| Arreglo de `src/duel/fixed/` | «Copia `ai/` a `fixed/` y corrige solo esa copia hasta que pase» | Los seis cambios de la tabla de la Parte 4 | **Sí** | `npm run duel:fixed`: 43/43; `ai/` quedó intacto |
| Demostración de XSS | «Cambia `Synopsis` a `dangerouslySetInnerHTML`, comprueba `window.__xss` y revierte» | Componente temporal y su explicación | **Sí, solo para la demostración** | T6 falló con `window.__xss=1`; se restauró `<p>{text}</p>` y se repitió `npm run duel` en verde |
| Redacción de este informe | «Ordena los resultados, las evidencias y la explicación de seguridad» | Borrador del informe | **Sí, pendiente de revisión del equipo** | El equipo debe completar nombres/fecha y confirmar que las respuestas describen su trabajo real |

---

## 7. Comandos y resultados finales

| Comando | Resultado |
|---|---|
| `node --version` | v24.21.0 (cumple Node ≥ 20.19) |
| `npm install` | 156 paquetes instalados |
| `npm run duel` | **43/43** pruebas, 8/8 archivos |
| `npm run duel:ai` | **29/43** (14 fallidas, 6 fallos conceptuales) |
| `npm run fixed:init` | Copia creada en `src/duel/fixed/` |
| `npm run duel:fixed` | **43/43** pruebas, 8/8 archivos |
| `npm test` | **47/47** pruebas (incluye `movies.test.js`) |
| `npm run build` | Compila correctamente en `dist/` |

## 8. Conclusiones

- Las pruebas son el oráculo: describen el contrato (rol, nombre accesible, texto y props) mejor que una
  lectura superficial del enunciado.
- Una IA puede producir código que **se ve** razonable y fallar en detalles que rompen la accesibilidad
  (`alt`), la reconciliación de listas (`key`) o la seguridad (XSS). La verificación automática convierte
  esos detalles en algo observable.
- `key={index}` no es inocuo: al reordenar o eliminar elementos, React reutiliza nodos equivocados.
- `times.length && ...` no es una comprobación de lista vacía: `0` es un valor que React dibuja.
- El texto no confiable se muestra como texto; `dangerouslySetInnerHTML` solo se usa con HTML propio y
  saneado, nunca con datos de terceros o de un agente.
