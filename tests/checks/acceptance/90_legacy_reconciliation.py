"""Accept legacy reconciliation against the fresh published builds."""

from lib.common import run

run("90_legacy_reconciliation")
