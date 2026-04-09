# converte-wallet

<p align="center">
  <a href="https://pypi.org/project/converte-wallet/">
    <img src="https://img.shields.io/pypi/v/converte-wallet?color=blue&label=PyPI" alt="PyPI version">
  </a>
  <a href="https://pypi.org/project/converte-wallet/">
    <img src="https://img.shields.io/pypi/pyversions/converte-wallet" alt="Python versions">
  </a>
  <a href="https://pypi.org/project/converte-wallet/">
    <img src="https://img.shields.io/pypi/dm/converte-wallet?color=green" alt="Downloads">
  </a>
  <img src="https://img.shields.io/badge/license-MIT-lightgrey" alt="License">
  <img src="https://img.shields.io/badge/статус-в%20разработке-orange" alt="Status">
</p>

<p align="center">
  Лёгкая Python-библиотека для конвертации валют.<br>
  Работает без регистрации и API-ключей. 150+ валют, включая криптовалюты.
</p>

```python
from converte_wallet import Converter

c = Converter()
print(c.convert(1, "RUB", "BTC"))    # 1 рубль → биткоин
print(c.convert(100, "USD", "EUR"))  # 100 долларов → евро
print(c.convert(0.5, "ETH", "RUB")) # 0.5 эфира → рубли
```

---

## Установка

```bash
pip install converte-wallet
```

Зависимости: только `requests`. Поддерживается Python 3.9+.

---

## Содержание

