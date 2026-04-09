import argparse
import sys

from .converter import Converter


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="converte",
        description="converte_wallet — конвертация валют из командной строки",
    )
    parser.add_argument("amount", type=float, help="Сумма для конвертации")
    parser.add_argument("from_currency", type=str, help="Исходная валюта (например USD)")
    parser.add_argument("to_currency", type=str, help="Целевая валюта (например EUR или BTC)")
    parser.add_argument(
        "--provider",
        choices=["currency-api", "frankfurter", "coingecko"],
        default="currency-api",
        help="Провайдер курсов (по умолчанию currency-api)",
    )

    args = parser.parse_args()

    from .providers import CurrencyAPIProvider, FrankfurterProvider, CoinGeckoProvider
    provider_map = {
        "currency-api": CurrencyAPIProvider,
        "frankfurter": FrankfurterProvider,
        "coingecko": CoinGeckoProvider,
    }
    provider = provider_map[args.provider]()

    try:
        c = Converter(provider=provider)
        result = c.convert(args.amount, args.from_currency, args.to_currency)
        print(result)
    except Exception as exc:
        print(f"Ошибка: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
