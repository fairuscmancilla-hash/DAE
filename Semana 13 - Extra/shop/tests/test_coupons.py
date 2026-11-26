from decimal import Decimal

from shop import domain
from shop.tests.base import CartTestCase


class CouponTests(CartTestCase):
    def test_one_coupon_replaces_the_previous_one(self):
        self.cart.add("MOUSEPAD")
        self.cart.apply_coupon("BIENVENIDA10")
        self.cart.apply_coupon("DAE5")
        self.assertEqual(self.cart.summary()["coupon"], "DAE5")
        self.assertEqual(self.cart.discount(), Decimal("0.42"))

    def test_double_click_does_not_accumulate_discount(self):
        self.cart.add("MOUSEPAD")
        self.cart.apply_coupon("BIENVENIDA10")
        once = self.cart.discount()
        self.cart.apply_coupon("BIENVENIDA10")
        self.assertEqual(self.cart.discount(), once)
        self.assertEqual(once, Decimal("0.85"))

    def test_coupon_code_is_stripped_and_uppercased(self):
        self.cart.add("MOUSEPAD")
        self.cart.apply_coupon("  bienvenida10 ")
        self.assertEqual(self.cart.summary()["coupon"], "BIENVENIDA10")

    def test_unknown_coupon_is_rejected(self):
        with self.assertRaises(domain.CouponError):
            self.cart.apply_coupon("NO-VALIDO")

    def test_discount_cannot_exceed_subtotal(self):
        cart = self.new_cart(coupons={"TODO": Decimal("1.00")})
        cart.add("MUG")
        cart.apply_coupon("TODO")
        self.assertIsInstance(cart.discount(), Decimal)
        self.assertEqual(cart.discount(), Decimal("12.00"))
        self.assertEqual(cart.total(), Decimal("0.00"))
