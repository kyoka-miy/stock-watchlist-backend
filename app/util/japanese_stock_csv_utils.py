import logging
from functools import lru_cache

import pandas as pd


_DATA_J_CSV_PATH = "app/data/data_j.csv"


@lru_cache(maxsize=1)
def _load_symbol_map() -> dict[str, dict[str, str]]:
    df = pd.read_csv(_DATA_J_CSV_PATH, dtype={"コード": str})
    # Keep only necessary columns and normalize missing values to empty strings.
    subset = df[["コード", "銘柄名", "33業種区分", "市場・商品区分"]].fillna("")
    return {
        row["コード"]: {
            "name": row["銘柄名"],
            "industry": row["33業種区分"],
            "market": row["市場・商品区分"],
        }
        for _, row in subset.iterrows()
    }


def _find_data_by_symbol(symbol: str) -> dict[str, str] | None:
    normalized_symbol = symbol.removesuffix(".T")
    return _load_symbol_map().get(normalized_symbol)


def get_japanese_name_by_symbol(symbol: str) -> str | None:
    try:
        data = _find_data_by_symbol(symbol)
        return data["name"] or None if data is not None else None
    except Exception as e:
        logging.error(
            f"Failed to read Japanese name from CSV for symbol: {symbol}, error: {e}"
        )
        return None


def get_japanese_industry_by_symbol(symbol: str) -> str | None:
    try:
        data = _find_data_by_symbol(symbol)
        return data["industry"] or None if data is not None else None
    except Exception as e:
        logging.error(
            f"Failed to read Japanese industry from CSV for symbol: {symbol}, error: {e}"
        )
        return None


def get_japanese_market_by_symbol(symbol: str) -> str | None:
    try:
        data = _find_data_by_symbol(symbol)
        if data is None or not data["market"]:
            return None
        # e.g. "プライム（内国株式）" -> "プライム"
        return data["market"].split("（", 1)[0]
    except Exception as e:
        logging.error(
            f"Failed to read Japanese market from CSV for symbol: {symbol}, error: {e}"
        )
        return None


def clear_japanese_stock_csv_cache() -> None:
    _load_symbol_map.cache_clear()
