from __future__ import annotations

import csv
import io

import httpx

ECB_API_URL = (
    "https://data-api.ecb.europa.eu/service/data/EXR/D.USD.EUR.SP00.A"
)


def fetch_usd_eur_rate(year: int) -> float:
    """Fetch the USD/EUR exchange rate from the ECB API for late December.

    Returns a float representing how many USD equal 1 EUR (e.g. 1.0386).
    Uses the last available business day rate in December of the given year.
    To convert USD to EUR: eur_amount = usd_amount / rate.
    """
    params = {
        "startPeriod": f"{year}-12-20",
        "endPeriod": f"{year}-12-31",
        "format": "csvdata",
    }
    resp = httpx.get(ECB_API_URL, params=params, timeout=15)
    resp.raise_for_status()

    reader = csv.DictReader(io.StringIO(resp.text))
    last_rate = None
    for row in reader:
        val = row.get("OBS_VALUE", "").strip()
        if val:
            last_rate = float(val)

    if last_rate is None:
        raise ValueError(f"Failed to fetch EUR/USD rate for year {year}")

    return last_rate
