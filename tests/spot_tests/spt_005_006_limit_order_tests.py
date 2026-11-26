from collections.abc import Callable
from decimal import Decimal

import pytest

from data.test_data import LIMIT_ORDER_AMOUNT, SIDES
from helpers.order_helpers import generate_client_order_id, get_passive_price
from models.market import Market
from services.whitebit_trade_service import WhiteBitTradeService
from helpers.waiter_helpers import wait_until
from utils.step import logger
from validators.order_validators import validate_balance_change, validate_order
from validators.response_validators import validate_status


@pytest.mark.parametrize("side", SIDES)
def test_limit_order_create_and_cancel(
    trade_service: WhiteBitTradeService,
    market: Market,
    last_price: Decimal,
    get_balances: Callable[[], dict],
    opened_orders: list[int],
    side: str,
) -> None:
    """TC-5/6. Limit order away from the market freezes funds; after cancel they are returned."""
    
    logger.info("Preconditions: price away from the market and balances before the order")
    price = get_passive_price(last_price, side, market.money_prec)
    amount = LIMIT_ORDER_AMOUNT
    client_order_id = generate_client_order_id()
    # buy freezes DUSDT (amount × price), sell freezes DBTC (amount)
    if side == "buy":
        locked_asset, other_asset, locked = market.money, market.stock, amount * price
    if side == "sell":
        locked_asset, other_asset, locked = market.stock, market.money, amount
    before = get_balances()

    def is_active(order_id: int) -> bool:
        active_orders = validate_status(trade_service.get_active_orders(market.name))
        return order_id in [o["orderId"] for o in active_orders]

    logger.info("STEP 1. Send limit order")
    response_create_limit_order = trade_service.create_limit_order(market.name, side, str(amount), str(price), clientOrderId=client_order_id)
    order = validate_status(response_create_limit_order)
    order_id = order["orderId"]
    opened_orders.append(order_id)

    validate_order(
        order,
        market=market.name,
        side=side,
        type="limit",
        clientOrderId=client_order_id,
        price=price,
        amount=amount,
        left=amount,
        dealStock=Decimal(0),
    )

    logger.info("STEP 2. Check active orders and balances after create")
    assert wait_until(lambda: is_active(order_id)), "order did not appear in active orders"

    frozen = get_balances()
    validate_balance_change(
        before, frozen, locked_asset, available=-locked, freeze=locked, precision=market.precision(locked_asset)
    )
    validate_balance_change(before, frozen, other_asset, available=0, freeze=0, precision=market.precision(other_asset))

    logger.info("STEP 3. Cancel limit order")
    response_cancel_order = trade_service.cancel_order(market.name, order_id)
    cancelled = validate_status(response_cancel_order)
    opened_orders.remove(order_id)

    validate_order(cancelled, orderId=order_id, clientOrderId=client_order_id, dealStock=Decimal(0))

    logger.info("STEP 4. Check active orders and balances after cancel")
    assert wait_until(lambda: not is_active(order_id)), "order is still active after cancel"

    after = get_balances()
    for asset in (market.stock, market.money):
        validate_balance_change(before, after, asset, available=0, freeze=0, precision=market.precision(asset))
