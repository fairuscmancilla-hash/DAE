"""Select the implementation under test.

``SHOP_MODE=team`` is the default.  Setting ``SHOP_MODE=ai`` makes the same
tests, API endpoints and management commands exercise the AI cart without
changing any test file.
"""

import os

from shop.cart_ai import Cart as AICart
from shop.cart_team import Cart as TeamCart


def mode():
    return "ai" if os.getenv("SHOP_MODE", "team").strip().lower() == "ai" else "team"


def get_cart_class():
    return AICart if mode() == "ai" else TeamCart


def new_cart(catalog=None, coupons=None):
    return get_cart_class()(catalog=catalog, coupons=coupons)


def catalog_from_db():
    from shop.models import catalog_from_db as load

    return load()
