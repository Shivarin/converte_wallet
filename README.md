# converte_wallet

> **Статус: в разработке** — API ядра активно пишется, интерфейсы ещё могут меняться.

Лёгкая Python-библиотека для конвертации валют. Работает из коробки — без регистрации и API-ключей. Поддерживает 150+ валют включая криптовалюты.

```python
from app import Converter

c = Converter()
print(c.convert(1, "RUB", "BTC"))    # 1 рубль в биткоин
print(c.convert(100, "USD", "EUR"))  # 100 долларов в евро
print(c.convert(0.5, "ETH", "RUB")) # 0.5 эфира в рубли
```

---

## Содержание

- [Установка](#установка)
- [Быстрый старт](#быстрый-старт)
- [Все методы Converter](#все-методы-converter)
- [Провайдеры курсов](#провайдеры-курсов)
- [Объект ConversionResult](#объект-conversionresult)
- [Кэширование](#кэширование)
- [CLI — командная строка](#cli--командная-строка)
- [Использование в проектах](#использование-в-проектах)
- [Разработка и тесты](#разработка-и-тесты)
- [Структура проекта](#структура-проекта)

---

## Установка

### Клонировать репозиторий

```bash
git clone https://github.com/your-username/converte_wallet.git
cd converte_wallet
```

### Установить зависимости

```bash
pip install requests
```

Или через файл зависимостей:

```bash
pip install -r requirements
```

### Установить как пакет (для импорта из других проектов)

```bash
pip install -e .
```

После этого в любом Python-файле на этой машине можно писать:

```python
from converte_wallet import Converter
```

> Без `pip install -e .` импорт работает только из корня репозитория как `from app import Converter`.

---

## Быстрый старт

### Одна конвертация

```python
from app import Converter

c = Converter()  # по умолчанию — бесплатный провайдер, не нужен ключ

result = c.convert(100, "USD", "EUR")

print(result.amount)       # 85.75 — сколько EUR получилось
print(result.rate)         # 0.8575 — курс 1 USD = ? EUR
print(result.from_currency)  # USD
print(result.to_currency)    # EUR
print(result.provider)     # currency-api
print(result)              # красивый вывод одной строкой
```

### Рубль в биткоин

```python
from app import Converter

c = Converter()
result = c.convert(1, "RUB", "BTC")
print(result)
# 0.00000018 BTC  (1 RUB = 1.79e-07 BTC, via currency-api)
```

### Криптовалюта в фиат

```python
result = c.convert(1, "BTC", "RUB")
print(result)
# 5586205.94 RUB  (1 BTC = 5586205 RUB, via currency-api)

result = c.convert(2, "ETH", "USD")
print(result)
# 4364.94 USD  (1 ETH = 2182.47 USD, via currency-api)
```

### Пакетная конвертация нескольких пар сразу

```python
from app import Converter

c = Converter()
results = c.convert_many([
    (100,  "USD", "EUR"),
    (1,    "RUB", "BTC"),
    (0.5,  "ETH", "USD"),
    (1000, "JPY", "CNY"),
])

for r in results:
    print(r)
```

### Только курс без конвертации

```python
rate = c.get_rate("USD", "RUB")
print(f"1 USD = {rate} RUB")
```

---

## Все методы Converter

### `Converter(provider=None, cache_ttl=3600)`

Создать конвертер.

| Параметр | Тип | По умолчанию | Описание |
|---|---|---|---|
| `provider` | `BaseProvider` | `CurrencyAPIProvider()` | Провайдер курсов |
| `cache_ttl` | `int` | `3600` | Время жизни кэша в секундах. `0` — без кэша |

```python
from app import Converter
from app.providers import CoinGeckoProvider, FrankfurterProvider

# по умолчанию — CurrencyAPIProvider, 150+ валют, бесплатно
c = Converter()

# конкретный провайдер
c = Converter(provider=CoinGeckoProvider())

# кэш на 10 минут
c = Converter(cache_ttl=600)

# без кэша (каждый раз свежий запрос)
c = Converter(cache_ttl=0)
```

---

### `convert(amount, from_currency, to_currency) → ConversionResult`

Конвертировать сумму.

```python
result = c.convert(1000, "RUB", "USD")
result = c.convert(0.01, "BTC", "EUR")
result = c.convert(1,    "rub", "btc")  # регистр не важен
```

---

### `convert_many(conversions) → List[ConversionResult]`

Конвертировать несколько пар за один вызов.

```python
results = c.convert_many([
    (100, "USD", "EUR"),
    (1,   "BTC", "RUB"),
    (50,  "GBP", "JPY"),
])
```

---

### `get_rate(from_currency, to_currency) → float`

Получить только курс.

```python
rate = c.get_rate("BTC", "USD")
print(rate)  # 55862.0
```

---

### `rate_at(on_date, from_currency, to_currency) → float`

Исторический курс на конкретную дату.

```python
from datetime import date
from app import Converter

c = Converter()
rate = c.rate_at(date(2023, 1, 1), "USD", "EUR")
print(f"USD/EUR на 1 января 2023: {rate}")
```

> Поддерживается провайдерами `CurrencyAPIProvider` и `FrankfurterProvider`.

---

### `invalidate_cache()`

Сбросить кэш, чтобы следующий запрос получил свежие курсы.

```python
c.invalidate_cache()
```

---

## Провайдеры курсов

Провайдер — это источник курсов. Можно использовать готовые или написать свой.

### CurrencyAPIProvider (по умолчанию)

```python
from app.providers import CurrencyAPIProvider

provider = CurrencyAPIProvider()
```

- Источник: [github.com/fawazahmed0/exchange-api](https://github.com/fawazahmed0/exchange-api)
- **Бесплатно**, API-ключ не нужен
- **150+ валют**: все основные фиат + BTC, ETH, SOL, BNB, DOGE, ADA и др.
- Поддерживает исторические курсы
- CDN-кэширование на стороне провайдера, лимитов практически нет

---

### FrankfurterProvider

```python
from app.providers import FrankfurterProvider

c = Converter(provider=FrankfurterProvider())
```

- Источник: [frankfurter.app](https://www.frankfurter.app) — данные ЕЦБ
- **Бесплатно**, ключ не нужен
- ~33 фиатные валюты (EUR, USD, GBP, JPY, CNY, ...)
- **Не поддерживает**: RUB (отключён ЕЦБ в 2022), крипту
- Поддерживает исторические курсы

---

### CoinGeckoProvider

```python
from app.providers import CoinGeckoProvider

c = Converter(provider=CoinGeckoProvider())
```

- Источник: [coingecko.com](https://www.coingecko.com)
- **Бесплатно**, ключ не нужен (лимит ~10–30 запросов/мин)
- Фокус на криптовалютах: BTC, ETH, SOL, BNB, DOGE, ADA, TON, ...
- Также поддерживает фиат: USD, EUR, RUB, GBP и др.

---

### StaticProvider (для тестов и офлайн)

```python
from app.providers import StaticProvider

provider = StaticProvider({
    "USD": {
        "EUR": 0.92,
        "RUB": 90.0,
        "BTC": 0.000022,
    }
})
c = Converter(provider=provider)
```

- Курсы задаются вручную — никакой сети не нужно
- Обратный курс считается автоматически: если есть USD→EUR, то EUR→USD тоже работает
- Идеально для юнит-тестов

---

### Написать свой провайдер

Достаточно унаследоваться от `BaseProvider` и реализовать один метод:

```python
from app.providers import BaseProvider
from typing import Dict

class MyProvider(BaseProvider):
    name = "my-provider"

    def get_rates(self, base: str) -> Dict[str, float]:
        # base — код базовой валюты в верхнем регистре, например "USD"
        # вернуть словарь: {код валюты: курс}
        # пример: {"EUR": 0.92, "RUB": 90.0, "USD": 1.0}
        rates = fetch_from_my_api(base)
        return rates

c = Converter(provider=MyProvider())
```

---

## Объект ConversionResult

Метод `convert()` возвращает объект `ConversionResult`, а не просто число.

| Поле | Тип | Описание |
|---|---|---|
| `amount` | `float` | Итоговая сумма в целевой валюте |
| `rate` | `float` | Курс: сколько `to_currency` за 1 `from_currency` |
| `from_currency` | `str` | Исходная валюта (всегда uppercase) |
| `to_currency` | `str` | Целевая валюта (всегда uppercase) |
| `provider` | `str` | Название провайдера |
| `fetched_at` | `datetime` | Время получения курса |
| `cached` | `bool` | Был ли результат из кэша |

```python
result = c.convert(100, "USD", "EUR")

# Использовать значение
print(result.amount)   # 85.75
print(result.rate)     # 0.8575

# Преобразовать в словарь (удобно для JSON/API-ответов)
data = result.to_dict()
# {
#   "amount": 85.75,
#   "rate": 0.8575,
#   "from_currency": "USD",
#   "to_currency": "EUR",
#   "provider": "currency-api",
#   "fetched_at": "2026-04-09T14:00:00+00:00",
#   "cached": False
# }

import json
print(json.dumps(result.to_dict(), indent=2))
```

---

## Кэширование

По умолчанию курсы кэшируются на 1 час в памяти. Это означает что за час делается только 1 HTTP-запрос на каждую пару валют — не важно сколько раз вызвать `convert()`.

```python
# Кэш на 5 минут
c = Converter(cache_ttl=300)

# Кэш на 24 часа
c = Converter(cache_ttl=86400)

# Без кэша (каждый раз свежий запрос к API)
c = Converter(cache_ttl=0)

# Принудительно сбросить кэш в любой момент
c.invalidate_cache()
```

---

## CLI — командная строка

После `pip install -e .` доступна команда `converte`:

```bash
converte 100 USD EUR
# 85.75 EUR  (1 USD = 0.8575 EUR, via currency-api)

converte 1 RUB BTC
# 0.00000018 BTC  (1 RUB = 1.79e-07 BTC, via currency-api)

converte 1 BTC RUB
# 5586205.94 RUB  (1 BTC = 5586206 RUB, via currency-api)
```

Выбор провайдера:

```bash
converte 100 USD EUR --provider frankfurter
converte 1 ETH USD  --provider coingecko
```

Без установки пакета — через Python:

```bash
python -m app.cli 100 USD EUR
python -m app.cli 1 RUB BTC
```

---

## Использование в проектах

### FastAPI

```python
from fastapi import FastAPI
from app import Converter

app = FastAPI()
converter = Converter()  # создаём один раз при старте

@app.get("/convert")
def convert(amount: float, from_currency: str, to_currency: str):
    result = converter.convert(amount, from_currency, to_currency)
    return result.to_dict()
```

### Telegram-бот (aiogram)

```python
from aiogram import Router
from app import Converter

router = Router()
converter = Converter()

@router.message()
async def handle(message):
    # ожидаем формат: "100 USD EUR"
    parts = message.text.split()
    if len(parts) == 3:
        amount, fc, tc = float(parts[0]), parts[1], parts[2]
        result = converter.convert(amount, fc, tc)
        await message.answer(str(result))
```

### Скрипт / CLI-утилита

```python
from app import Converter

c = Converter()

# портфель в разных валютах -> итого в USD
portfolio = {"BTC": 0.05, "ETH": 1.2, "RUB": 50000}
total_usd = sum(c.convert(amount, currency, "USD").amount
                for currency, amount in portfolio.items())
print(f"Итого: ${total_usd:.2f}")
```

### Jupyter / pandas

```python
import pandas as pd
from app import Converter

c = Converter()
currencies = ["EUR", "RUB", "GBP", "JPY", "BTC", "ETH"]
data = [c.convert(1, "USD", cur).to_dict() for cur in currencies]
df = pd.DataFrame(data)[["to_currency", "rate"]]
print(df)
```

---

## Разработка и тесты

### Запуск тестов

```bash
pip install pytest
python -m pytest tests/ -v
```

### Запуск демо

```bash
python main.py
```

### Добавить новый провайдер

1. Создать файл `app/providers/my_provider.py`
2. Унаследовать от `BaseProvider`, реализовать `get_rates()`
3. Добавить в `app/providers/__init__.py`

### Поддерживаемые валюты (примеры)

**Фиат:** USD, EUR, RUB, GBP, JPY, CNY, KRW, INR, BRL, CAD, AUD, CHF, TRY, PLN, UAH и 100+ других

**Крипто (через CurrencyAPIProvider):** BTC, ETH, BNB, SOL, XRP, DOGE, ADA, AVAX, DOT, SHIB, LTC, TRX, UNI, LINK, TON, USDT, USDC и многие другие

---

## Структура проекта

```
converte_wallet/
├── app/
│   ├── __init__.py         # Converter, ConversionResult, MemoryCache
│   ├── converter.py        # основной класс Converter
│   ├── models.py           # ConversionResult
│   ├── cache.py            # MemoryCache с TTL
│   ├── cli.py              # CLI entrypoint
│   └── providers/
│       ├── __init__.py     # экспорт всех провайдеров
│       ├── base.py         # BaseProvider — базовый класс
│       ├── static.py       # StaticProvider (офлайн/тесты)
│       ├── currency_api.py # CurrencyAPIProvider (дефолт, 150+ валют)
│       ├── frankfurter.py  # FrankfurterProvider (ECB данные)
│       └── coingecko.py    # CoinGeckoProvider (крипто)
├── tests/
│   ├── test_converter.py   # 14 тестов конвертера
│   └── test_providers.py   # 6 тестов провайдеров
├── main.py                 # демо запуска
├── pyproject.toml          # метаданные пакета
├── requirements            # зависимости
└── README.md
```

---

## Лицензия

MIT
