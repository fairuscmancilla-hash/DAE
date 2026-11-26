from shop import domain
from shop.tests.base import CartTestCase


class LineTests(CartTestCase):
    def test_add_builds_a_line_and_remove_to_zero_deletes_it(self):
        self.cart.add("MOUSEPAD", 2)
        lines = self.cart.lines()
        self.assertEqual(len(lines), 1)
        self.assertEqual(lines[0]["sku"], "MOUSEPAD")
        self.assertEqual(lines[0]["qty"], 2)
        self.assertEqual(lines[0]["subtotal"], "16.90")

        self.cart.remove("MOUSEPAD", 2)
        self.assertEqual(self.cart.lines(), [])
        self.assertEqual(self.cart.subtotal(), domain.money("0"))

    def test_remove_more_than_current_never_creates_negative_quantity(self):
        self.cart.add("NOTEBOOK", 1)
        remaining = self.cart.remove("NOTEBOOK", 4)
        self.assertEqual(remaining, 0)
        self.assertEqual(self.cart.lines(), [])
        self.assertEqual(self.cart.total(), domain.money("0"))

    def test_quantity_must_be_a_positive_integer(self):
        with self.assertRaises(domain.CartError):
            self.cart.add("MOUSEPAD", 0)
        with self.assertRaises(domain.CartError):
            self.cart.add("MOUSEPAD", "2")
        with self.assertRaises(domain.CartError):
            self.cart.remove("MOUSEPAD", -1)

    def test_unknown_sku_is_rejected(self):
        with self.assertRaises(domain.UnknownProduct):
            self.cart.add("NO-SUCH-SKU")

    def test_lines_sort_by_sku_and_use_catalog_price(self):
        self.cart.add("MUG")
        self.cart.add("MOUSEPAD")
        self.assertEqual([line["sku"] for line in self.cart.lines()], ["MOUSEPAD", "MUG"])
        self.assertEqual(self.cart.lines()[0]["unit_price"], "8.45")
