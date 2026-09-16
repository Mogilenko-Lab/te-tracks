#!/usr/bin/env python3
"""Verify registered targets and count-seven conservation through DuckDB joins and distinct features."""

import importlib
from pathlib import Path
import sys

try:
    import duckdb
except ImportError:
    print("unsupported: python module duckdb absent")
    raise SystemExit(3)

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tests/checks/core"))
registration_check = importlib.import_module("41_export_registration")
from records import BUILD, require


def main():
    """Conserve each measured count once per target and level through its registered supporting records."""
    require("tables/export_feature_members.tsv.gz")
    membership, counts, targets, totals = registration_check.conservation_fixture()
    with duckdb.connect(":memory:") as connection:
        connection.register("membership", membership)
        connection.register("counts", counts)
        connection.execute("""
            CREATE TEMP TABLE edges AS
            SELECT m.emitted_feature_id, r.rmsk_record_id,
                   r.feature_level, r.emitted_feature_id AS target
            FROM read_csv(?, delim = '\t', header = true, quote = '', all_varchar = true) AS r
            JOIN membership AS m ON r.rmsk_record_id = m.rmsk_record_id
            WHERE r.universe_name = 'interspersed' AND r.variant = 'full'
              AND r.feature_level IN ('record', 'subfamily', 'family')
              AND (r.feature_level <> 'record' OR r.emitted_feature_id = r.rmsk_record_id)
        """, [str(BUILD / "tables/export_feature_members.tsv.gz")])
        observed_targets = connection.execute("""
            SELECT emitted_feature_id, rmsk_record_id, feature_level, target FROM edges
        """).fetchall()
        assert sorted(observed_targets) == sorted(targets.itertuples(index=False, name=None)), (
            "conservation targets per measured feature", observed_targets)
        rolled_up = connection.execute("""
            SELECT selected.feature_level, selected.target, SUM(c.count)
            FROM (
                SELECT DISTINCT feature_level, target, emitted_feature_id FROM edges
            ) AS selected
            JOIN counts AS c USING (emitted_feature_id)
            GROUP BY selected.feature_level, selected.target
        """).fetchall()
        assert sorted(rolled_up) == sorted(totals.itertuples(index=False, name=None)), rolled_up
        conserved = connection.execute("""
            SELECT selected.feature_level, SUM(c.count)
            FROM (
                SELECT DISTINCT feature_level, emitted_feature_id FROM edges
            ) AS selected
            JOIN counts AS c USING (emitted_feature_id)
            GROUP BY selected.feature_level
            ORDER BY selected.feature_level
        """).fetchall()
        assert conserved == [("family", 7), ("record", 7), ("subfamily", 7)], conserved
        expanded = connection.execute("""
            SELECT e.feature_level, SUM(c.count)
            FROM edges AS e JOIN counts AS c USING (emitted_feature_id)
            GROUP BY e.feature_level ORDER BY e.feature_level
        """).fetchall()
        assert expanded == [("family", 21), ("record", 21), ("subfamily", 21)], expanded
    print("DuckDB registration targets and hand-computed totals pass; "
          "count 7 stays 7 at record, subfamily and family levels")


if __name__ == "__main__":
    main()
