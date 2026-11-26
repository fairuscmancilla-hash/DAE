from django.contrib import admin
from django.urls import path

from shop import api

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/cart/", api.cart_detail, name="cart-detail"),
    path("api/cart/add/", api.cart_add, name="cart-add"),
    path("api/cart/coupon/", api.cart_coupon, name="cart-coupon"),
    path("api/cart/checkout/", api.cart_checkout, name="cart-checkout"),
]
