from django.contrib import admin

from shop.models import Order, OrderLine, Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("sku", "name", "price", "stock")
    list_filter = ("stock",)
    search_fields = ("sku", "name")


class OrderLineInline(admin.TabularInline):
    model = OrderLine
    extra = 0
    readonly_fields = ("sku", "name", "unit_price", "qty", "subtotal")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("code", "coupon", "subtotal", "discount", "igv", "total", "created_at")
    list_filter = ("created_at",)
    search_fields = ("code", "coupon")
    inlines = [OrderLineInline]
