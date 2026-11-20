from pathlib import Path

from django.conf import settings
from django.contrib.auth.models import Group, User
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.text import slugify
from PIL import Image, ImageDraw

from catalog.models import Category, Product

CATEGORIES = [
    ("Drinks", "Café, té y bebidas para la semana."),
    ("Snacks", "Aperitivos para compartir o llevar."),
    ("Technology", "Accesorios para el puesto de trabajo."),
]

PRODUCTS = [
    ("Drinks", "Ground coffee 500 g", "Dark roast, whole bean aroma.", "18.90", 25, (111, 78, 55)),
    ("Drinks", "Green tea 100 g", "Light infusion with lemon notes.", "9.50", 40, (143, 178, 96)),
    ("Drinks", "Lemonade powder", "One litre of refreshment per sachet.", "7.20", 60, (238, 214, 91)),
    ("Snacks", "Natural potato chips", "Thin cut, sea salt.", "6.80", 80, (226, 173, 86)),
    ("Snacks", "Chocolate cookies", "Crunchy biscuits with chocolate chips.", "5.50", 100, (150, 99, 66)),
    ("Snacks", "Mixed dried fruit", "Almonds, raisins and cashews.", "14.90", 35, (172, 114, 72)),
    ("Technology", "Wireless mouse", "Silent clicks, Bluetooth and USB receiver.", "45.00", 12, (90, 105, 125)),
    ("Technology", "Mechanical keyboard", "Compact layout with tactile switches.", "129.00", 8, (55, 65, 80)),
    ("Technology", "Bluetooth headphones", "Over-ear, 30 h battery life.", "89.90", 15, (72, 82, 105)),
]


def make_image(name, color):
    """Generate a small deterministic PNG so the seed has no binary assets."""
    image = Image.new("RGB", (480, 320), color)
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, 479, 48), fill=(255, 255, 255))
    draw.text((16, 16), name[:46], fill=(20, 30, 50))
    draw.rectangle((16, 80, 464, 288), outline=(255, 255, 255), width=4)
    target = Path(settings.MEDIA_ROOT) / "products"
    target.mkdir(parents=True, exist_ok=True)
    path = target / f"{slugify(name)}.png"
    image.save(path, "PNG")
    return path


class Command(BaseCommand):
    help = "Load the catalog demo data: 3 categories, 9 products and a dev admin."

    @transaction.atomic
    def handle(self, *args, **options):
        categories = {}
        for name, description in CATEGORIES:
            category, _ = Category.objects.update_or_create(
                name=name,
                defaults={"description": description},
            )
            categories[name] = category

        for category_name, name, description, price, stock, color in PRODUCTS:
            path = make_image(name, color)
            Product.objects.update_or_create(
                name=name,
                defaults={
                    "category": categories[category_name],
                    "description": description,
                    "price": price,
                    "stock": stock,
                    "image": ContentFile(path.read_bytes(), name=path.name),
                },
            )

        staff_group, _ = Group.objects.get_or_create(name="Staff")
        admin, _ = User.objects.get_or_create(
            username="admin",
            defaults={"is_staff": True, "is_superuser": True},
        )
        admin.is_staff = True
        admin.is_superuser = True
        admin.set_password("admin123")  # classroom-only account
        admin.save()
        admin.groups.add(staff_group)

        self.stdout.write(
            self.style.SUCCESS(
                f"Listo: {Category.objects.count()} categorías, "
                f"{Product.objects.count()} productos con imagen."
            )
        )
        self.stdout.write("Admin de Django: admin / admin123 (solo para esta máquina).")
