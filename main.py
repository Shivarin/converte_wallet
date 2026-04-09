"""
Демо — запускай напрямую: python main.py
Показывает основные возможности библиотеки.
"""

from app import Converter
from app.providers import StaticProvider, CurrencyAPIProvider


def demo_static():
    """Работает без интернета — удобно для тестов и разработки."""
    print("=" * 55)
    print("  StaticProvider (офлайн, без интернета)")
    print("=" * 55)

    provider = StaticProvider({
        "USD": {
            "EUR": 0.92,
            "RUB": 90.5,
            "GBP": 0.79,
            "BTC": 0.0000215,
            "ETH": 0.00032,
        }
    })
    c = Converter(provider=provider)

    print(c.convert(100,    "USD", "EUR"))
    print(c.convert(100,    "USD", "RUB"))
    print(c.convert(1,      "RUB", "BTC"))   # 1 рубль в биткоин
    print(c.convert(1,      "BTC", "RUB"))   # 1 биткоин в рубли
    print(c.convert(1,      "ETH", "USD"))
    print(c.convert(1000,   "RUB", "USD"))
    print()


def demo_live():
    """Реальные курсы с currency-api (бесплатно, без ключа)."""
    print("=" * 55)
    print("  CurrencyAPIProvider (реальные курсы, нужен интернет)")
    print("=" * 55)

    c = Converter()  # по умолчанию CurrencyAPIProvider

    pairs = [
        (100,   "USD", "EUR"),
        (100,   "USD", "RUB"),
        (1,     "RUB", "BTC"),   # 1 рубль в биткоин
        (1,     "BTC", "RUB"),   # 1 биткоин в рубли
        (0.5,   "ETH", "USD"),
        (1000,  "RUB", "USD"),
        (1,     "USD", "JPY"),
        (100,   "EUR", "CNY"),
    ]

    for amount, fc, tc in pairs:
        try:
            result = c.convert(amount, fc, tc)
            print(result)
        except Exception as exc:
            print(f"  {amount} {fc} → {tc}: ошибка — {exc}")

    print()
    print("Пакетная конвертация:")
    results = c.convert_many([
        (1,   "USD", "EUR"),
        (1,   "USD", "RUB"),
        (1,   "USD", "BTC"),
    ])
    for r in results:
        print(f"  {r}")


if __name__ == "__main__":
    demo_static()

    try:
        demo_live()
    except Exception as exc:
        print(f"Нет соединения или ошибка API: {exc}")
