from decimal import ROUND_DOWN, Decimal
from uuid import uuid4


def generate_client_order_id() -> str:
    return f"at-{uuid4().hex[:20]}"


def get_passive_price(last_price: Decimal, side: str, precision: int) -> Decimal:
    """20% below the market for buy, 20% above for sell, so the order stays in the book."""
    factor = Decimal("0.8") if side == "buy" else Decimal("1.2")
    return (last_price * factor).quantize(Decimal(1).scaleb(-precision), rounding=ROUND_DOWN)


def parse_balances(body: dict, *assets: str) -> dict:
    """{"DBTC": {"available": Decimal, "freeze": Decimal}, ...}"""
    return {
        asset: {key: Decimal(body.get(asset, {}).get(key, "0")) for key in ("available", "freeze")}
        for asset in assets
    }
