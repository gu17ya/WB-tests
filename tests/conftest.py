from decimal import Decimal

import pytest

import config
from helpers.order_helpers import parse_balances
from models.market import Market
from services.whitebit_public_service import WhiteBitPublicService
from services.whitebit_trade_service import WhiteBitTradeService
from validators.response_validators import validate_status


@pytest.fixture(scope="session")
def public_service():
    service = WhiteBitPublicService()
    yield service
    service.close()


@pytest.fixture(scope="session")
def trade_service():
    service = WhiteBitTradeService()
    validate_status(service.get_balance())  # fail fast on bad keys / permissions
    yield service
    service.close()


@pytest.fixture(scope="session")
def market(public_service) -> Market:
    markets = validate_status(public_service.get_markets())
    return Market.from_dict(next(m for m in markets if m["name"] == config.MARKET))


@pytest.fixture
def last_price(public_service, market) -> Decimal:
    return Decimal(validate_status(public_service.get_ticker())[market.name]["last_price"])


@pytest.fixture
def get_balances(trade_service, market):
    """Call to get a fresh snapshot of the market's two assets."""
    return lambda: parse_balances(validate_status(trade_service.get_balance()), market.stock, market.money)


@pytest.fixture
def opened_orders(trade_service, market):
    """Order ids put here are cancelled after the test, even if it failed."""
    orders = []
    yield orders
    for order_id in orders:
        trade_service.cancel_order(market.name, order_id)
