# Servidor · Laboratorio 13

API del Lab 12 más la app `catalog` (estructura de comercio electrónico).

## Arranque

```powershell
cd "Semana 13/server"
python -m venv .venv
& .venv/Scripts/python.exe -m pip install -r requirements.txt
& .venv/Scripts/python.exe manage.py migrate
& .venv/Scripts/python.exe manage.py seed_quiz
& .venv/Scripts/python.exe manage.py seed_catalog
& .venv/Scripts/python.exe manage.py runserver 127.0.0.1:8002 --noreload
```

`seed_catalog` genera 3 categorías, 9 productos con imagen PNG y el usuario `admin / admin123` para el administrador.

## Estructura añadida

- `catalog/models.py`: `Category` y `Product` (`FK` a categoría, precio, existencias e imagen).
- `catalog/serializers.py`: `category` anidado dentro de cada producto; `category_id` de escritura.
- `catalog/views.py`: ViewSets con paginación, búsqueda y filtro por categoría.
- `catalog/admin.py`: ambos modelos registrados con listados, búsqueda y filtros.
- `catalog/management/commands/seed_catalog.py`: datos de demostración.
- `config/urls.py`: `/admin/`, `/api/catalog/`, `/api/` y serve de `/media/` en DEBUG.

Ver `API_TABLE.md` para el contrato completo y `tests/test_catalog.py` para las 10 pruebas nuevas.

## Pruebas

```powershell
& .venv/Scripts/python.exe manage.py test
```

Resultado: **73 pruebas, OK** (63 heredadas + 10 del catálogo).
