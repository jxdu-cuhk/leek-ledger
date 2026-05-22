from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from .runtime import APP_DIR
from .utils import clean_text, parse_float


DAILY_PNL_CACHE_VERSION = 1
DAILY_PNL_CACHE_PATH = APP_DIR / "tools" / "cache" / "daily_pnl_history.json"
EPSILON = 0.000001


def load_daily_pnl_cache() -> dict[str, object]:
    if not DAILY_PNL_CACHE_PATH.exists():
        return {"version": DAILY_PNL_CACHE_VERSION, "days": {}}
    try:
        data = json.loads(DAILY_PNL_CACHE_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {"version": DAILY_PNL_CACHE_VERSION, "days": {}}
    if not isinstance(data, dict):
        return {"version": DAILY_PNL_CACHE_VERSION, "days": {}}
    days = data.get("days")
    if not isinstance(days, dict):
        days = {}
    return {"version": DAILY_PNL_CACHE_VERSION, "days": days}


def save_daily_pnl_cache(cache: dict[str, object]) -> None:
    DAILY_PNL_CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    DAILY_PNL_CACHE_PATH.write_text(
        json.dumps(cache, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )


def _current_daily_snapshot(display_payload: dict[str, object]) -> tuple[str, dict[str, object]] | None:
    daily = display_payload.get("dailyPnl") if isinstance(display_payload, dict) else None
    current = daily.get("current") if isinstance(daily, dict) else None
    if not isinstance(current, dict):
        return None
    iso = clean_text(current.get("date"))
    by_currency = current.get("byCurrency")
    if not iso or not isinstance(by_currency, dict):
        return None
    snapshot_by_currency: dict[str, object] = {}
    for currency, payload in by_currency.items():
        if not isinstance(payload, dict):
            continue
        label = clean_text(currency) or clean_text(payload.get("currency"))
        native = parse_float(payload.get("native"))
        cny = parse_float(payload.get("cny"))
        rate = parse_float(payload.get("rateToCny"))
        if not label or native is None:
            continue
        snapshot_by_currency[label] = {
            "currency": label,
            "native": native,
            "cny": cny if cny is not None else native,
            "rateToCny": rate if rate is not None and rate > 0 else 1.0,
        }
    if not snapshot_by_currency:
        return None
    holding_cny = parse_float(current.get("holdingFloatCny"))
    return iso, {
        "date": iso,
        "updatedAt": datetime.now(timezone.utc).isoformat(),
        "holdingFloatCny": holding_cny if holding_cny is not None else sum(
            parse_float(item.get("cny")) or 0.0 for item in snapshot_by_currency.values() if isinstance(item, dict)
        ),
        "byCurrency": snapshot_by_currency,
    }


def record_daily_pnl_snapshot(display_payload: dict[str, object]) -> dict[str, object]:
    cache = load_daily_pnl_cache()
    snapshot = _current_daily_snapshot(display_payload)
    if snapshot is None:
        return cache
    iso, payload = snapshot
    days = cache.setdefault("days", {})
    if isinstance(days, dict):
        days[iso] = payload
    save_daily_pnl_cache(cache)
    return cache


def _point_total(point: dict[str, object] | None) -> float | None:
    if not point:
        return None
    total = parse_float(point.get("total_value"))
    if total is None:
        total = parse_float(point.get("value"))
    return total


def apply_daily_pnl_history_to_curve(
    data: dict[str, object],
    display_payload: dict[str, object],
    cache: dict[str, object] | None = None,
) -> dict[str, object]:
    if not isinstance(data, dict):
        return data
    cache = cache or record_daily_pnl_snapshot(display_payload)
    days = cache.get("days") if isinstance(cache, dict) else None
    if not isinstance(days, dict):
        return data
    for series in data.get("curve_series", []) or []:
        if not isinstance(series, dict):
            continue
        currency = clean_text(series.get("currency"))
        if not currency:
            continue
        points = [point for point in series.get("points", []) or [] if isinstance(point, dict)]
        previous: dict[str, object] | None = None
        for point in sorted(points, key=lambda item: clean_text(item.get("iso"))):
            iso = clean_text(point.get("iso"))
            day_payload = days.get(iso) if iso else None
            by_currency = day_payload.get("byCurrency") if isinstance(day_payload, dict) else None
            currency_payload = by_currency.get(currency) if isinstance(by_currency, dict) else None
            daily_float = parse_float(currency_payload.get("native")) if isinstance(currency_payload, dict) else None
            if daily_float is not None:
                point["daily_float_value"] = daily_float
                current_total = _point_total(point)
                previous_total = _point_total(previous)
                if current_total is not None:
                    point["daily_total_value"] = current_total if previous_total is None else current_total - previous_total
            previous = point
    return data
