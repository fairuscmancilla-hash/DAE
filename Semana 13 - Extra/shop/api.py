"""Thin HTTP layer: translate requests into cart calls and errors into codes."""

import json
from datetime import datetime

from django.db import transaction
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from shop import domain, impl
from shop.models import Order, OrderLine, Product


def _body(request):
    if not request.body:
        return {}
    try:
        return json.loads(request.body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise domain.BadPayload("Invalid JSON body") from exc


def _cart(request):
    cart = impl.new_cart(catalog=impl.catalog_from_db())
    cart.restore_state(request.session.get("cart_state", {}))
    return cart


def _save(request, cart):
    request.session["cart_state"] = cart.public_state()
    request.session.modified = True


def _error(exc):
    if isinstance(exc, domain.UnknownProduct):
        return JsonResponse({"error": str(exc)}, status=404)
    if isinstance(exc, domain.StockError):
        return JsonResponse({"error": str(exc)}, status=409)
    if isinstance(exc, domain.CartError):
        return JsonResponse({"error": str(exc)}, status=400)
    return JsonResponse({"error": str(exc)}, status=500)


@csrf_exempt
@require_http_methods(["GET", "POST"])
def cart_detail(request):
    cart = _cart(request)
    if request.method == "POST":
        return _error(domain.BadPayload("Use /api/cart/add/ to add lines"))
    return JsonResponse(cart.summary())


@csrf_exempt
@require_http_methods(["POST"])
def cart_add(request):
    try:
        cart = _cart(request)
        cart.add_from_payload(_body(request))
        _save(request, cart)
        return JsonResponse(cart.summary(), status=201)
    except domain.CartError as exc:
        return _error(exc)


@csrf_exempt
@require_http_methods(["POST"])
def cart_coupon(request):
    try:
        cart = _cart(request)
        body = _body(request)
        code = body.get("code") if isinstance(body, dict) else None
        cart.apply_coupon(code)
        _save(request, cart)
        return JsonResponse(cart.summary())
    except domain.CartError as exc:
        return _error(exc)


@csrf_exempt
@require_http_methods(["POST"])
def cart_checkout(request):
    try:
        cart = _cart(request)
        if not cart.lines():
            return JsonResponse({"error": "Cart is empty"}, status=400)
        receipt = cart.checkout(code=f"DAE-{datetime.now():%Y%m%d%H%M%S}")
        with transaction.atomic():
            products = {p.sku: p for p in Product.objects.select_for_update().all()}
            for line in receipt["lines"]:
                product = products[line["sku"]]
                if product.stock < line["qty"]:
                    raise domain.StockError(
                        f"{line['sku']}: stock changed during checkout"
                    )
                product.stock -= line["qty"]
                product.save(update_fields=["stock"])
            order = Order.objects.create(
                code=receipt["code"],
                coupon=receipt["coupon"],
                subtotal=receipt["subtotal"],
                discount=receipt["discount"],
                igv=receipt["igv"],
                total=receipt["total"],
            )
            for line in receipt["lines"]:
                OrderLine.objects.create(order=order, **line)
        request.session.pop("cart_state", None)
        return JsonResponse(receipt, status=201)
    except domain.CartError as exc:
        return _error(exc)
