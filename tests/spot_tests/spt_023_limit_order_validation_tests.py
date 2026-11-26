from collections.abc import Callable
from decimal import Decimal

import pytest

from data.test_data import LIMIT_ORDER_AMOUNT, POST_ONLY_WITH_IOC_ERROR
from helpers.order_helpers import generate_client_order_id, get_passive_price
from models.market import Market
from services.whitebit_trade_service import WhiteBitTradeService
from utils.step import logger
from validators.order_validators import validate_balance_change
from validators.response_validators import validate_status
from http import HTTPStatus


@pytest.mark.parametrize("side", ["buy"])
def test_post_only_with_ioc_is_rejected(
    trade_service: WhiteBitTradeService,
    market: Market,
    last_price: Decimal,
    get_balances: Callable[[], dict],
    opened_orders: list[int],
    side: str,
) -> None:
    """TC-23. Limit order with postOnly and ioc both true is rejected and not created."""

    logger.info("Preconditions: valid limit order data and balances before the request")
    price = get_passive_price(last_price, side, market.money_prec)
    amount = LIMIT_ORDER_AMOUNT
    client_order_id = generate_client_order_id()
    before = get_balances()

    logger.info("STEP 1. Send limit order with postOnly and ioc both true")
    response_create_limit_order = trade_service.create_limit_order(
        market.name, side, str(amount), str(price), postOnly=True, ioc=True, clientOrderId=client_order_id
    )
    if response_create_limit_order.status_code == 200:
        opened_orders.append(response_create_limit_order.json()["orderId"])  # cleanup if the check is broken

    error = validate_status(response_create_limit_order, HTTPStatus.UNPROCESSABLE_ENTITY)
    assert error == POST_ONLY_WITH_IOC_ERROR

    logger.info("STEP 2. Check active orders and balances")
    response_active_orders = trade_service.get_active_orders(market.name)
    active_orders = validate_status(response_active_orders)
    active_client_ids = [o["clientOrderId"] for o in active_orders]

    assert client_order_id not in active_client_ids, "rejected order is among active orders"

    after = get_balances()
    for asset in (market.stock, market.money):
        validate_balance_change(before, after, asset, available=0, freeze=0, precision=market.precision(asset))
