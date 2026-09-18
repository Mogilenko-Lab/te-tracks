#!/usr/bin/env python3
"""Qualify the record gene profile and combined-annotation identity boundaries."""

from pathlib import Path
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "lib"))
from consumers import run_check, starsolo_profile_check

run_check("STARsolo/cellranger", "record profile parser", starsolo_profile_check)
