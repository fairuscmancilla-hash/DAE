"""Pure shop rules.

The cart never touches Django models directly.  It receives a plain catalog
of dictionaries with ``Decimal`` prices and integer stock, so the same rules
can be exercised without a database or a browser.
"""

from copy import deepcopy
from decimal import Decimal, ROUND_HALF_UP

CENT = Decimal("0.01")
IGV_RATE = Decimal("0.18")

CATALOG = {
    "MOUSEPAD": {"name": "Mousepad", "price": Decimal("8.45"), "stock": 5},
    "MUG": {"name": "Taza DAE", "price": Decimal("12.00"), "stock": 3},
    "NOTEBOOK": {"name": "Cuaderno", "price": Decimal("6.30"), "stock": 4},
    "KEYBOARD": {"name": "Teclado", "price": Decimal("49.90"), "stock": 2},
}

COUPONS = {
    "BIENVENIDA10": Decimal("0.10"),
    "DAE5": Decimal("0.05"),
}


class CartError(Exception):
    """Base error raised by a cart rule."""


class BadPayload(CartError):
    """The API body is not a valid cart request."""


class UnknownProduct(CartError):
    """The requested SKU does not exist in the server catalog."""


class StockError(CartError):
    """There is not enough stock for the requested quantity."""


class CouponError(CartError):
    """The coupon code is unknown."""


def money(value):
    """Return ``value`` rounded to cents using half up, never as float."""
    amount = value if isinstance(value, Decimal) else Decimal(str(value))
    return amount.quantize(CENT, rounding=ROUND_HALF_UP)


def clone_catalog(source=None):
    """Return an isolated copy of the pure catalog."""
    return deepcopy(source if source is not None else CATALOG)


def normalize_coupon(code):
    """Strip spaces and upper-case a coupon code."""
    if not isinstance(code, str):
        raise CouponError("Coupon code must be text")
    normalized = code.strip().upper()
    if not normalized:
        raise CouponError("Coupon code is required")
    return normalized
