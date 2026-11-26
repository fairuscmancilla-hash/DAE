"""Persistent shop data.  The cart itself stays as pure business logic."""

from decimal import Decimal

from django.db import models

from shop.domain import CATALOG, money


class Product(models.Model):
    sku = models.CharField(max_length=32, unique=True)
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField()

    class Meta:
        ordering = ["sku"]

    def __str__(self):
        return f"{self.sku} - {self.name}"


class Order(models.Model):
    code = models.CharField(max_length=32, unique=True)
    coupon = models.CharField(max_length=32, blank=True)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=10, decimal_places=2)
    igv = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.code


class OrderLine(models.Model):
    order = models.ForeignKey(Order, related_name="lines", on_delete=models.CASCADE)
    sku = models.CharField(max_length=32)
    name = models.CharField(max_length=100)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    qty = models.PositiveIntegerField()
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.order.code}: {self.sku} x {self.qty}"


def catalog_from_db():
    """Read the server-side price and stock into the pure cart catalog."""
    catalog = {}
    for product in Product.objects.all():
        catalog[product.sku] = {
            "name": product.name,
            "price": money(Decimal(product.price)),
            "stock": product.stock,
        }
    if not catalog:
        return {
            sku: {"name": item["name"], "price": item["price"], "stock": item["stock"]}
            for sku, item in CATALOG.items()
        }
    return catalog
