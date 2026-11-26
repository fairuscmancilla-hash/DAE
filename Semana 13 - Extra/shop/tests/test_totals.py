from decimal import Decimal, ROUND_HALF_UP

from shop import domain
from shop.tests.base import CartTestCase


class TotalsTests(CartTestCase):
    def test_float_and_decimal_examples_are_not_the_same(self):
        self.assertNotEqual(0.1 + 0.2, 0.3)
        self.assertEqual(Decimal("0.1") + Decimal("0.2"), Decimal("0.3"))
        self.assertEqual(round(0.845, 2), 0.84)
        self.assertEqual(
            Decimal("0.845").quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
            Decimal("0.85"),
        )
        self.assertEqual(domain.money("0.845"), Decimal("0.85"))

    def test_mousepad_with_welcome_coupon_matches_the_manual_calculation(self):
        self.cart.add("MOUSEPAD")
        self.cart.apply_coupon("BIENVENIDA10")
        self.assertEqual(self.cart.subtotal(), Decimal("8.45"))
        self.assertEqual(self.cart.discount(), Decimal("0.85"))
        self.assertEqual(self.cart.igv(), Decimal("1.37"))
        self.assertEqual(self.cart.total(), Decimal("8.97"))

    def test_totals_without_coupon(self):
        self.cart.add("MUG")
        self.assertEqual(self.cart.discount(), Decimal("0.00"))
        self.assertEqual(self.cart.igv(), Decimal("2.16"))
        self.assertEqual(self.cart.total(), Decimal("14.16"))

    def test_total_is_always_decimal(self):
        self.cart.add("KEYBOARD", 2)
        self.assertIsInstance(self.cart.total(), Decimal)
        self.assertEqual(str(self.cart.total()), "117.76")

    def test_igv_is_calculated_after_discount(self):
        self.cart.add("MUG")
        self.cart.apply_coupon("DAE5")
        self.assertEqual(self.cart.discount(), Decimal("0.60"))
        self.assertEqual(self.cart.igv(), Decimal("2.05"))
        self.assertEqual(self.cart.total(), Decimal("13.45"))
