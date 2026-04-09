from abc import ABC, abstractmethod
from typing import Dict


class BaseProvider(ABC):
    """
    Base class for all rate providers.

    Implement `get_rates(base)` to return a dict of {CURRENCY: rate}
    where rate means: 1 unit of `base` = rate units of that currency.
    """

    name: str = "base"

    @abstractmethod
    def get_rates(self, base: str) -> Dict[str, float]:
        """
        Return exchange rates relative to base currency.

        Example:
            get_rates("USD") -> {"EUR": 0.92, "RUB": 90.1, "BTC": 0.000022, ...}
        """

    def supports(self, currency: str) -> bool:
        """Return True if this provider can handle the given currency code."""
        return True
