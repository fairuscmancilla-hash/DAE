# Semana 11 - Comunicación entre componentes en ReactJS

Laboratorio de DAE que parte de la cartelera de la Semana 10 y añade comunicación entre
componentes hermanos, hooks propios y estados de carga y error.

## Ejecutar

```powershell
npm install
npm run dev
npm test
npm run build
```

## Puntos clave

- `src/App.jsx`: estado elevado de favoritas y filtros; llama a `toast()` de Sonner.
- `src/hooks/`: `useDebounce`, `useWindowSize` (compartido) y `usePremieres`.
- `src/lib/movieAdapter.js`: adapta el payload externo al modelo de la interfaz.
- `src/components/PremieresSection.jsx`: estados de carga, datos y error del carrusel.

El desarrollo completo, el árbol de componentes y las evidencias están en `ENTREGABLE.md`.
