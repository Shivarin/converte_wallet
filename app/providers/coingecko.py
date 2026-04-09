from typing import Dict

import requests

from .base import BaseProvider


# CoinGecko coin IDs for popular tickers
CRYPTO_IDS: Dict[str, str] = {
    "BTC":   "bitcoin",
    "ETH":   "ethereum",
    "BNB":   "binancecoin",
    "SOL":   "solana",
    "XRP":   "ripple",
    "DOGE":  "dogecoin",
    "ADA":   "cardano",
    "AVAX":  "avalanche-2",
    "MATIC": "matic-network",
    "DOT":   "polkadot",
    "SHIB":  "shiba-inu",
    "LTC":   "litecoin",
    "TRX":   "tron",
    "UNI":   "uniswap",
    "LINK":  "chainlink",
    "TON":   "the-open-network",
    "USDT":  "tether",
    "USDC":  "usd-coin",
    "NOT":   "notcoin",
}

FIAT_CURRENCIES = frozenset({
    "USD", "EUR", "RUB", "GBP", "JPY", "CNY", "KRW", "INR",
    "BRL", "CAD", "AUD", "CHF", "MXN", "SGD", "HKD", "TRY",
    "SEK", "NOK", "DKK", "PLN", "CZK", "HUF", "UAH",
})

_ID_TO_TICKER = {v: k for k, v in CRYPTO_IDS.items()}


class CoinGeckoProvider(BaseProvider):
    """
    CoinGecko-based provider for crypto ↔ fiat conversions.
    Free tier, no API key required. Rate limit ~10-30 req/min.

    Supports all tickers in CRYPTO_IDS + major fiat currencies.
    """

    name = "coingecko"
    BASE_URL = "https://api.coingecko.com/api/v3"

    def __init__(self, timeout: int = 15):
        self._timeout = timeout
        self._session = requests.Session()
        self._session.headers["User-Agent"] = "converte_wallet/0.1"

    def supports(self, currency: str) -> bool:
        upper = currency.upper()
        return upper in CRYPTO_IDS or upper in FIAT_CURRENCIES

    def get_rates(self, base: str) -> Dict[str, float]:
        base = base.upper()
        if base in CRYPTO_IDS:
            return self._rates_from_crypto(base)
        if base in FIAT_CURRENCIES:
            return self._rates_from_fiat(base)
        raise ValueError(
            f"CoinGeckoProvider: unknown currency '{base}'. "
            f"Add it to CRYPTO_IDS or FIAT_CURRENCIES."
        )

    def _rates_from_crypto(self, ticker: str) -> Dict[str, float]:
        coin_id = CRYPTO_IDS[ticker]
        vs = ",".join(
            list(c.lower() for c in FIAT_CURRENCIES)
            + [c.lower() for c in CRYPTO_IDS if c != ticker]
        )
        resp = self._session.get(
            f"{self.BASE_URL}/simple/price",
            params={"ids": coin_id, "vs_currencies": vs},
            timeout=self._timeout,
        )
        resp.raise_for_status()
        data = resp.json().get(coin_id, {})
        rates: Dict[str, float] = {k.upper(): float(v) for k, v in data.items()}
        rates[ticker] = 1.0
        return rates

    def _rates_from_fiat(self, fiat: str) -> Dict[str, float]:
        coin_ids = ",".join(CRYPTO_IDS.values())
        resp = self._session.get(
            f"{self.BASE_URL}/simple/price",
            params={"ids": coin_ids, "vs_currencies": fiat.lower()},
            timeout=self._timeout,
        )
        resp.raise_for_status()
        data = resp.json()

        rates: Dict[str, float] = {fiat: 1.0}
        fiat_lower = fiat.lower()
        for coin_id, prices in data.items():
            ticker = _ID_TO_TICKER.get(coin_id)
            if ticker and fiat_lower in prices:
                price_in_fiat = float(prices[fiat_lower])
                if price_in_fiat > 0:
                    rates[ticker] = 1.0 / price_in_fiat
        return rates
