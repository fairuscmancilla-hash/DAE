"""Run the same test oracle against the team cart and the AI cart."""

import os
import re
import subprocess
import sys
from pathlib import Path

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Compare the team cart and the AI cart with the same test suite."

    def add_arguments(self, parser):
        parser.add_argument("--modo", choices=["team", "ai"], help="Run only one mode")

    def _run(self, mode):
        env = dict(os.environ, SHOP_MODE=mode)
        result = subprocess.run(
            [sys.executable, "manage.py", "test", "shop.tests", "--verbosity=1"],
            cwd=Path(__file__).resolve().parents[3],
            env=env,
            capture_output=True,
            text=True,
        )
        output = result.stdout + result.stderr
        ran = re.search(r"Ran (\d+) tests?", output)
        failed = re.search(r"failures=(\d+)", output)
        errors = re.search(r"errors=(\d+)", output)
        failing = int(failed.group(1)) if failed else 0
        failing += int(errors.group(1)) if errors else 0
        total = int(ran.group(1)) if ran else 0
        return {
            "mode": mode,
            "total": total,
            "passing": total - failing,
            "failing": failing,
            "exit_code": result.returncode,
        }

    def handle(self, *args, **options):
        modes = [options["modo"]] if options.get("modo") else ["team", "ai"]
        rows = [self._run(mode) for mode in modes]
        self.stdout.write("=" * 58)
        self.stdout.write("DUELO DE CARRITOS - the same tests, two implementations")
        self.stdout.write("=" * 58)
        self.stdout.write(f"{'mode':<8}{'tests':>8}{'passed':>9}{'failed':>9}  verdict")
        for row in rows:
            verdict = "OK" if row["failing"] == 0 else "RECHAZAR"
            self.stdout.write(
                f"{row['mode']:<8}{row['total']:>8}{row['passing']:>9}{row['failing']:>9}  {verdict}"
            )
        self.stdout.write("=" * 58)
