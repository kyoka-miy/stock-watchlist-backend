class NumberUtils:
    @staticmethod
    def get_percent_and_round(val):
        if isinstance(val, (int, float)):
            return round(val * 100, 2)
        return None

    @staticmethod
    def get_round(val):
        if isinstance(val, (int, float)):
            return round(val, 2)
        return None

    @staticmethod
    def _to_float(val):
        if isinstance(val, (int, float)):
            return float(val)
        return None

    @staticmethod
    def format_compact_number(val, digits: int = 2):
        num = NumberUtils._to_float(val)
        if num is None:
            return None

        abs_num = abs(num)
        units = [
            (1_000_000_000_000, "T"),
            (1_000_000_000, "B"),
            (1_000_000, "M"),
            (1_000, "K"),
        ]

        for threshold, suffix in units:
            if abs_num >= threshold:
                return f"{num / threshold:.{digits}f}{suffix}"
        return f"{num:.{digits}f}"

    @staticmethod
    def format_yen(val):
        return f"¥{val}"

    @staticmethod
    def format_currency(val, symbol: str = "¥", compact: bool = False, digits: int = 2):
        num = NumberUtils._to_float(val)
        if num is None:
            return None

        if compact:
            compact_val = NumberUtils.format_compact_number(num, digits)
            return f"{symbol}{compact_val}" if compact_val is not None else None

        return f"{symbol}{num:.{digits}f}"

    @staticmethod
    def format_percent(val, ratio: bool = True, digits: int = 2, with_sign: bool = False):
        num = NumberUtils._to_float(val)
        if num is None:
            return None
        percentage = num * 100 if ratio else num
        sign = "+" if with_sign and percentage > 0 else ""
        return f"{sign}{percentage:.{digits}f}%"

    @staticmethod
    def add_percent_sign(val, digits: int = 2):
        num = NumberUtils._to_float(val)
        if num is None:
            return None
        return f"{num:.{digits}f}%"
