# Laboratorio 11 - Comunicación entre componentes en ReactJS

**Curso:** Desarrollo de Aplicaciones Empresariales (DAE) · 4.º ciclo · 2026-2
**Actividad:** DAE - Lab11 - Comunicación entre componentes
**Alumna:** Yajaira
**Rama de trabajo:** `semana-11` (creada desde `main`)
**Repositorio:** https://github.com/fairuscmancilla-hash/DAE

---

## Puesta en marcha

```powershell
cd "Semana 11"
npm install
npm run dev        # http://localhost:5173
npm test           # 9 pruebas automatizadas
npm run build      # compilación de producción
```

La aplicación parte de la cartelera de la Semana 10 y añade: adaptador de datos, avisos con
Sonner, hooks propios, carrusel de estrenos con tres estados, contador elevado y limpieza de
filtros desde el banner.

---

## 1. Comunicación entre hermanos elevando el estado

**Título del desarrollo:** Estado de favoritas y filtros en el ancestro común.

**Captura:** `capturas/03-aviso-favorita.png` y `capturas/02-estrenos-con-datos.png`.

**Código (App.jsx):**

```jsx
const [favorites, setFavorites] = useState(readFavorites);
const [query, setQuery] = useState("");
const favoriteCount = favorites.length;

function toggleFavorite(id) {
  const movie = movies.find((item) => item.id === id);
  const wasFavorite = favorites.includes(id);
  setFavorites((current) =>
    wasFavorite ? current.filter((f) => f !== id) : [...current, id]
  );
  toast.success(wasFavorite ? "Quitada de favoritas" : "Agregada a favoritas", {
    description: movie?.title,
  });
}
```

**Explicación:** `Header`, `Hero` y `MovieList` son hermanos. El estado vive en `App`, que es
el ancestro común más cercano: `Header` recibe solo `favoriteCount`, `MovieCard` recibe
`isFavorite` y `onToggleFavorite`, y `Hero` recibe `hasFilters` y `onClearFilters`. Ningún
hermano guarda una copia del estado, por lo que el contador, las tarjetas y el filtro siempre
muestran el mismo valor. El aviso emergente también se decide en `App`, así la tarjeta solo
informa del clic y no sabe cómo se muestra el mensaje.

**Casos de prueba:**
- Marcar una película desde una tarjeta → contador `1` y aviso «Agregada a favoritas».
- Desmarcarla → contador `0` y aviso «Quitada de favoritas».
- Marcar desde el banner destacado → el mismo contador y el mismo aviso.
- Escribir en el buscador y pulsar «Limpiar filtros» en el banner → buscador y listado vuelven
  a su estado inicial.

---

## 2. Hooks propios extraídos

**Título del desarrollo:** `useDebounce`, `useWindowSize` y `usePremieres`.

**Captura:** `capturas/01-estado-carga.png`, `capturas/05-vista-movil.png` y
`capturas/06-estructura-proyecto.png`.

**Código (extracto):**

```jsx
// useDebounce.js
useEffect(() => {
  const timer = window.setTimeout(() => setDebouncedValue(value), delay);
  return () => window.clearTimeout(timer);
}, [value, delay]);

// useWindowSize.js
useEffect(() => {
  const handleResize = () => setSize(readSize());
  window.addEventListener("resize", handleResize);
  return () => window.removeEventListener("resize", handleResize);
}, []);

// usePremieres.js
const { status, premieres, error, retry } = usePremieres();
```

**Explicación:** antes el filtrado reaccionaba a cada pulsación; ahora `App` filtra con
`debouncedQuery` (300 ms). `useWindowSize` se extrajo porque **dos componentes comparten la
misma lógica**: `MovieList` decide entre 1 y 4 columnas y `PremieresCarousel` decide entre 1 y
3 tarjetas visibles. `usePremieres` concentra la simulación de petición con `requestRef` para
descartar respuestas obsoletas y expone `retry(shouldFail)` para probar el error. Los tres
hooks nombran con el prefijo `use`, no llaman a otros hooks dentro de bucles ni condicionales,
y limpian temporizadores y listeners en su efecto.

**Casos de prueba:**
- Mantener el valor anterior durante 299 ms y actualizarlo a los 300 ms (`useDebounce`).
- Redimensionar la ventana a 500 px → `width = 500` y una sola columna (`useWindowSize`).
- Carga → datos → error → recuperación con `retry(false)` (`usePremieres`).

---

## 3. Biblioteca de interfaz y estados de carga y error

**Título del desarrollo:** Avisos con Sonner, iconos con lucide-react y carrusel con tres estados.

**Captura:** `capturas/01-estado-carga.png`, `capturas/02-estrenos-con-datos.png` y
`capturas/04-estado-error.png`.

**Código (PremieresSection.jsx):**

