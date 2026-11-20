# Tabla de la API del catálogo · Laboratorio 13

Base: `http://127.0.0.1:8002/api/catalog/`
Autenticación: los ViewSets usan `AllowAny` en este laboratorio de clase. El cliente puede enviar `Authorization: Token ...` de forma opcional.

| Método | Ruta | Descripción | Respuesta principal |
|--------|------|-------------|---------------------|
| GET | `/api/catalog/products/` | Lista paginada de productos con la categoría anidada | `{count, next, previous, results[]}` |
| GET | `/api/catalog/products/?category=<id>` | Filtra productos por categoría en el servidor | Misma forma, solo los productos de esa categoría |
| GET | `/api/catalog/products/?search=<texto>` | Búsqueda por nombre, descripción o categoría | Misma forma |
| GET | `/api/catalog/products/<id>/` | Detalle de un producto | Producto con `category` anidado |
| POST | `/api/catalog/products/` | Alta con `category_id` de escritura e imagen | `201` con categoría anidada |
| PUT / PATCH | `/api/catalog/products/<id>/` | Modificación; la imagen es opcional | `200` con categoría anidada |
| DELETE | `/api/catalog/products/<id>/` | Borrado lógico físico del producto | `204` |
| GET | `/api/catalog/categories/` | Lista de categorías con `product_count` | `{count, results[]}` |
| GET | `/api/catalog/categories/<id>/` | Detalle de categoría | Categoría con `product_count` |
| POST | `/api/catalog/categories/` | Alta de categoría | `201` |
| PUT / PATCH | `/api/catalog/categories/<id>/` | Edición de categoría | `200` |
| DELETE | `/api/catalog/categories/<id>/` | Borrado de categoría | `204` |

## Ejemplo de una sola petición

`GET /api/catalog/products/?page_size=20`

```json
{
  "count": 9,
  "results": [
    {
      "id": 2,
      "name": "Green tea 100 g",
      "price": "9.50",
      "stock": 40,
      "image_url": "http://127.0.0.1:8002/media/products/green-tea.png",
      "category": {
        "id": 1,
        "name": "Drinks",
        "description": "Café, té y bebidas para la semana.",
        "product_count": 3
      }
    }
  ]
}
```

La categoría llega dentro del producto: la pantalla no necesita una segunda petición para pintar el nombre de la categoría ni el contador.
