from datetime import date
from typing import Dict, Optional

import requests

from .base import BaseProvider


_SUPPORTED = frozenset({
    "AUD", "BGN", "BRL", "CAD", "CHF", "CNY", "CZK", "DKK",
    "EUR", "GBP", "HKD", "HUF", "IDR", "ILS", "INR", "ISK",
    "JPY", "KRW", "MXN", "MYR", "NOK", "NZD", "PHP", "PLN",
    "RON", "SEK", "SGD", "THB", "TRY", "USD", "ZAR",
})


class FrankfurterProvider(BaseProvider):
    """
    ECB-based fiat provider. Free, no API key, ~33 currencies.
    Source: https://www.frankfurter.app

    Does NOT support: RUB (dropped by ECB in 2022), crypto.
    Use CurrencyAPIProvider for RUB or crypto.
    """

    name = "frankfurter"
    BASE_URL = "https://api.frankfurter.app"

    def __init__(self, timeout: int = 10):
        self._timeout = timeout
        self._session = requests.Session()
        self._session.headers["User-Agent"] = "converte_wallet/0.1"

    def supports(self, currency: str) -> bool:
        return currency.upper() in _SUPPORTED

    def get_rates(self, base: str, on_date: Optional[date] = None) -> Dict[str, float]:
        base = base.upper()
        if base not in _SUPPORTED:
            raise ValueError(
                f"FrankfurterProvider: unsupported currency '{base}'. "
                f"Use CurrencyAPIProvider for RUB or crypto."
            )

        endpoint = on_date.isoformat() if on_date else "latest"
        resp = self._session.get(
            f"{self.BASE_URL}/{endpoint}",
            params={"from": base},
            timeout=self._timeout,
        )
        resp.raise_for_status()
        data = resp.json()
        rates = {k.upper(): float(v) for k, v in data["rates"].items()}
        rates[base] = 1.0
        return rates

    def rate_at(self, on_date: date, base: str) -> Dict[str, float]:
        """Historical rates for a specific date."""
        return self.get_rates(base, on_date=on_date)