- [Быстрый старт](#быстрый-старт)
- [Все методы](#все-методы)
- [Провайдеры курсов](#провайдеры-курсов)
- [ConversionResult](#conversionresult)
- [Кэширование](#кэширование)
- [CLI](#cli)
- [Интеграция в проекты](#интеграция-в-проекты)
- [Разработка](#разработка)

---

## Быстрый старт

### Базовая конвертация

```python
from converte_wallet import Converter

c = Converter()  # бесплатно, без ключей, работает сразу

result = c.convert(100, "USD", "EUR")
print(result.amount)   # 85.75
print(result.rate)     # 0.8575
print(result)          # 85.75 EUR  (1 USD = 0.8575 EUR, via currency-api)
```

### Рубль в биткоин

```python
result = c.convert(1, "RUB", "BTC")
print(result)
# 0.00000018 BTC  (1 RUB = 1.79e-07 BTC, via currency-api)
```

### Крипта в фиат

```python
print(c.convert(1,   "BTC", "RUB"))  # 1 BTC → рубли
print(c.convert(2,   "ETH", "USD"))  # 2 ETH → доллары
print(c.convert(100, "SOL", "EUR"))  # 100 SOL → евро
```

### Пакетная конвертация

```python
results = c.convert_many([
    (100,  "USD", "EUR"),
    (1,    "RUB", "BTC"),
    (0.5,  "ETH", "USD"),
    (1000, "JPY", "CNY"),
])
for r in results:
    print(r)
```

### Только курс

```python
rate = c.get_rate("BTC", "USD")
print(f"1 BTC = {rate} USD")
```

### Исторический курс

```python
from datetime import date
rate = c.rate_at(date(2023, 1, 1), "USD", "EUR")
print(f"USD/EUR на 01.01.2023: {rate}")
```

---

## Все методы

### `Converter(provider=None, cache_ttl=3600)`

```python
from converte_wallet import Converter
from converte_wallet.providers import CoinGeckoProvider

c = Converter()                           # по умолчанию: CurrencyAPIProvider
c = Converter(provider=CoinGeckoProvider())  # конкретный провайдер
c = Converter(cache_ttl=600)              # кэш на 10 минут
c = Converter(cache_ttl=0)               # без кэша
```

### `convert(amount, from_currency, to_currency) → ConversionResult`

```python
c.convert(100, "USD", "EUR")
c.convert(1,   "rub", "btc")   # регистр не важен
c.convert(0.001, "BTC", "RUB")
```

### `convert_many(conversions) → List[ConversionResult]`

```python
c.convert_many([
    (100, "USD", "EUR"),
    (1, "BTC", "RUB"),
])
```

### `get_rate(from_currency, to_currency) → float`

```python
rate = c.get_rate("USD", "RUB")  # 90.5
```

### `rate_at(on_date, from_currency, to_currency) → float`

```python
from datetime import date
c.rate_at(date(2024, 6, 15), "EUR", "USD")
```

### `invalidate_cache()`

```python
c.invalidate_cache()  # сбросить кэш, следующий запрос будет свежим
```

---

## Провайдеры курсов

| Провайдер | Валюты | Крипта | Ключ | История |
|---|---|---|---|---|
| `CurrencyAPIProvider` | 150+ | ✅ | Не нужен | ✅ |
| `FrankfurterProvider` | ~33 фиат | ❌ | Не нужен | ✅ |
| `CoinGeckoProvider` | фиат + крипта | ✅ | Не нужен | ❌ |
| `StaticProvider` | любые | ✅ | — | ❌ |

### CurrencyAPIProvider — по умолчанию

```python
from converte_wallet.providers import CurrencyAPIProvider

c = Converter(provider=CurrencyAPIProvider())
```

Источник: [github.com/fawazahmed0/exchange-api](https://github.com/fawazahmed0/exchange-api). Бесплатно, CDN, лимитов нет. Поддерживает USD, EUR, RUB, GBP, BTC, ETH, SOL, BNB, DOGE и 140+ других.

### FrankfurterProvider — данные ЕЦБ

```python
from converte_wallet.providers import FrankfurterProvider

c = Converter(provider=FrankfurterProvider())
```

Источник: [frankfurter.app](https://www.frankfurter.app). Высокая надёжность для EUR-пар. Не поддерживает RUB (отключён ЕЦБ) и крипту.

### CoinGeckoProvider — фокус на крипте

```python
from converte_wallet.providers import CoinGeckoProvider

c = Converter(provider=CoinGeckoProvider())
```

Источник: [coingecko.com](https://www.coingecko.com). Бесплатно, ~30 запросов/мин. BTC, ETH, SOL, TON, BNB, DOGE, ADA, XRP и другие.

### StaticProvider — офлайн / тесты

```python
from converte_wallet.providers import StaticProvider

c = Converter(provider=StaticProvider({
    "USD": {"EUR": 0.92, "RUB": 90.0, "BTC": 0.000022}
}))
# Обратный курс считается автоматически: EUR→USD тоже работает
```

### Свой провайдер

```python
from converte_wallet.providers import BaseProvider
from typing import Dict

class MyProvider(BaseProvider):
    name = "my-source"

    def get_rates(self, base: str) -> Dict[str, float]:
        # base — код в верхнем регистре: "USD", "BTC", ...
        # вернуть: {"EUR": 0.92, "RUB": 90.0, ...}
        return fetch_from_my_api(base)

c = Converter(provider=MyProvider())
```

---

## ConversionResult

```python
result = c.convert(100, "USD", "EUR")

result.amount        # float — итоговая сумма в EUR
result.rate          # float — курс: 1 USD = ? EUR
result.from_currency # "USD"
result.to_currency   # "EUR"
result.provider      # "currency-api"
result.fetched_at    # datetime UTC
result.cached        # bool — из кэша или нет

str(result)          # "85.75 EUR  (1 USD = 0.8575 EUR, via currency-api)"
result.to_dict()     # dict — удобно для JSON/API-ответов
```

---

## Кэширование

```python
c = Converter(cache_ttl=3600)   # 1 час (по умолчанию)
c = Converter(cache_ttl=300)    # 5 минут
c = Converter(cache_ttl=86400)  # 24 часа
c = Converter(cache_ttl=0)      # без кэша

c.invalidate_cache()            # сбросить вручную
```

---

## CLI

После установки доступна команда `converte`:

```bash
converte 100 USD EUR
# 85.75 EUR  (1 USD = 0.8575 EUR, via currency-api)

converte 1 RUB BTC
# 0.00000018 BTC  (1 RUB = 1.79e-07 BTC, via currency-api)

converte 0.5 ETH USD --provider coingecko
converte 100 USD EUR --provider frankfurter
```

---

## Интеграция в проекты

### FastAPI

```python
from fastapi import FastAPI
from converte_wallet import Converter

app = FastAPI()
converter = Converter()

@app.get("/convert")
def convert(amount: float, from_currency: str, to_currency: str):
    return converter.convert(amount, from_currency, to_currency).to_dict()
```

### Telegram-бот (aiogram)

```python
from converte_wallet import Converter

converter = Converter()

@router.message()
async def handle(message):
    parts = message.text.split()  # "100 USD EUR"
    if len(parts) == 3:
        result = converter.convert(float(parts[0]), parts[1], parts[2])
        await message.answer(str(result))
```

### Pandas / Jupyter

```python
import pandas as pd
from converte_wallet import Converter

c = Converter()
currencies = ["EUR", "RUB", "GBP", "BTC", "ETH", "SOL"]
df = pd.DataFrame([c.convert(1, "USD", cur).to_dict() for cur in currencies])
print(df[["to_currency", "rate"]])
```

### Портфель в одной валюте

```python
from converte_wallet import Converter

c = Converter()
portfolio = {"BTC": 0.05, "ETH": 1.2, "RUB": 50000, "USD": 200}
total = sum(c.convert(amount, cur, "USD").amount for cur, amount in portfolio.items())
print(f"Портфель: ${total:.2f}")
```

---

## Разработка

```bash
git clone https://github.com/Shivarin/converte_wallet.git
cd converte_wallet
pip install -e .
```

### Запуск тестов

```bash
pip install pytest
python -m pytest tests/ -v
# 20 passed
```

### Запуск демо

```bash
python main.py
```

---

## Структура

```
converte_wallet/
├── app/
│   ├── converter.py          # Converter
│   ├── models.py             # ConversionResult
│   ├── cache.py              # MemoryCache
│   ├── cli.py                # CLI
│   └── providers/
│       ├── base.py           # BaseProvider
│       ├── currency_api.py   # CurrencyAPIProvider (дефолт)
│       ├── frankfurter.py    # FrankfurterProvider
│       ├── coingecko.py      # CoinGeckoProvider
│       └── static.py         # StaticProvider
└── tests/
    ├── test_converter.py     # 14 тестов
    └── test_providers.py     # 6 тестов
```

---

## Лицензия

MIT © [Shivarin](https://github.com/Shivarin)
