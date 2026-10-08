from datetime import timedelta

from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.text import slugify

from news.models import Article, Author, Category, SiteSetting

CATEGORIES = [
    ("Tecnología", "Noticias sobre software, hardware y desarrollo."),
    ("Deportes", "Resultados, análisis y calendario de la temporada."),
    ("Cultura", "Libros, cine, música y eventos de la ciudad."),
]

ARTICLES = [
    {
        "title": "Django 6 llega con mejoras en el motor de plantillas",
        "category": "Tecnología",
        "summary": "La nueva versión afina la plantilla heredada y reduce el tiempo de renderizado.",
        "body": (
            "El equipo de Django publicó la sexta versión mayor del framework. "
            "Entre las novedades destaca la reescritura del intérprete de plantillas, "
            "que ahora resuelve la herencia de bloques en una sola pasada.\n\n"
            "Los equipos que ya usan <b>plantillas base</b> no tienen que cambiar nada: "
            "las etiquetas {% extends %} y {% block %} conservan su significado."
        ),
        "days_ago": 1,
        "color": (37, 99, 235),
    },
    {
        "title": "Cómo organizar fragmentos reutilizables en un proyecto",
        "category": "Tecnología",
        "summary": "Un fragmento por tarjeta evita repetir marcado entre la portada y el listado por categoría.",
        "body": (
            "La regla es simple: si el mismo marcado aparece en dos plantillas, "
            "se extrae a un fragmento con guion bajo inicial.\n\n"
            "El include recibe solo las variables que necesita, de modo que el fragmento "
            "no depende del contexto completo de la página."
        ),
        "days_ago": 3,
        "color": (16, 185, 129),
    },
    {
        "title": "La selección define su convocatoria para el torneo regional",
        "category": "Deportes",
        "summary": "Veintitrés jugadores confirmados y dos debutantes en la lista del cuerpo técnico.",
        "body": (
            "El cuerpo técnico anunció la lista definitiva tras el último entrenamiento. "
            "Los dos debutantes se sumaron por su rendimiento en el torneo local.\n\n"
            "El equipo inicia la fase de grupos el próximo mes."
        ),
        "days_ago": 2,
        "color": (220, 38, 38),
    },
    {
        "title": "Resumen de la jornada: goles, lesiones y polémicas",
        "category": "Deportes",
        "summary": "Nueve goles en seis partidos y dos expulsiones marcaron el fin de semana.",
        "body": (
            "La jornada dejó resultados dispares: los favoritos ganaron con solvencia "
            "y dos equipos de la mitad de la tabla sacaron puntos importantes de visitante.\n\n"
            "La comisión de disciplina revisará dos jugadas del clásico."
        ),
        "days_ago": 5,
        "color": (217, 119, 6),
    },
    {
        "title": "Festival de cine independiente abre su convocatoria",
        "category": "Cultura",
        "summary": "Directorios de todo el país podrán presentar cortometrajes hasta fin de mes.",
        "body": (
            "La muestra acepta ficción, documental y animación con una duración máxima de veinte minutos. "
            "Las proyecciones serán abiertas al público en la sala central.\n\n"
            "El jurado premiará a tres categorías y a la mejor ópera prima."
        ),
        "days_ago": 4,
        "color": (124, 58, 237),
    },
    {
        "title": "Cinco libros para entender la historia de la ciudad",
        "category": "Cultura",
        "summary": "Una selección de lecturas que explican cómo creció el puerto y sus barrios.",
        "body": (
            "La biblioteca pública presentó su lista de recomendaciones del mes. "
            "Los cinco títulos combinan crónica, ensayo y fotografía histórica.\n\n"
            "Todos están disponibles en la sala de préstamo sin reserva previa."
        ),
        "days_ago": 7,
        "color": (5, 150, 105),
    },
]

