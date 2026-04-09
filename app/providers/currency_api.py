from datetime import date
from typing import Dict, Optional

import requests

from .base import BaseProvider


class CurrencyAPIProvider(BaseProvider):
    """
    Free provider backed by https://github.com/fawazahmed0/exchange-api.
    No API key required. CDN-cached, effectively no rate limit.

    Supports 150+ currencies including:
    - All major fiat: USD, EUR, RUB, GBP, JPY, CNY, ...
    - Crypto: BTC, ETH, SOL, BNB, DOGE, ADA, XRP, ...

    Also supports historical rates by date.
    """

    name = "currency-api"

    _CDN = "https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@{date}/v1/currencies/{base}.json"
    _FALLBACK = "https://{date}.currency-api.pages.dev/v1/currencies/{base}.json"

    def __init__(self, timeout: int = 10):
        self._timeout = timeout
        self._session = requests.Session()
        self._session.headers["User-Agent"] = "converte_wallet/0.1"

    def get_rates(self, base: str, on_date: Optional[date] = None) -> Dict[str, float]:
        base_lower = base.lower()
        date_str = on_date.isoformat() if on_date else "latest"

        urls = [
            self._CDN.format(date=date_str, base=base_lower),
            self._FALLBACK.format(date=date_str, base=base_lower),
        ]

        last_exc: Exception = RuntimeError("no urls tried")
        for url in urls:
            try:
                resp = self._session.get(url, timeout=self._timeout)
                resp.raise_for_status()
                data = resp.json()
                rates = {k.upper(): float(v) for k, v in data[base_lower].items()}
                rates[base.upper()] = 1.0
                return rates
            except Exception as exc:
                last_exc = exc

        raise ConnectionError(
            f"CurrencyAPIProvider: failed to fetch rates for '{base}': {last_exc}"
        )

    def rate_at(self, on_date: date, base: str) -> Dict[str, float]:
        """Historical rates for a specific date."""
        return self.get_rates(base, on_date=on_date)
