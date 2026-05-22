from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


TOOLS_DIR = Path(__file__).resolve().parents[1] / "tools"
sys.path.insert(0, str(TOOLS_DIR))

import trade_tracker.daily_pnl_history as daily_pnl_history_module  # noqa: E402
from trade_tracker.daily_pnl_history import apply_daily_pnl_history_to_curve, record_daily_pnl_snapshot  # noqa: E402


class DailyPnlHistoryTests(unittest.TestCase):
    def test_current_daily_pnl_snapshot_overrides_curve_daily_float_by_currency(self):
        display_payload = {
            "dailyPnl": {
                "current": {
                    "date": "2026-05-22",
                    "holdingFloatCny": 152.0,
                    "byCurrency": {
                        "人民币": {"native": 100.0, "cny": 100.0, "rateToCny": 1.0},
                        "港币": {"native": 60.0, "cny": 52.0, "rateToCny": 0.8667},
                    },
                }
            }
        }
        data = {
            "curve_series": [
                {
                    "currency": "人民币",
                    "points": [
                        {"iso": "2026-05-21", "value": 20.0, "realized_value": 10.0},
                        {"iso": "2026-05-22", "value": 50.0, "realized_value": 15.0, "daily_float_value": 1.0},
                    ],
                },
                {
                    "currency": "港币",
                    "points": [
                        {"iso": "2026-05-21", "value": -10.0, "realized_value": 0.0},
                        {"iso": "2026-05-22", "value": 5.0, "realized_value": 0.0, "daily_float_value": 2.0},
                    ],
                },
            ]
        }
        with tempfile.TemporaryDirectory() as temp_dir:
            cache_path = Path(temp_dir) / "daily_pnl_history.json"
            with patch.object(daily_pnl_history_module, "DAILY_PNL_CACHE_PATH", cache_path):
                cache = record_daily_pnl_snapshot(display_payload)
                apply_daily_pnl_history_to_curve(data, display_payload, cache)

        cny_point = data["curve_series"][0]["points"][1]
        hk_point = data["curve_series"][1]["points"][1]
        self.assertAlmostEqual(cny_point["daily_float_value"], 100.0)
        self.assertAlmostEqual(cny_point["daily_total_value"], 30.0)
        self.assertAlmostEqual(hk_point["daily_float_value"], 60.0)
        self.assertAlmostEqual(hk_point["daily_total_value"], 15.0)


if __name__ == "__main__":
    unittest.main()
