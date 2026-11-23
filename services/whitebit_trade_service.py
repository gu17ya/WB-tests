from services.whitebit_base_service import WhiteBitBaseService
from utils.step import step


class WhiteBitTradeService(WhiteBitBaseService):
    """Private HTTP API v4 — spot trading."""

    @step("Get trade balance")
    def get_balance(self):
        return self._post("/api/v4/trade-account/balance")

    @step("Get market fee for {market}")
    def get_market_fee(self, market: str):
        return self._post("/api/v4/market/fee", market=market)

    @step("Create market order: {side} {amount} on {market}")
    def create_market_order(self, market: str, side: str, amount: str, **extra):
        return self._post("/api/v4/order/market", market=market, side=side, amount=amount, **extra)

    @step("Create limit order: {side} {amount} at {price} on {market} {extra}")
    def create_limit_order(self, market: str, side: str, amount: str, price: str, **extra):
        return self._post("/api/v4/order/new", market=market, side=side, amount=amount, price=price, **extra)

    @step("Cancel order {order_id} on {market}")
    def cancel_order(self, market: str, order_id: int):
        return self._post("/api/v4/order/cancel", market=market, orderId=order_id)

    @step("Get active orders on {market}")
    def get_active_orders(self, market: str):
        return self._post("/api/v4/orders", market=market, limit=100)

    @step("Get order {order_id} from executed history")
    def get_order_history(self, market: str, order_id: int):
        return self._post("/api/v4/trade-account/order/history", market=market, orderId=order_id)

    @step("Get deals of order {order_id}")
    def get_order_deals(self, order_id: int):
        return self._post("/api/v4/trade-account/order", orderId=order_id, limit=100)
