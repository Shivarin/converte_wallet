import pytest
from app import Converter
from app.providers import StaticProvider

RATES = {
    "USD": {
        "EUR": 0.92,
        "RUB": 90.0,
        "BTC": 0.000022,
        "GBP": 0.79,
        "ETH": 0.00033,
    }
}


@pytest.fixture
def converter():
    return Converter(provider=StaticProvider(RATES))


def test_convert_basic(converter):
    result = converter.convert(100, "USD", "EUR")
    assert result.amount == pytest.approx(92.0)
    assert result.rate == pytest.approx(0.92)
    assert result.from_currency == "USD"
    assert result.to_currency == "EUR"
    assert result.provider == "static"


def test_convert_same_currency(converter):
    result = converter.convert(100, "USD", "USD")
    assert result.amount == pytest.approx(100.0)
    assert result.rate == pytest.approx(1.0)


def test_convert_to_crypto(converter):
    result = converter.convert(1000, "USD", "BTC")
    assert result.amount == pytest.approx(0.022)


def test_convert_from_crypto_inverse(converter):
    result = converter.convert(1, "BTC", "USD")
    assert result.amount == pytest.approx(1.0 / 0.000022, rel=1e-5)


def test_convert_fiat_to_fiat_via_inverse(converter):
    # EUR is not in RATES directly, but USD->EUR=0.92 so EUR->USD = 1/0.92
    result = converter.convert(100, "EUR", "USD")
    assert result.amount == pytest.approx(100.0 / 0.92, rel=1e-5)


def test_convert_many(converter):
    results = converter.convert_many([
        (100, "USD", "EUR"),
        (50, "USD", "RUB"),
        (1, "USD", "BTC"),
    ])
    assert len(results) == 3
    assert results[0].amount == pytest.approx(92.0)
    assert results[1].amount == pytest.approx(4500.0)
    assert results[2].amount == pytest.approx(0.000022)


def test_get_rate(converter):
    assert converter.get_rate("USD", "RUB") == pytest.approx(90.0)


def test_get_rate_same(converter):
    assert converter.get_rate("USD", "USD") == pytest.approx(1.0)


def test_caching_is_consistent(converter):
    r1 = converter.convert(1, "USD", "EUR")
    r2 = converter.convert(1, "USD", "EUR")
    assert r1.amount == r2.amount


def test_invalidate_cache(converter):
    converter.convert(1, "USD", "EUR")
    converter.invalidate_cache()
    assert len(converter._cache) == 0


def test_unknown_currency_raises(converter):
    with pytest.raises((ValueError, Exception)):
        converter.convert(1, "USD", "XYZ_FAKE")


def test_result_str(converter):
    result = converter.convert(100, "USD", "EUR")
    s = str(result)
    assert "EUR" in s
    assert "USD" in s


def test_result_to_dict(converter):
    result = converter.convert(100, "USD", "EUR")
    d = result.to_dict()
    assert d["from_currency"] == "USD"
    assert d["to_currency"] == "EUR"
    assert d["amount"] == pytest.approx(92.0)
    assert "fetched_at" in d
    assert "provider" in d


def test_small_amount_crypto(converter):
    # 1 rub -> BTC equivalent (very small number)
    result = converter.convert(1, "RUB", "BTC")
    # RUB->BTC = (USD->BTC) / (USD->RUB) = 0.000022 / 90
    expected_rate = 0.000022 / 90.0
    assert result.rate == pytest.approx(expected_rate, rel=1e-4)
    assert result.amount == pytest.approx(expected_rate, rel=1e-4)
