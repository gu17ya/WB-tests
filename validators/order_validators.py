from decimal import Decimal

from data.test_data import TAKER_ROLE
from utils.step import step


def assert_close(actual, expected, precision: int, what: str) -> None:
    """Equal up to one unit of the asset precision."""
    actual, expected = Decimal(actual), Decimal(expected)
    assert abs(actual - expected) <= Decimal(1).scaleb(-precision), f"{what}: expected {expected}, got {actual}"


@step("Validate order fields: {expected}")
def validate_order(order: dict, **expected) -> None:
    """Compare order fields; Decimal expectations are compared numerically."""
    for field, value in expected.items():
        actual = Decimal(order[field]) if isinstance(value, Decimal) else order[field]
        assert actual == value, f"order.{field}: expected {value}, got {actual}"


@step("Validate taker fee of deal {deal[id]}")
def validate_deal_fee(deal: dict, money: str, taker_rate: Decimal, precision: int) -> None:
    """Market order deals are taker; fee = deal value in the fee asset × taker rate."""
    assert deal["role"] == TAKER_ROLE, f"deal {deal['id']} is not taker"
    base = deal["deal"] if deal["feeAsset"] == money else deal["amount"]
    assert_close(deal["fee"], Decimal(base) * taker_rate, precision, f"fee of deal {deal['id']}")


@step("Validate {asset} balance change: available {available}, freeze {freeze}")
def validate_balance_change(before: dict, after: dict, asset: str, available, freeze, precision: int) -> None:
    assert_close(after[asset]["available"] - before[asset]["available"], available, precision, f"{asset} available change")
    assert_close(after[asset]["freeze"] - before[asset]["freeze"], freeze, precision, f"{asset} freeze change")


@step("Validate market order fill: {side} {amount}")
def validate_market_order_fill(order: dict, side: str, amount: Decimal, stock_precision: int) -> None:
    """Sell is filled exactly. Buy by total may leave unspent "dust" smaller than one stock step,
    so the exchange closes it as PARTIALLY_FILLED; a bigger remainder means it was not filled."""
    deal_stock, deal_money = Decimal(order["dealStock"]), Decimal(order["dealMoney"])
    assert deal_stock > 0 and deal_money > 0, f"order not executed: dealStock={deal_stock}, dealMoney={deal_money}"
    if side == "sell":
        assert order["status"] == "FILLED", f"order.status: expected FILLED, got {order['status']}"
        assert deal_stock == amount, f"dealStock: expected {amount}, got {deal_stock}"
        return
    assert order["status"] in ("FILLED", "PARTIALLY_FILLED"), f"unexpected order.status {order['status']}"
    remainder = amount - deal_money
    one_step_cost = deal_money / deal_stock * Decimal(1).scaleb(-stock_precision)
    assert 0 <= remainder < one_step_cost, f"unspent {remainder} is not dust (one stock step costs {one_step_cost})"
