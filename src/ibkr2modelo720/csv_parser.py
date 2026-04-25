from __future__ import annotations

import csv
import dataclasses as dcs
import pathlib


@dcs.dataclass
class Position:
    isin: str
    description: str
    quantity: float
    currency: str
    value: float
    asset_class: str
    country_code: str = dcs.field(init=False)

    def __post_init__(self) -> None:
        self.country_code = self.isin[:2].upper()


def parse_ibkr_csv(path: str | pathlib.Path) -> list[Position]:
    """Parse an Interactive Brokers CSV portfolio export.

    Skips duplicate header rows and merges positions with the same ISIN
    by summing their quantity and value.
    """
    merged: dict[str, dict] = {}

    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            isin = row["ISIN"].strip()
            if isin == "ISIN":
                continue

            qty = float(row["Quantity"])
            val = float(row["PositionValue"])

            if isin in merged:
                merged[isin]["quantity"] += qty
                merged[isin]["value"] += val
            else:
                merged[isin] = {
                    "isin": isin,
                    "description": row["Description"].strip(),
                    "quantity": qty,
                    "currency": row["CurrencyPrimary"].strip(),
                    "value": val,
                    "asset_class": row["AssetClass"].strip(),
                }

    return [
        Position(
            isin=d["isin"],
            description=d["description"],
            quantity=d["quantity"],
            currency=d["currency"],
            value=d["value"],
            asset_class=d["asset_class"],
        )
        for d in merged.values()
    ]
