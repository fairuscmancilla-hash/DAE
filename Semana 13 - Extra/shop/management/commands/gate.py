"""Acceptance gate: tests + headless audit with exit code 0/1."""

import json
import os
import re
import subprocess
import sys
from pathlib import Path

from django.core.management.base import BaseCommand

from shop.management.commands.audit_cart import audit_file

BASE = Path(__file__).resolve().parents[3]


def run_tests(mode):
    env = dict(os.environ, SHOP_MODE=mode)
    result = subprocess.run(
        [sys.executable, "manage.py", "test", "shop.tests", "--verbosity=1"],
        cwd=BASE,
        env=env,
        capture_output=True,
        text=True,
    )
    output = result.stdout + result.stderr
    ran = re.search(r"Ran (\d+) tests?", output)
    failed = re.search(r"failures=(\d+)", output)
    errors = re.search(r"errors=(\d+)", output)
    total = int(ran.group(1)) if ran else 0
    failing = (int(failed.group(1)) if failed else 0) + (int(errors.group(1)) if errors else 0)
    names = re.findall(r"^(?:FAIL|ERROR): ([^\s]+)", output, flags=re.MULTILINE)
    return {
        "total": total,
        "passing": total - failing,
        "failing": failing,
        "failing_names": names,
    }


class Command(BaseCommand):
    help = "Decide whether a cart implementation is accepted (0) or rejected (1)."

    def add_arguments(self, parser):
        parser.add_argument("--modo", choices=["team", "ai"], default="team")
        parser.add_argument("--cart", default=str(BASE / "carts" / "01-valid.json"))
        parser.add_argument("--json", action="store_true", dest="as_json")

    def handle(self, *args, **options):
        mode = options["modo"]
        os.environ["SHOP_MODE"] = mode
        tests = run_tests(mode)
        audit = audit_file(Path(options["cart"]), replay=True)
        accepted = tests["failing"] == 0 and audit["verdict"] == "ACEPTAR"
        verdict = "ACEPTAR" if accepted else "RECHAZAR"
        report = {
            "verdict": verdict,
            "mode": mode,
            "tests": tests,
            "audit": {
                "cart": audit["cart"],
                "verdict": audit["verdict"],
                "findings": audit["findings"],
            },
            "exit_code": 0 if accepted else 1,
        }

        if options["as_json"]:
            self.stdout.write(json.dumps(report, indent=2, ensure_ascii=False))
        else:
            self.stdout.write("=" * 70)
            self.stdout.write(f"COMPUERTA / GATE - modo={mode} - carrito={audit['cart']}")
            self.stdout.write("=" * 70)
            self.stdout.write(
                f"tests   : {tests['passing']}/{tests['total']} passed, {tests['failing']} failing"
            )
            for name in tests["failing_names"]:
                self.stdout.write(f"          - {name}")
            self.stdout.write(f"auditoria: {audit['verdict']} ({len(audit['findings'])} hallazgos)")
            for finding in audit["findings"]:
                self.stdout.write(f"          - {finding}")
            self.stdout.write(f"VEREDICTO: {verdict} (exit={report['exit_code']})")
            self.stdout.write("=" * 70)
        raise SystemExit(report["exit_code"])
