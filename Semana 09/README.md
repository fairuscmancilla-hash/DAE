# Semana 09 — Cartelera de cine con React

Laboratorio 9 de **Desarrollo de Aplicaciones Empresariales**: una cartelera de cine construida con
React, Vite, JSX, componentes funcionales y props.

## Puesta en marcha

```powershell
node --version     # se recomienda Node 20.19 o superior
npm install
npm run dev        # http://localhost:5173
```

Para comprobar la compilación de producción:

```powershell
npm run build
npm run preview
```

## Estructura

```text
Semana 09/
├─ capturas/                 Capturas del resultado y de la estructura del proyecto
├─ public/posters/           Ocho afiches SVG
├─ src/
│  ├─ components/            Header, Footer, Hero, MovieCard y MovieList
│  ├─ data/movies.js         Ocho películas, contactos y navegación
│  ├─ styles/                base.css, layout.css y components.css
│  ├─ App.jsx                Composición de la cartelera
│  └─ main.jsx               Punto de entrada de React
├─ index.html
├─ package.json
├─ vite.config.js
└─ ENTREGABLE.md             Informe del laboratorio
```

## Componentes

| Componente | Props | Responsabilidad |
|---|---|---|
| `Header` | `name`, `links` | Nombre del cine y navegación principal |
| `Footer` | `contact` | Dirección, horario, teléfono y correo |
| `Hero` | `movie` | Banner de la película destacada |
| `MovieCard` | `movie` | Afiche, título, clasificación, valoración y horarios |
| `MovieList` | `movies` | Recorre la cartelera con `map` y dibuja una tarjeta por película |

## Datos

`src/data/movies.js` contiene ocho películas y cada una incluye `title`, `image`, `synopsis`,
`classification`, `rating` y `showtimes`. La película **Ruta 91** no tiene funciones hoy: sirve para
comprobar el estado vacío de `MovieCard`.
