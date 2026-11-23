import pytest

from data.test_data import LIMIT_ORDER_AMOUNT, POST_ONLY_WITH_IOC_ERROR
from helpers.order_helpers import generate_client_order_id, get_passive_price
from validators.order_validators import validate_balance_change
from validators.response_validators import validate_status


@pytest.mark.parametrize("side", ["buy"])
def test_post_only_with_ioc_is_rejected(trade_service, market, last_price, get_balances, opened_orders, side):
    price = get_passive_price(last_price, side, market.money_prec)
    amount = LIMIT_ORDER_AMOUNT
    before = get_balances()
    client_order_id = generate_client_order_id()

    # 1. send limit order with postOnly + ioc
    response = trade_service.create_limit_order(
        market.name, side, str(amount), str(price), postOnly=True, ioc=True, clientOrderId=client_order_id
    )
    if response.status_code == 200:
        opened_orders.append(response.json()["orderId"])  # cleanup if the check is broken

    assert validate_status(response, 422) == POST_ONLY_WITH_IOC_ERROR

    # 2. order is not created, balances are unchanged
    active_client_ids = [o["clientOrderId"] for o in validate_status(trade_service.get_active_orders(market.name))]
    assert client_order_id not in active_client_ids, "rejected order is among active orders"
    after = get_balances()
    for asset in (market.stock, market.money):
        validate_balance_change(before, after, asset, available=0, freeze=0, precision=market.precision(asset))
