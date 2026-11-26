from django.test import TestCase

from shop import domain, impl


class CartTestCase(TestCase):
    """Every test builds a fresh pure cart from an isolated catalog."""

    def setUp(self):
        self.catalog = domain.clone_catalog()
        self.coupons = dict(domain.COUPONS)
        self.cart = self.new_cart()

    def new_cart(self, catalog=None, coupons=None):
        return impl.new_cart(
            catalog=catalog if catalog is not None else self.catalog,
            coupons=coupons if coupons is not None else self.coupons,
        )
