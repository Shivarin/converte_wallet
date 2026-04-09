import pytest
from app.providers import StaticProvider


def test_static_direct_rates():
    p = StaticProvider({"USD": {"EUR": 0.92, "RUB": 90.0}})
    rates = p.get_rates("USD")
    assert rates["EUR"] == pytest.approx(0.92)
    assert rates["RUB"] == pytest.approx(90.0)
    assert rates["USD"] == pytest.approx(1.0)


def test_static_inverse():
    p = StaticProvider({"USD": {"EUR": 0.92}})
    rates = p.get_rates("EUR")
    assert "USD" in rates
    assert rates["USD"] == pytest.approx(1.0 / 0.92, rel=1e-5)
    assert rates["EUR"] == pytest.approx(1.0)


def test_static_missing_raises():
    p = StaticProvider({"USD": {"EUR": 0.92}})
    with pytest.raises(ValueError, match="JPY"):
        p.get_rates("JPY")


def test_static_case_insensitive():
    p = StaticProvider({"usd": {"eur": 0.92, "rub": 90.0}})
    rates = p.get_rates("USD")
    assert "EUR" in rates
    assert "RUB" in rates


def test_static_crypto():
    p = StaticProvider({"USD": {"BTC": 0.000022, "ETH": 0.00033}})
    rates = p.get_rates("USD")
    assert rates["BTC"] == pytest.approx(0.000022)
    assert rates["ETH"] == pytest.approx(0.00033)


def test_static_inverse_crypto():
    p = StaticProvider({"USD": {"BTC": 0.000022}})
    rates = p.get_rates("BTC")
    assert "USD" in rates
    assert rates["USD"] == pytest.approx(1.0 / 0.000022, rel=1e-5)