AUTHORS = [
    {
        "username": "mmontgomery",
        "first_name": "Michael",
        "last_name": "Montgomery",
        "bio": "Docente de Desarrollo de Aplicaciones Empresariales. Escribe sobre Django y arquitectura web.",
        "website": "https://example.com/mmontgomery",
    },
    {
        "username": "aredaction",
        "first_name": "Ana",
        "last_name": "Redacción",
        "bio": "Editora del portal. Coordina las secciones de deportes y cultura.",
        "website": "",
    },
    {
        "username": "lquispe",
        "first_name": "Lucía",
        "last_name": "Quispe",
        "bio": "Periodista especializada en tecnología, innovación y educación digital.",
        "website": "",
    },
    {
        "username": "dcabrera",
        "first_name": "Diego",
        "last_name": "Cabrera",
        "bio": "Cronista deportivo y analista de competencias regionales.",
        "website": "",
    },
    {
        "username": "sramirez",
        "first_name": "Sofía",
        "last_name": "Ramírez",
        "bio": "Redactora de cultura, cine y literatura.",
        "website": "",
    },
    {
        "username": "jtorres",
        "first_name": "Javier",
        "last_name": "Torres",
        "bio": "Reportero de actualidad y coordinador de contenidos del portal.",
        "website": "",
    },
]


class Command(BaseCommand):
    help = "Seed the portal with the superuser, 3 categories and 6 articles."

    def add_arguments(self, parser):
        parser.add_argument("--username", default="admin")
        parser.add_argument("--password", default="admin123")

    def handle(self, *args, **options):
        site = SiteSetting.current()
        site.site_name = "Portal de Noticias"
        site.tagline = "Noticias gestionadas desde el administrador de Django."
        site.announcement = ""
        site.save()

        self.create_superuser(options["username"], options["password"])

        categories = {
            name: Category.objects.get_or_create(
                name=name, defaults={"description": description}
            )[0]
            for name, description in CATEGORIES
        }

        authors = [self.create_author(data) for data in AUTHORS]

        for index, data in enumerate(ARTICLES):
            author = authors[index % len(authors)]
            image_name = f"article_{index + 1}.png"
            article, created = Article.objects.get_or_create(
                slug=slugify(data["title"]),
                defaults={
                    "title": data["title"],
                    "summary": data["summary"],
                    "body": data["body"],
                    "published_at": timezone.now() - timedelta(days=data["days_ago"]),
                    "author": author,
                    "featured_image": None,
                },
            )
            if created:
                article.categories.add(categories[data["category"]])
            if article.author_id != author.id:
                article.author = author
                article.save(update_fields=["author"])
            if not article.featured_image:
                article.featured_image.save(
                    image_name, ContentFile(self.render_image(data)), save=True
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"Site '{site.site_name}' seeded: "
                f"{Category.objects.count()} categories, "
                f"{Article.objects.count()} articles."
            )
        )

    def create_superuser(self, username, password):
        if User.objects.filter(username=username).exists():
            self.stdout.write(f"User '{username}' already exists, password untouched.")
            return
        User.objects.create_superuser(username=username, password=password, email="")
        self.stdout.write(self.style.SUCCESS(f"Superuser '{username}' created."))

    def create_author(self, data):
        user, created = User.objects.get_or_create(
            username=data["username"],
            defaults={
                "first_name": data["first_name"],
                "last_name": data["last_name"],
            },
        )
        author, _ = Author.objects.get_or_create(
            user=user,
            defaults={"bio": data["bio"], "website": data["website"]},
        )
        return author

    def render_image(self, data):
        """Build a deterministic placeholder image without external assets."""
        from io import BytesIO

        from PIL import Image, ImageDraw

        width, height = 800, 450
        image = Image.new("RGB", (width, height), data["color"])
        draw = ImageDraw.Draw(image)
        draw.rectangle([20, 20, width - 20, height - 20], outline=(255, 255, 255), width=4)
        draw.text((40, 40), data["category"], fill=(255, 255, 255))

        buffer = BytesIO()
        image.save(buffer, format="PNG")
        return buffer.getvalue()
