from decimal import Decimal

from django.core.management.base import BaseCommand

from shop.domain import CATALOG
from shop.models import Product


class Command(BaseCommand):
    help = "Seed the server-side shop catalog with the laboratory products."

    def handle(self, *args, **options):
        for sku, item in CATALOG.items():
            Product.objects.update_or_create(
                sku=sku,
                defaults={
                    "name": item["name"],
                    "price": Decimal(str(item["price"])),
                    "stock": item["stock"],
                },
            )
        self.stdout.write(
            self.style.SUCCESS(
                f"seed_shop: {len(CATALOG)} products ready (server owns price and stock)"
            )
        )
        for sku, item in CATALOG.items():
            self.stdout.write(f"  {sku:10} {item['name']:12} {item['price']:>6} stock={item['stock']}")
