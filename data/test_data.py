from decimal import Decimal

SIDES = ["buy", "sell"]

MARKET_ORDER_AMOUNT = {"buy": Decimal("10"), "sell": Decimal("0.0002")}  # buy in DUSDT, sell in DBTC
LIMIT_ORDER_AMOUNT = Decimal("0.0002")  # DBTC

TAKER_ROLE = 2

POST_ONLY_WITH_IOC_ERROR = {
    "code": 37,
    "message": "Validation failed",
    "errors": {"ioc": ["Either IOC or PostOnly flag in true state is allowed."]},
}