```jsx
{status === "loading" && <PremieresSkeleton count={3} />}
{status === "error" && (
  <div className="premieres__error" role="alert">
    <TriangleAlert size={28} aria-hidden="true" />
    <p>{error?.message}</p>
    <Button onClick={() => retry(false)}>Reintentar</Button>
  </div>
)}
{status === "success" && <PremieresCarousel premieres={premieres} />}
```

**Explicación:** se integraron **Sonner** (un único `<Toaster />` montado en `App` y
`toast.success()` desde los manejadores de eventos) y **lucide-react** (iconos de corazón,
calendario, flechas, alerta y recarga). Mientras la petición simulada está en curso se muestra
un esqueleto con `aria-busy`; si falla, un panel con `role="alert"` explica el motivo y ofrece
reintentar; con datos se muestra el carrusel con scroll horizontal y control por teclado. El
botón «Simular error» permite verificar el tercer estado sin depender de la red.

**Casos de prueba:**
- Al entrar: mensaje «Cargando estrenos…» y tarjetas esqueleto.
- Tras 1,1 s: cuatro estrenos y flechas de navegación.
- Pulsar «Simular error»: panel rojo con «El servicio de estrenos no respondió».
- Pulsar «Reintentar»: vuelve al carrusel.

---

## 4. Entrega del repositorio con hooks y observaciones

**Título del desarrollo:** Historial por commit, pruebas y observaciones.

**Captura:** `capturas/06-estructura-proyecto.png`.

**Historial de la rama `semana-11`:**

| Commit | Contenido |
|---|---|
| `de181e1` | Proyecto base copiado de la Semana 10 y dependencias instaladas |
| `f7d51ae` | Tipografía y utilidades nuevas |
| `661918c` | Adaptador de datos y avisos con Sonner |
| `94bfbfc` | Hooks `useDebounce`, `useWindowSize` y `usePremieres` |
| `29a92ec` | Carrusel, estados de carga/error, contador y limpieza de filtros |
| `1b3be31` | 9 pruebas automatizadas con Vitest |

**Observaciones:**
- Se extrajo la lógica repetida de ancho de ventana en `useWindowSize`; la comparten
  `MovieList` y `PremieresCarousel`.
- `useDebounce` lo usa `App` para el buscador; `usePremieres` lo usa `PremieresSection`.
- El adaptador (`src/lib/movieAdapter.js`) lo consumen `App` (cartelera) y `usePremieres`
  (estrenos), de modo que los componentes nunca conocen los nombres del servicio externo.
- El estado de favoritas se persiste en `localStorage` con lectura y escritura defensivas.

**Casos de prueba automatizados (`npm test`): 3 archivos, 9 pruebas en verde** — adaptador,
los tres hooks y la comunicación `App` → `Header`/`MovieCard` junto a los tres estados de
estrenos.

---

## Árbol de componentes y dato que vive en cada nivel

```text
App  [favorites: number[], query: string, debouncedQuery: string,
      onlyFavorites: boolean, movies: Película[] adaptadas]
├── Header            [favoriteCount: number]  ← solo el contador, nunca la lista
├── Hero              [movie, isFavorite, hasFilters, callbacks]
├── SearchBar         [value: string, resultCount, totalCount]
├── MovieList         [movies filtradas, favorites, useWindowSize → columns]
│   └── MovieCard     [movie, isFavorite, onToggleFavorite]
├── PremieresSection  [status, premieres, error, retry (usePremieres)]
│   ├── PremieresSkeleton [count]
│   └── PremieresCarousel [premieres, useWindowSize → visibleColumns]
└── Toaster           [instancia única de Sonner]
```

### ¿Por qué el contador de favoritas no puede vivir en Header?

`Header` es hermano de `Hero` y de `MovieList`, no su padre. Si el contador se guardara dentro
de `Header`, tendría que recibir la lista completa de favoritas (lo que rompe el principio de
recibir solo lo necesario) o mantener una copia propia del estado. En cuanto `MovieCard`
marcara una película, la copia de `Header` quedaría desincronizada y aparecerían dos fuentes de
verdad. Al elevar el estado a `App`, el ancestro común notifica a todos: `Header` muestra el
número, `MovieList` marca las tarjetas y el filtro «Solo favoritas» usa la misma lista. Por eso
la ubicación correcta es el nivel más bajo que contiene a todos los componentes que lo necesitan.

---

## Conclusión

El laboratorio permitió visualizar cómo la elevación del estado simplifica la comunicación entre
componentes hermanos: una sola lista de favoritas alimenta el contador, las tarjetas y los
filtros. La extracción de hooks dejó los componentes más limpios y reutilizables, en especial
`useWindowSize`, compartido por la cartelera y el carrusel. Por último, la integración de Sonner
y lucide-react, junto con los estados de carga y error del hook `usePremieres`, hizo que la
interfaz avisara en todo momento qué está pasando, en lugar de quedarse en blanco o mostrar un
mensaje genérico. Las nueve pruebas automatizadas y las capturas adjuntas dejan constancia de
cada comportamiento solicitado.
