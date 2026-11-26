from collections.abc import Callable
from decimal import Decimal

import pytest

from data.test_data import MARKET_ORDER_AMOUNT
from helpers.order_helpers import generate_client_order_id
from models.market import Market
from services.whitebit_trade_service import WhiteBitTradeService
from utils.step import logger
from validators.order_validators import (
    assert_close,
    validate_balance_change,
    validate_deal_fee,
    validate_market_order_fill,
    validate_order,
)
from validators.response_validators import validate_response_time, validate_status


@pytest.mark.parametrize("side", ["buy"])
def test_market_order(
    trade_service: WhiteBitTradeService,
    market: Market,
    get_balances: Callable[[], dict],
    side: str,
) -> None:
    """TC-1. Market order: executed history, deals, taker fee and balances are consistent."""

    logger.info("Preconditions: taker fee rate and balances before the order")
    fee_info = validate_status(trade_service.get_market_fee(market.name))
    taker_rate = Decimal(fee_info["taker"]) / 100  # API returns percent: "0.1" = 0.1 %
    amount = MARKET_ORDER_AMOUNT[side]
    client_order_id = generate_client_order_id()
    before = get_balances()

    logger.info("STEP 1. Send market order")
    response_create_market_order = trade_service.create_market_order(market.name, side, str(amount), clientOrderId=client_order_id)
    order = validate_status(response_create_market_order)
    order_id = order["orderId"]
    deal_stock = Decimal(order["dealStock"])
    deal_money = Decimal(order["dealMoney"])

    validate_response_time(response_create_market_order)
    validate_order(order, market=market.name, side=side, type="market", clientOrderId=client_order_id)
    validate_market_order_fill(order, side, amount, market.stock_prec)

    logger.info("STEP 2. Check order history")
    response_get_order_history = trade_service.get_order_history(market.name, order_id)
    history = validate_status(response_get_order_history)[market.name]

    assert len(history) == 1
    validate_order(history[0], status=order["status"], dealStock=deal_stock, dealMoney=deal_money)

    logger.info("STEP 3. Check order deals")
    response_get_order_deals = trade_service.get_order_deals(order_id)
    deals = validate_status(response_get_order_deals)["records"]
    assert deals, "order has no deals"

    fee_asset = deals[0]["feeAsset"]
    total_stock = sum(Decimal(d["amount"]) for d in deals)
    total_money = sum(Decimal(d["deal"]) for d in deals)
    total_fee = sum(Decimal(d["fee"]) for d in deals)

    assert all(d["dealOrderId"] == order_id for d in deals)
    assert fee_asset in (market.stock, market.money)
    for deal in deals:
        validate_deal_fee(deal, market.money, taker_rate, market.precision(fee_asset))
    assert_close(total_stock, deal_stock, market.stock_prec, "sum of deal amounts")
    assert_close(total_money, deal_money, market.money_prec, "sum of deal totals")
    assert_close(total_fee, order["dealFee"], market.precision(fee_asset), "dealFee")

    logger.info("STEP 4. Check balances")
    if side == "buy":
        expected = {market.stock: deal_stock, market.money: -deal_money}
    if side == "sell":
        expected = {market.stock: -deal_stock, market.money: deal_money}
    expected[fee_asset] -= total_fee
    after = get_balances()

    for asset, delta in expected.items():
        validate_balance_change(before, after, asset, available=delta, freeze=0, precision=market.precision(asset))
