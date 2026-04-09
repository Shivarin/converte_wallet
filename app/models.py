from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict


@dataclass
class ConversionResult:
    amount: float
    rate: float
    from_currency: str
    to_currency: str
    provider: str = ""
    fetched_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    cached: bool = False

    def __str__(self) -> str:
        if self.amount < 0.001 or self.rate < 0.001:
            amount_str = f"{self.amount:.8f}"
            rate_str = f"{self.rate:.8g}"
        else:
            amount_str = f"{self.amount:.2f}"
            rate_str = f"{self.rate:.6g}"
        return (
            f"{amount_str} {self.to_currency}"
            f"  (1 {self.from_currency} = {rate_str} {self.to_currency}"
            f", via {self.provider})"
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "amount": self.amount,
            "rate": self.rate,
            "from_currency": self.from_currency,
            "to_currency": self.to_currency,
            "provider": self.provider,
            "fetched_at": self.fetched_at.isoformat(),
            "cached": self.cached,
        }
