from datetime import date
from typing import List, Optional, Tuple, Union

from .cache import MemoryCache
from .models import ConversionResult
from .providers.base import BaseProvider


class Converter:
    """
    Main currency converter. Works out of the box — no API key needed.

    Uses CurrencyAPIProvider by default: 150+ currencies including crypto.

    Quick start:
        from converte_wallet import Converter

        c = Converter()
        print(c.convert(1, "RUB", "BTC"))   # 1 рубль в биткоин
        print(c.convert(100, "USD", "EUR"))
        print(c.convert(0.5, "ETH", "USD"))

    Custom provider:
        from converte_wallet.providers import CoinGeckoProvider
        c = Converter(provider=CoinGeckoProvider())

    No cache:
        c = Converter(cache_ttl=0)
    """

    def __init__(
        self,
        provider: Optional[BaseProvider] = None,
        cache_ttl: int = 3600,
    ):
        if provider is None:
            from .providers.currency_api import CurrencyAPIProvider
            provider = CurrencyAPIProvider()
        self.provider = provider
        self._cache = MemoryCache(ttl=cache_ttl) if cache_ttl > 0 else None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_rate(self, from_currency: str, to_currency: str) -> float:
        """
        Return the exchange rate: how much `to_currency` you get for 1 `from_currency`.

        Example:
            get_rate("USD", "RUB")  -> 90.5
            get_rate("RUB", "BTC")  -> 0.00000012
        """
        from_currency = from_currency.upper()
        to_currency = to_currency.upper()

        if from_currency == to_currency:
            return 1.0

        if self._cache is not None:
            cache_key = f"{self.provider.name}:{from_currency}:{to_currency}"
            cached = self._cache.get(cache_key)
            if cached is not None:
                return cached

        rates = self.provider.get_rates(from_currency)

        if to_currency not in rates:
            raise ValueError(
                f"Rate not found: {from_currency} → {to_currency}. "
                f"Provider '{self.provider.name}' returned {len(rates)} currencies. "
                f"Try a different provider or check the currency code."
            )

        rate = rates[to_currency]

        if self._cache is not None:
            self._cache.set(cache_key, rate)

        return rate

    def convert(
        self,
        amount: Union[int, float],
        from_currency: str,
        to_currency: str,
    ) -> ConversionResult:
        """
        Convert `amount` from `from_currency` to `to_currency`.

        Returns a ConversionResult with .amount, .rate, .provider, .fetched_at.
        """
        rate = self.get_rate(from_currency, to_currency)
        return ConversionResult(
            amount=amount * rate,
            rate=rate,
            from_currency=from_currency.upper(),
            to_currency=to_currency.upper(),
            provider=self.provider.name,
        )

    def convert_many(
        self,
        conversions: List[Tuple[Union[int, float], str, str]],
    ) -> List[ConversionResult]:
        """
        Convert multiple amounts at once.

        Example:
            results = c.convert_many([
                (100, "USD", "EUR"),
                (1,   "RUB", "BTC"),
                (0.5, "ETH", "USD"),
            ])
        """
        return [self.convert(amount, fc, tc) for amount, fc, tc in conversions]

    def rate_at(
        self,
        on_date: date,
        from_currency: str,
        to_currency: str,
    ) -> float:
        """
        Get the historical exchange rate on a specific date.
        Provider must support historical rates (CurrencyAPIProvider, FrankfurterProvider).
        """
        if not hasattr(self.provider, "rate_at"):
            raise NotImplementedError(
                f"Provider '{self.provider.name}' does not support historical rates."
            )
        rates = self.provider.rate_at(on_date, from_currency.upper())
        to_upper = to_currency.upper()
        if to_upper not in rates:
            raise ValueError(
                f"Historical rate not found: {from_currency} → {to_currency} on {on_date}"
            )
        return rates[to_upper]

    def invalidate_cache(self) -> None:
        """Clear all cached rates, forcing fresh fetch on next call."""
        if self._cache is not None:
            self._cache.clear()
