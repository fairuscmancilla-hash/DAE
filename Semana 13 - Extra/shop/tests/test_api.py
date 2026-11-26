import json
from decimal import Decimal

from django.test import TestCase

from shop import domain, impl
from shop.models import Order, Product


class ApiBoundaryTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        for sku, item in domain.CATALOG.items():
            Product.objects.create(
                sku=sku,
                name=item["name"],
                price=Decimal(str(item["price"])),
                stock=item["stock"],
            )

    def setUp(self):
        self.cart = impl.new_cart(catalog=impl.catalog_from_db())

    def test_payload_must_be_an_object_with_text_sku(self):
        with self.assertRaises(domain.BadPayload):
            self.cart.add_from_payload(["MOUSEPAD"])
        with self.assertRaises(domain.BadPayload):
            self.cart.add_from_payload({"sku": 123})
        with self.assertRaises(domain.BadPayload):
            self.cart.add_from_payload({"sku": "   "})

    def test_client_price_is_never_read(self):
        self.cart.add_from_payload({"sku": "MOUSEPAD", "price": "0.01", "qty": 1})
        self.assertEqual(self.cart.lines()[0]["unit_price"], "8.45")
        self.assertEqual(self.cart.subtotal(), Decimal("8.45"))

    def test_http_add_coupon_checkout_sequence(self):
        add = self.client.post(
            "/api/cart/add/",
            data=json.dumps({"sku": "MOUSEPAD", "qty": 1, "price": "0.01"}),
            content_type="application/json",
        )
        self.assertEqual(add.status_code, 201)
        self.assertEqual(add.json()["lines"][0]["unit_price"], "8.45")
        self.assertEqual(add.json()["total"], "9.97")

        coupon = self.client.post(
            "/api/cart/coupon/",
            data=json.dumps({"code": " bienvenida10 "}),
            content_type="application/json",
        )
        self.assertEqual(coupon.status_code, 200)
        self.assertEqual(coupon.json()["total"], "8.97")

        checkout = self.client.post(
            "/api/cart/checkout/", data="{}", content_type="application/json"
        )
        self.assertEqual(checkout.status_code, 201)
        self.assertEqual(checkout.json()["total"], "8.97")
        self.assertEqual(Product.objects.get(sku="MOUSEPAD").stock, 4)
        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(Order.objects.first().lines.count(), 1)

    def test_http_maps_cart_errors_to_status_codes(self):
        missing = self.client.post(
            "/api/cart/add/",
            data=json.dumps({"sku": "NO-SUCH-SKU"}),
            content_type="application/json",
        )
        self.assertEqual(missing.status_code, 404)

        over_stock = self.client.post(
            "/api/cart/add/",
            data=json.dumps({"sku": "KEYBOARD", "qty": 5}),
            content_type="application/json",
        )
        self.assertEqual(over_stock.status_code, 409)

        bad_body = self.client.post(
            "/api/cart/add/", data="[]", content_type="application/json"
        )
        self.assertEqual(bad_body.status_code, 400)

        bad_coupon = self.client.post(
            "/api/cart/coupon/",
            data=json.dumps({"code": "NO-VALIDO"}),
            content_type="application/json",
        )
        self.assertEqual(bad_coupon.status_code, 400)
