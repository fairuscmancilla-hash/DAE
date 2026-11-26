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

    # FIX 3: incoming units are counted together with the units already held.
    def add(self, sku, qty=1):
        return super().add(sku, qty)

    # FIX 4: reaching zero deletes the line; quantity never goes negative.
    def remove(self, sku, qty=1):
        return super().remove(sku, qty)

    # FIX 2: the unit price always comes from the server catalog.
    def lines(self):
        result = []
        for sku, qty in sorted(self._qty.items()):
            entry = self._catalog[sku]
            unit_price = domain.money(entry["price"])
            result.append(
                {
                    "sku": sku,
                    "name": entry["name"],
                    "unit_price": str(unit_price),
                    "qty": qty,
                    "subtotal": str(domain.money(unit_price * qty)),
                }
            )
        return result

    # FIX 1: money is Decimal from the catalog and rounded with money().
    def subtotal(self):
        return domain.money(
            sum(
                (
                    domain.money(Decimal(self._catalog[sku]["price"]) * qty)
                    for sku, qty in self._qty.items()
                ),
                Decimal("0.00"),
            )
        )

    # FIX 5: one coupon per cart; applying again replaces the previous one.
    def apply_coupon(self, code):
        normalized = domain.normalize_coupon(code)
        if normalized not in self._coupons:
            raise domain.CouponError(f"Unknown coupon: {normalized}")
        self._coupons_applied = [normalized]
        self._coupon = normalized
        return normalized

    # FIX 1 + FIX 5: a single coupon rate and Decimal money only.
    def discount(self):
        subtotal = self.subtotal()
        if self._coupon is None:
            return Decimal("0.00")
        return min(domain.money(subtotal * self._coupons[self._coupon]), subtotal)

    # FIX 1: IGV is Decimal money calculated after the discount.
    def igv(self):
        return domain.money((self.subtotal() - self.discount()) * domain.IGV_RATE)

    # FIX 1: the final total is Decimal money as well.
    def total(self):
        return domain.money(self.subtotal() - self.discount() + self.igv())

    # FIX 1 + FIX 5: the receipt is built from Decimal values and one coupon.
    def summary(self, code=""):
        return {
            "code": code,
            "coupon": self._coupon or "",
            "lines": self.lines(),
            "subtotal": str(self.subtotal()),
            "discount": str(self.discount()),
            "igv": str(self.igv()),
            "total": str(self.total()),
        }

    # FIX 2: the request never supplies a price; delegate to the reviewed rule.
    def add_from_payload(self, payload):
        return super().add_from_payload(payload)

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

    # FIX 2: a declared price is only evidence for the auditor, never an input.
    @classmethod
    def from_dict(cls, data, catalog=None, coupons=None):
        cart = cls(catalog=catalog, coupons=coupons)
        for line in data.get("lines", []):
            cart._qty[line["sku"]] = int(line["qty"])
        for code in data.get("coupons_applied", [data.get("coupon")] if data.get("coupon") else []):
            if code:
                cart.apply_coupon(code)
        return cart

    # FIX 2: the session never stores client-supplied prices.
    def public_state(self):
        state = super().public_state()
        state["coupons_applied"] = list(self._coupons_applied)
        return state

    # FIX 5: a restored session can hold only the single active coupon.
    def restore_state(self, state):
        super().restore_state(state)
        self._client_prices = {}
        self._coupons_applied = [self._coupon] if self._coupon else []
