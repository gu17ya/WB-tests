from decimal import Decimal

import pytest

from data.test_data import LIMIT_ORDER_AMOUNT, SIDES
from helpers.order_helpers import generate_client_order_id, get_passive_price
from validators.order_validators import validate_balance_change, validate_order
from helpers.waiter_helpers import wait_until
from validators.response_validators import validate_status


@pytest.mark.parametrize("side", SIDES)
def test_limit_order_create_and_cancel(trade_service, market, last_price, get_balances, opened_orders, side):
    price = get_passive_price(last_price, side, market.money_prec)
    amount = LIMIT_ORDER_AMOUNT
    locked_asset, locked = (market.money, amount * price) if side == "buy" else (market.stock, amount)
    other_asset = market.stock if locked_asset == market.money else market.money
    before = get_balances()
    client_order_id = generate_client_order_id()

    def is_active(order_id) -> bool:
        return order_id in [o["orderId"] for o in validate_status(trade_service.get_active_orders(market.name))]

    # 1. create
    order = validate_status(
        trade_service.create_limit_order(market.name, side, str(amount), str(price), clientOrderId=client_order_id)
    )
    opened_orders.append(order["orderId"])

    validate_order(
        order, market=market.name, side=side, type="limit", clientOrderId=client_order_id,
        price=price, amount=amount, left=amount, dealStock=Decimal(0),
    )

    # 2. order is active, funds are locked
    assert wait_until(lambda: is_active(order["orderId"])), "order did not appear in active orders"
    locked_state = get_balances()
    validate_balance_change(before, locked_state, locked_asset, available=-locked, freeze=locked, precision=market.precision(locked_asset))
    validate_balance_change(before, locked_state, other_asset, available=0, freeze=0, precision=market.precision(other_asset))

    # 3. cancel
    cancelled = validate_status(trade_service.cancel_order(market.name, order["orderId"]))
    opened_orders.remove(order["orderId"])

    validate_order(cancelled, orderId=order["orderId"], clientOrderId=client_order_id, dealStock=Decimal(0))

    # 4. order is gone, funds are back
    assert wait_until(lambda: not is_active(order["orderId"])), "order is still active after cancel"
    after = get_balances()
    for asset in (market.stock, market.money):
        validate_balance_change(before, after, asset, available=0, freeze=0, precision=market.precision(asset))
