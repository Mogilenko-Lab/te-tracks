#!/usr/bin/env python3
"""Report executable availability and verify import-failure classification in process."""

from contextlib import redirect_stderr, redirect_stdout
import io
from pathlib import Path
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "lib"))
from consumers import TOOLS, discover, run_check


def missing_symbol():
    from math import te_tracks_absent_symbol


def missing_module():
    import te_tracks_absent_dependency


for probe, expected_exit, message in (
    (missing_symbol, 1, "cannot import name 'te_tracks_absent_symbol'"),
    (missing_module, 3, "unsupported: inventory_probe python module te_tracks_absent_dependency absent"),
):
    output, errors = io.StringIO(), io.StringIO()
    with redirect_stdout(output), redirect_stderr(errors):
        try:
            run_check("inventory_probe", "self-test", probe)
        except SystemExit as error:
            assert error.code == expected_exit, (error.code, output.getvalue(), errors.getvalue())
        else:
            raise AssertionError("import probe succeeded")
    assert message in output.getvalue(), output.getvalue()

inventory = [discover(tool) for tool in TOOLS]
print("supported tool_inventory reporting-only; " + "; ".join(
    f"{item['tool']}={item['version']}" for item in inventory))
for item in inventory:
    print(f"{item['tool']}\t{item['version']}\t{item['path'] or 'absent'}")
print("import classification self-test: missing symbol exit=1; absent module exit=3")
