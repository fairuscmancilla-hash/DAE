"""Headless audit of carts declared by the shop (and by the AI)."""

import json
from decimal import Decimal, InvalidOperation
from pathlib import Path

from django.core.management.base import BaseCommand

from shop import domain, impl
from shop.cart_team import Cart as TeamCart

BASE = Path(__file__).resolve().parents[3]
TOTAL_KEYS = ("subtotal", "discount", "igv", "total")


def _as_money(value):
    try:
        return domain.money(Decimal(str(value)))
    except (InvalidOperation, TypeError, ValueError):
        return None


def audit_file(path, replay=False):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    catalog = impl.catalog_from_db()
    findings = []

    coupons = data.get("coupons_applied")
    if coupons is None:
        coupons = [data["coupon"]] if data.get("coupon") else []
    if len(coupons) > 1:
        findings.append(
            f"MULTIPLE_COUPONS: {', '.join(coupons)}; only one coupon is allowed"
        )

    for line in data.get("lines", []):
        sku = line.get("sku")
        qty = line.get("qty")
        if type(qty) is not int or qty <= 0:
            findings.append(f"BAD_QTY: {sku} has quantity {qty!r}")
            continue
        if sku in catalog and qty > catalog[sku]["stock"]:
            findings.append(
                f"OVER_STOCK: {sku} asks {qty} but stock is {catalog[sku]['stock']}"
            )
        declared_price = _as_money(line.get("unit_price"))
        if sku in catalog and declared_price is not None:
            server_price = domain.money(catalog[sku]["price"])
            if declared_price != server_price:
                findings.append(
                    f"PRICE_MISMATCH: {sku} declares {declared_price}, server has {server_price}"
                )

    oracle = TeamCart.from_dict(data, catalog=catalog)
    expected = oracle.summary()
    declared = data.get("totals", {})
    for key in TOTAL_KEYS:
        declared_value = _as_money(declared.get(key))
        expected_value = _as_money(expected.get(key))
        if declared_value != expected_value:
            findings.append(
                f"TOTAL_MISMATCH: {key} declares {declared.get(key)}, expected {expected.get(key)}"
            )

    replayed = {}
    if replay:
        active = impl.get_cart_class().from_dict(data, catalog=catalog)
        replayed = active.summary()
        for key in TOTAL_KEYS:
            if _as_money(replayed.get(key)) != _as_money(expected.get(key)):
                findings.append(
                    f"REPLAY_MISMATCH: {key} replayed as {replayed.get(key)}, expected {expected.get(key)}"
                )

    return {
        "cart": Path(path).name,
        "mode": impl.mode(),
        "verdict": "ACEPTAR" if not findings else "RECHAZAR",
        "findings": findings,
        "expected_totals": {key: expected.get(key) for key in TOTAL_KEYS},
        "replayed_totals": {key: replayed.get(key) for key in TOTAL_KEYS} if replay else None,
    }


class Command(BaseCommand):
    help = "Audit declared carts against the server catalog and the shop rules."

    def add_arguments(self, parser):
        parser.add_argument("carts", nargs="*", help="Cart JSON files (default: carts/*.json)")
        parser.add_argument("--replay", action="store_true", help="Recompute with SHOP_MODE implementation")
        parser.add_argument("--json", action="store_true", dest="as_json", help="Machine-readable output")
        parser.add_argument("--strict", action="store_true", help="Exit 1 when any cart is rejected")

    def handle(self, *args, **options):
        paths = [Path(p) for p in options["carts"]]
        if not paths:
            paths = sorted((BASE / "carts").glob("*.json"))
        reports = [audit_file(path, replay=options["replay"]) for path in paths]

        if options["as_json"]:
            self.stdout.write(json.dumps({"carts": reports}, indent=2, ensure_ascii=False))
        else:
            self.stdout.write("=" * 70)
            self.stdout.write(f"AUDITORIA DE CARRITOS / SHOP_MODE={impl.mode()} / replay={options['replay']}")
            self.stdout.write("=" * 70)
            for report in reports:
                self.stdout.write(f"[{report['cart']}] {report['verdict']}")
                if not report["findings"]:
                    self.stdout.write("  sin hallazgos")
                for finding in report["findings"]:
                    self.stdout.write(f"  - {finding}")
            self.stdout.write("=" * 70)

        if options["strict"] and any(r["verdict"] == "RECHAZAR" for r in reports):
            raise SystemExit(1)
