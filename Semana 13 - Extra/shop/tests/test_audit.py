import json
import tempfile
from pathlib import Path

from django.test import TestCase

from shop.management.commands.audit_cart import audit_file


def write_cart(payload):
    file = tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8")
    json.dump(payload, file)
    file.close()
    return file.name


class AuditTests(TestCase):
    def test_valid_cart_has_no_findings(self):
        path = write_cart(
            {
                "lines": [
                    {
                        "sku": "MOUSEPAD",
                        "name": "Mousepad",
                        "unit_price": "8.45",
                        "qty": 1,
                        "subtotal": "8.45",
                    }
                ],
                "coupon": "BIENVENIDA10",
                "totals": {
                    "subtotal": "8.45",
                    "discount": "0.85",
                    "igv": "1.37",
                    "total": "8.97",
                },
            }
        )
        report = audit_file(path)
        Path(path).unlink()
        self.assertEqual(report["verdict"], "ACEPTAR")
        self.assertEqual(report["findings"], [])

    def test_negative_quantity_is_detected(self):
        path = write_cart(
            {
                "lines": [
                    {
                        "sku": "NOTEBOOK",
                        "name": "Cuaderno",
                        "unit_price": "6.30",
                        "qty": -1,
                        "subtotal": "-6.30",
                    }
                ],
                "coupon": "",
                "totals": {
                    "subtotal": "-6.30",
                    "discount": "0.00",
                    "igv": "-1.13",
                    "total": "-7.43",
                },
            }
        )
        report = audit_file(path)
        Path(path).unlink()
        self.assertEqual(report["verdict"], "RECHAZAR")
        self.assertTrue(any("BAD_QTY" in item for item in report["findings"]))

    def test_client_price_is_detected(self):
        path = write_cart(
            {
                "lines": [
                    {
                        "sku": "KEYBOARD",
                        "name": "Teclado",
                        "unit_price": "1.00",
                        "qty": 1,
                        "subtotal": "1.00",
                    }
                ],
                "coupon": "",
                "totals": {
                    "subtotal": "1.00",
                    "discount": "0.00",
                    "igv": "0.18",
                    "total": "1.18",
                },
            }
        )
        report = audit_file(path)
        Path(path).unlink()
        self.assertTrue(any("PRICE_MISMATCH" in item for item in report["findings"]))
        self.assertTrue(any("TOTAL_MISMATCH" in item for item in report["findings"]))

    def test_multiple_coupons_are_detected(self):
        path = write_cart(
            {
                "lines": [
                    {
                        "sku": "MOUSEPAD",
                        "name": "Mousepad",
                        "unit_price": "8.45",
                        "qty": 1,
                        "subtotal": "8.45",
                    }
                ],
                "coupon": "DAE5",
                "coupons_applied": ["BIENVENIDA10", "DAE5"],
                "totals": {
                    "subtotal": "8.45",
                    "discount": "1.27",
                    "igv": "1.29",
                    "total": "8.47",
                },
            }
        )
        report = audit_file(path)
        Path(path).unlink()
        self.assertTrue(any("MULTIPLE_COUPONS" in item for item in report["findings"]))
