from typing import Dict

from .base import BaseProvider


class StaticProvider(BaseProvider):
    """
    Provider with hard-coded rates. Useful for testing and offline use.

    Example:
        provider = StaticProvider({
            "USD": {"EUR": 0.92, "RUB": 90.0, "BTC": 0.000022}
        })

    Supports inverse rate calculation automatically:
    if you have USD->EUR, you can also convert EUR->USD.
    """

    name = "static"

    def __init__(self, rates: Dict[str, Dict[str, float]]):
        self._rates: Dict[str, Dict[str, float]] = {
            base.upper(): {quote.upper(): rate for quote, rate in quotes.items()}
            for base, quotes in rates.items()
        }

    def get_rates(self, base: str) -> Dict[str, float]:
        base = base.upper()

        if base in self._rates:
            result = dict(self._rates[base])
            result[base] = 1.0
            return result

        # Try inverse: find base as a quote in another base
        for stored_base, quotes in self._rates.items():
            if base in quotes:
                pivot = 1.0 / quotes[base]
                result = {k: v * pivot for k, v in quotes.items() if k != base}
                result[stored_base] = pivot
                result[base] = 1.0
                return result

        raise ValueError(f"StaticProvider: no rates available for '{base}'")
