# Cliente · Laboratorio 13

React + Vite sobre el proyecto del Lab 11/12. Añade el catálogo de comercio electrónico.

## Arranque

```powershell
cd "Semana 13/client"
npm install
Copy-Item .env.example .env.local
npm run dev -- --host 127.0.0.1 --port 5174
```

`.env.local` apunta a `http://127.0.0.1:8002`. El token es opcional porque la API de catálogo es pública en el laboratorio de clase.

## Capa de servicios

Ningún componente importa Axios. Todo pasa por:

- `src/services/apiClient.js`: instancia, errores y helpers CRUD.
- `src/services/productService.js`: `list`, `get`, `create`, `update`, `remove`.
- `src/services/categoryService.js`: `list`, `get`, `create`, `update`, `remove`.

## Rutas de la interfaz

| Hash | Vista |
|------|-------|
| `#catalog` | Catálogo con filtro por categoría y estados carga/datos/error |
| `#product-new` | Alta de producto |
| `#product-edit-<id>` | Edición de producto |
| `#questions`, `#new`, `#home` | Laboratorios 12 y 11 acumulados |

## Pruebas

```powershell
npm test
npm run build
```

Resultado: **8 archivos, 27 pruebas** y build correcto.
