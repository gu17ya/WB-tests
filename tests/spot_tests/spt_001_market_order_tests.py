from decimal import Decimal

import pytest

from data.test_data import MARKET_ORDER_AMOUNT
from helpers.order_helpers import generate_client_order_id
from validators.order_validators import (
    assert_close,
    validate_balance_change,
    validate_deal_fee,
    validate_market_order_fill,
    validate_order,
)
from validators.response_validators import validate_response_time, validate_status


@pytest.mark.parametrize("side", ["buy"])
def test_market_order(trade_service, market, get_balances, side):
    taker_rate = Decimal(validate_status(trade_service.get_market_fee(market.name))["taker"]) / 100
    amount = MARKET_ORDER_AMOUNT[side]
    before = get_balances()
    client_order_id = generate_client_order_id()

    # 1. create
    response = trade_service.create_market_order(market.name, side, str(amount), clientOrderId=client_order_id)
    order = validate_status(response)

    validate_response_time(response)
    validate_order(order, market=market.name, side=side, type="market", clientOrderId=client_order_id)
    validate_market_order_fill(order, side, amount, market.stock_prec)
    deal_stock, deal_money = Decimal(order["dealStock"]), Decimal(order["dealMoney"])

    # 2. order is in executed history
    history = validate_status(trade_service.get_order_history(market.name, order["orderId"]))[market.name]
    assert len(history) == 1
    validate_order(history[0], status=order["status"], dealStock=deal_stock, dealMoney=deal_money)

    # 3. deals and fee
    deals = validate_status(trade_service.get_order_deals(order["orderId"]))["records"]
    assert deals and all(d["dealOrderId"] == order["orderId"] for d in deals)
    fee_asset = deals[0]["feeAsset"]
    assert fee_asset in (market.stock, market.money)
    for deal in deals:
        validate_deal_fee(deal, market.money, taker_rate, market.precision(fee_asset))
    fee = sum(Decimal(d["fee"]) for d in deals)
    assert_close(sum(Decimal(d["amount"]) for d in deals), deal_stock, market.stock_prec, "sum of deal amounts")
    assert_close(sum(Decimal(d["deal"]) for d in deals), deal_money, market.money_prec, "sum of deal totals")
    assert_close(fee, order["dealFee"], market.precision(fee_asset), "dealFee")

    # 4. balances
    sign = 1 if side == "buy" else -1
    expected = {market.stock: sign * deal_stock, market.money: -sign * deal_money}
    expected[fee_asset] -= fee
    after = get_balances()
    for asset, delta in expected.items():
        validate_balance_change(before, after, asset, available=delta, freeze=0, precision=market.precision(asset))
