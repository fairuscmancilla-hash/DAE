"""Cart written by an AI assistant, before review.

It compiles and handles the happy path, but it contains five deliberate
defects.  The comments mark them so the review table can point at exact
lines.  The team keeps this file as the submitted original until step 13.
"""

from decimal import Decimal

from shop import domain
from shop.cart_team import Cart as TeamCart


class Cart(TeamCart):
    def __init__(self, catalog=None, coupons=None):
        super().__init__(catalog=catalog, coupons=coupons)
        self._client_prices = {}
        self._coupons_applied = []

    # BUG 3: only the incoming quantity is compared with stock; the units
    # already in the cart are ignored.
    def add(self, sku, qty=1):
        qty = self._positive_int(qty)
        entry = self._entry(sku)
        if qty > entry["stock"]:
            raise domain.StockError(f"{sku}: {qty} requested > {entry['stock']} in stock")
        self._qty[sku] = self._qty.get(sku, 0) + qty
        return self._qty[sku]

    # BUG 4: the line is never deleted, so removing more than the current
    # quantity leaves a negative line that reduces the total.
    def remove(self, sku, qty=1):
        qty = self._positive_int(qty)
        self._entry(sku)
        self._qty[sku] = self._qty.get(sku, 0) - qty
        return self._qty[sku]

    # BUG 2: the unit price may be overwritten by a value in the request.
    def lines(self):
        result = []
        for sku, qty in sorted(self._qty.items()):
            entry = self._catalog[sku]
            price = self._client_prices.get(sku, entry["price"])
            unit_price = float(price)
            result.append(
                {
                    "sku": sku,
                    "name": entry["name"],
                    "unit_price": f"{unit_price:.2f}",
                    "qty": qty,
                    "subtotal": f"{unit_price * qty:.2f}",
                }
            )
        return result

    # BUG 1: money is handled as float and rounded with Python's round(),
    # which uses banker's rounding on an inexact binary value.
    def subtotal(self):
        total = 0.0
        for sku, qty in self._qty.items():
            price = self._client_prices.get(sku, self._catalog[sku]["price"])
            total += float(price) * qty
        return round(total, 2)

    # BUG 5: every click adds another coupon, so discounts accumulate.
    def apply_coupon(self, code):
        normalized = domain.normalize_coupon(code)
        if normalized not in self._coupons:
            raise domain.CouponError(f"Unknown coupon: {normalized}")
        self._coupons_applied.append(normalized)
        self._coupon = normalized
        return normalized

    # BUG 5 + BUG 1: all applied rates are summed and rounded as float.
    def discount(self):
        subtotal = float(self.subtotal())
        rate = sum(float(self._coupons[code]) for code in self._coupons_applied)
        return round(min(subtotal * rate, subtotal), 2)

    def igv(self):
        return round(float(self.subtotal() - self.discount()) * 0.18, 2)

    def total(self):
        return round(float(self.subtotal() - self.discount() + self.igv()), 2)

    def summary(self, code=""):
        return {
            "code": code,
            "coupon": ", ".join(self._coupons_applied),
            "lines": self.lines(),
            "subtotal": f"{float(self.subtotal()):.2f}",
            "discount": f"{float(self.discount()):.2f}",
            "igv": f"{float(self.igv()):.2f}",
            "total": f"{float(self.total()):.2f}",
        }

    # BUG 2: the request supplies the price and the cart believes it.
    def add_from_payload(self, payload):
        if not isinstance(payload, dict):
            raise domain.BadPayload("Request body must be an object")
        sku = payload.get("sku")
        if not isinstance(sku, str) or not sku.strip():
            raise domain.BadPayload("A text 'sku' is required")
        sku = sku.strip()
        price = payload.get("price")
        if price is not None:
            self._client_prices[sku] = price
        try:
            return self.add(sku, payload.get("qty", 1))
        except domain.UnknownProduct:
            raise
        except domain.StockError as exc:
            raise domain.StockError(str(exc)) from exc
        except domain.CartError as exc:
            raise domain.BadPayload(str(exc)) from exc

    def checkout(self, code=""):
        for sku, qty in self._qty.items():
            if qty > self._catalog[sku]["stock"]:
                raise domain.StockError(
                    f"{sku}: {qty} requested, {self._catalog[sku]['stock']} available"
                )
        receipt = self.summary(code=code)
        for sku, qty in self._qty.items():
            self._catalog[sku]["stock"] -= qty
        self._qty.clear()
        self._coupon = None
        self._coupons_applied.clear()
        self._client_prices.clear()
        return receipt

    def as_dict(self):
        data = self.summary()
        return {
            "lines": data["lines"],
            "coupon": self._coupon or "",
            "coupons_applied": list(self._coupons_applied),
            "totals": {
                "subtotal": data["subtotal"],
                "discount": data["discount"],
                "igv": data["igv"],
                "total": data["total"],
            },
        }

    @classmethod
    def from_dict(cls, data, catalog=None, coupons=None):
        cart = cls(catalog=catalog, coupons=coupons)
        for line in data.get("lines", []):
            cart._qty[line["sku"]] = int(line["qty"])
            if "unit_price" in line:
                cart._client_prices[line["sku"]] = line["unit_price"]
        for code in data.get("coupons_applied", [data.get("coupon")] if data.get("coupon") else []):
            if code:
                cart.apply_coupon(code)
        return cart

    def public_state(self):
        state = super().public_state()
        state["client_prices"] = dict(self._client_prices)
        state["coupons_applied"] = list(self._coupons_applied)
        return state

    def restore_state(self, state):
        super().restore_state(state)
        self._client_prices = dict(state.get("client_prices", {}))
        self._coupons_applied = list(state.get("coupons_applied", []))
