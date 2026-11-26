"""The team cart: exact money, accumulated stock and one coupon.

Every public method is deliberately independent of HTTP and Django so the
tests can call it directly.  The catalog passed to the constructor is held by
reference, so ``checkout`` debits exactly that catalog; callers that need
isolation pass ``domain.clone_catalog()`` as the tests do.
"""

from decimal import Decimal

from shop import domain


class Cart:
    def __init__(self, catalog=None, coupons=None):
        self._catalog = catalog if catalog is not None else domain.clone_catalog()
        self._coupons = dict(coupons if coupons is not None else domain.COUPONS)
        self._qty = {}
        self._coupon = None

    # ---------- validation helpers ----------
    @staticmethod
    def _positive_int(qty):
        if type(qty) is not int or qty <= 0:
            raise domain.CartError("Quantity must be a positive integer")
        return qty

    def _entry(self, sku):
        if not isinstance(sku, str) or sku not in self._catalog:
            raise domain.UnknownProduct(f"Unknown product: {sku!r}")
        return self._catalog[sku]

    # ---------- lines and stock ----------
    def add(self, sku, qty=1):
        """Add units, counting what the cart already holds."""
        qty = self._positive_int(qty)
        entry = self._entry(sku)
        current = self._qty.get(sku, 0)
        if current + qty > entry["stock"]:
            raise domain.StockError(
                f"{sku}: {current} in cart + {qty} requested > {entry['stock']} in stock"
            )
        self._qty[sku] = current + qty
        return self._qty[sku]

    def remove(self, sku, qty=1):
        """Remove units; reaching zero deletes the line."""
        qty = self._positive_int(qty)
        self._entry(sku)
        current = self._qty.get(sku, 0)
        remaining = current - qty
        if remaining <= 0:
            self._qty.pop(sku, None)
            return 0
        self._qty[sku] = remaining
        return remaining

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

    # ---------- exact money ----------
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

    def discount(self):
        if self._coupon is None:
            return Decimal("0.00")
        discount = domain.money(self.subtotal() * self._coupons[self._coupon])
        return min(discount, self.subtotal())

    def igv(self):
        return domain.money((self.subtotal() - self.discount()) * domain.IGV_RATE)

    def total(self):
        return domain.money(self.subtotal() - self.discount() + self.igv())

    def summary(self, code=""):
        subtotal = self.subtotal()
        discount = self.discount()
        igv = self.igv()
        total = self.total()
        return {
            "code": code,
            "coupon": self._coupon or "",
            "lines": self.lines(),
            "subtotal": str(subtotal),
            "discount": str(discount),
            "igv": str(igv),
            "total": str(total),
        }

    # ---------- coupon ----------
    def apply_coupon(self, code):
        """Replace the current coupon: a double click must be idempotent."""
        normalized = domain.normalize_coupon(code)
        if normalized not in self._coupons:
            raise domain.CouponError(f"Unknown coupon: {normalized}")
        self._coupon = normalized
        return normalized

    # ---------- API boundary ----------
    def add_from_payload(self, payload):
        """Translate an HTTP body into ``add`` without ever reading a price."""
        if not isinstance(payload, dict):
            raise domain.BadPayload("Request body must be an object")
        sku = payload.get("sku")
        if not isinstance(sku, str) or not sku.strip():
            raise domain.BadPayload("A text 'sku' is required")
        qty = payload.get("qty", 1)
        try:
            return self.add(sku.strip(), qty)
        except domain.UnknownProduct:
            raise
        except domain.StockError as exc:
            raise domain.StockError(str(exc)) from exc
        except domain.CartError as exc:
            raise domain.BadPayload(str(exc)) from exc

    # ---------- checkout ----------
    def checkout(self, code=""):
        """Recheck all stock, debit it once, clear the cart and return a receipt."""
        for sku, qty in self._qty.items():
            if qty > self._catalog[sku]["stock"]:
                raise domain.StockError(f"{sku}: {qty} requested, {self._catalog[sku]['stock']} available")
        receipt = self.summary(code=code)
        for sku, qty in self._qty.items():
            self._catalog[sku]["stock"] -= qty
        self._qty.clear()
        self._coupon = None
        return receipt

    # ---------- audit serialization ----------
    def as_dict(self):
        return {
            "lines": self.lines(),
            "coupon": self._coupon or "",
            "totals": {
                "subtotal": str(self.subtotal()),
                "discount": str(self.discount()),
                "igv": str(self.igv()),
                "total": str(self.total()),
            },
        }

    @classmethod
    def from_dict(cls, data, catalog=None, coupons=None):
        cart = cls(catalog=catalog, coupons=coupons)
        for line in data.get("lines", []):
            cart._qty[line["sku"]] = int(line["qty"])
        if data.get("coupon"):
            cart._coupon = domain.normalize_coupon(data["coupon"])
        return cart

    # ---------- state used by the thin HTTP layer ----------
    def public_state(self):
        return {"qty": dict(self._qty), "coupon": self._coupon}

    def restore_state(self, state):
        self._qty = dict(state.get("qty", {}))
        self._coupon = state.get("coupon") or None
