# Semana 6 · Motor de plantillas con Django

Implementación del laboratorio de la semana 6: motor de plantillas de una
aplicación web en Django con herencia, fragmentos reutilizables, datos del
modelo en plantillas y contenido gestionado desde el administrador.

## Estructura del proyecto

```
Semana6-DAE/
├── manage.py
├── config/                     # Proyecto Django
│   ├── settings.py             # Plantillas, estáticos, medios, apps
│   └── urls.py                 # Rutas + medios en desarrollo
├── templates/
│   └── base.html               # Plantilla base con bloques
├── news/                       # Aplicación del portal
│   ├── models.py               # SiteSetting, Category, Author, Article
│   ├── admin.py                # list_display, list_filter, search_fields
│   ├── views.py                # home, article_detail, category_list
│   ├── urls.py                 # Rutas con nombre (app_name = "news")
│   ├── context_processors.py   # categories + site para todas las plantillas
│   ├── management/commands/seed_news.py
│   ├── templates/news/
│   │   ├── home.html           # for / empty / filtros (portada)
│   │   ├── article_detail.html # detalle con imagen, autor y categorías
│   │   ├── category_list.html  # listado por categoría
│   │   ├── _article_card.html  # fragmento de tarjeta reutilizable
│   │   └── _sidebar.html       # fragmento de barra lateral
│   └── tests.py                # 10 casos de prueba
├── static/css/styles.css
└── media/articles/             # Imágenes destacadas
```

## Cómo ejecutar

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_news           # superusuario, 3 categorías, 6 noticias
python manage.py runserver
```

- Portal: <http://127.0.0.1:8000/>
- Administrador: <http://127.0.0.1:8000/admin/> (usuario `admin`, clave `admin123`)

## Capacidades implementadas

### 1. Motor de plantillas con herencia y fragmentos reutilizables

- `base.html` define la estructura común (cabecera, banner, `content`, `sidebar`
  y pie) y los bloques `title`, `content` y `sidebar` que cada página completa.
- `news/_article_card.html` es el fragmento de tarjeta que se incluye desde la
  portada y desde el listado por categoría sin repetir marcado.
- `news/_sidebar.html` se reutiliza en la portada y en el listado por categoría.

### 2. Datos del modelo con variables, etiquetas de control y filtros

- Variables: `{{ article.title }}`, `{{ article.author.full_name }}`.
- Control: `{% for %}`, `{% empty %}`, `{% if %}`, `{% include %}`, `{% url %}`,
  `{% extends %}` y `{% block %}`.
- Filtros: `date` (con localización `es-pe`), `timesince`, `truncatewords`,
  `capfirst`, `length`, `pluralize`, `slice` y `linebreaks`.

### 3. Contenido gestionado desde el administrador

- Modelos `Article`, `Category`, `Author` y `SiteSetting` registrados en el
  administrador con `list_display`, `list_filter`, `search_fields` y
  `prepopulated_fields`.
- El modelo `SiteSetting` guarda el nombre del portal, la bajada y el banner;
  todo lo que se modifica en el panel se publica en las plantillas sin tocar
  código, gracias al context processor `site_menu`.

## Casos de prueba

`python manage.py test news` ejecuta 10 pruebas:

1. La portada hereda de `base.html` (`extends` + `include` del fragmento).
2. Sin noticias se muestra el bloque `empty`.
3. Las tarjetas muestran variables, resumen y fecha formateada con filtros.
4. El listado por categoría reutiliza el mismo fragmento de tarjeta.
5. El detalle muestra autor y categorías.
6. El HTML del cuerpo aparece escapado (autoescape).
7. Los enlaces entre páginas se resuelven con la etiqueta `{% url %}`.
8. El changelist del admin lista las noticias con las opciones personalizadas.
9. Lo que se cambia en el admin (SiteSetting) llega al sitio sin tocar código.
10. Las noticias no publicadas se ocultan del portal.

## Escapado automático (paso 12 del procedimiento)

- La noticia **"Django 6 llega con mejoras en el motor de plantillas"** guarda en
  su cuerpo las etiquetas `<b>plantillas base</b>` y `{% extends %}`.
- En la página de detalle el contenido se muestra como texto literal
  (`&lt;b&gt;plantillas base&lt;/b&gt;`), no como HTML aplicado.
- ¿Por qué? Django escapa de forma automática todo valor de variable antes de
  mostrarlo: `&`, `<`, `>`, `"` y `'` se convierten en entidades. Es una medida
  de seguridad contra ataques XSS; se desactiva solo donde hace falta (por
  ejemplo con `|safe`), algo que no se usa en este laboratorio.