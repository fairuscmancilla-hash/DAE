from shop import domain
from shop.tests.base import CartTestCase


class StockTests(CartTestCase):
    def test_add_counts_what_is_already_in_the_cart(self):
        self.cart.add("MOUSEPAD", 3)
        with self.assertRaises(domain.StockError):
            self.cart.add("MOUSEPAD", 3)
        self.assertEqual(self.cart._qty["MOUSEPAD"], 3)

    def test_checkout_rechecks_stock_and_debits_catalog_once(self):
        self.cart.add("MOUSEPAD", 2)
        receipt = self.cart.checkout(code="PEDIDO-1")
        self.assertEqual(receipt["code"], "PEDIDO-1")
        self.assertEqual(self.catalog["MOUSEPAD"]["stock"], 3)
        self.assertEqual(self.cart.lines(), [])
        self.assertEqual(self.cart._coupon, None)

    def test_checkout_rejects_when_stock_changed_after_add(self):
        self.cart.add("KEYBOARD", 2)
        self.cart._catalog["KEYBOARD"]["stock"] = 1
        with self.assertRaises(domain.StockError):
            self.cart.checkout()
        self.assertEqual(self.cart._qty["KEYBOARD"], 2)
        self.assertEqual(self.cart._catalog["KEYBOARD"]["stock"], 1)

    def test_two_checkouts_cannot_double_spend_the_same_units(self):
        self.cart.add("MUG", 3)
        self.cart.checkout()
        self.assertEqual(self.catalog["MUG"]["stock"], 0)
        with self.assertRaises(domain.StockError):
            self.cart.add("MUG")
        with self.assertRaises(domain.CartError):
            self.cart.add("MUG", 1)
