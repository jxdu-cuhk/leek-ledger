from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest.mock import patch


TOOLS_DIR = Path(__file__).resolve().parents[1] / "tools"
sys.path.insert(0, str(TOOLS_DIR))

from trade_tracker.overview import insert_transaction_fee_metric, split_overview_by_currency


class Cell:
    def __init__(self, raw):
        self.raw = raw


class Core:
    def normalize_currency(self, value):
        mapping = {
            "人民币": "CNY",
            "RMB": "CNY",
            "CNY": "CNY",
            "港币": "HKD",
            "HKD": "HKD",
            "美元": "USD",
            "USD": "USD",
        }
        return mapping.get(str(value or "").strip(), str(value or "").strip().upper())


def overview_shell() -> str:
    return """
        <div class="dashboard-grid">
          <div class="metric-card">
            <div class="metric-label">总盈亏</div>
            <div class="metric-value metric-value-wide">
              <span class="metric-segment value-positive">人民币 100.00</span>
              <span class="metric-separator"> / </span>
              <span class="metric-segment value-negative">港币 -20.00</span>
            </div>
            <div class="metric-note">示例</div>
          </div>
        </div>
    """


def overview_reconciliation_shell() -> str:
    cards = []
    metrics = [
        ("总盈亏", [("人民币", "50.00", "value-positive"), ("港币", "-20.00", "value-negative")]),
        ("总收益率", [("人民币", "5.00%", "value-positive"), ("港币", "-10.00%", "value-negative")]),
        ("已实现盈亏", [("人民币", "100.00", "value-positive"), ("港币", "10.00", "value-positive")]),
        ("持仓浮盈亏", [("人民币", "20.00", "value-positive"), ("港币", "-5.00", "value-negative")]),
    ]
    for label, segments in metrics:
        value_html = '<span class="metric-separator"> / </span>'.join(
            f'<span class="metric-segment {value_class}">{currency} {value}</span>'
            for currency, value, value_class in segments
        )
        cards.append(
            f"""
          <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value metric-value-wide">{value_html}</div>
            <div class="metric-note">示例</div>
          </div>
            """
        )
    return '<div class="dashboard-grid">' + "".join(cards) + "</div>"


class OverviewTests(unittest.TestCase):
    def test_insert_transaction_fee_metric_groups_by_currency(self):
        rows = [
            (2, {11: Cell(2.5), 20: Cell("CNY")}),
            (3, {11: Cell(-3), 20: Cell("HKD")}),
            (4, {11: Cell(0), 20: Cell("USD")}),
        ]

        updated = insert_transaction_fee_metric(Core(), rows, overview_shell())

        self.assertIn("交易费用", updated)
        self.assertIn("人民币 2.50", updated)
        self.assertIn("港币 3.00", updated)
        self.assertNotIn("美元 0.00", updated)

    def test_split_overview_by_currency_includes_transaction_fee_in_reporting_card(self):
        rows = [
            (2, {11: Cell(2.5), 20: Cell("CNY")}),
            (3, {11: Cell(3), 20: Cell("HKD")}),
        ]
        html = insert_transaction_fee_metric(Core(), rows, overview_shell())

        with patch("trade_tracker.overview.current_fx_rates_to_cny", return_value={"人民币": 1.0, "港币": 0.9}):
            updated = split_overview_by_currency(html)

        self.assertIn("<span>交易费用</span>", updated)
        self.assertIn('data-reporting-money-cny="5.200000"', updated)
        self.assertIn(">5.20</strong>", updated)

    def test_split_overview_keeps_source_total_pnl_values(self):
        with patch("trade_tracker.overview.current_fx_rates_to_cny", return_value={"人民币": 1.0, "港币": 0.9}):
            updated = split_overview_by_currency(overview_reconciliation_shell())

        self.assertIn("<span>总盈亏</span><strong class=\"value-positive\">50.00</strong>", updated)
        self.assertIn("<span>总盈亏</span><strong class=\"value-negative\">-20.00</strong>", updated)
        self.assertIn('data-reporting-money-cny="32.000000"', updated)
        self.assertIn(">32.00</strong>", updated)


if __name__ == "__main__":
    unittest.main()
