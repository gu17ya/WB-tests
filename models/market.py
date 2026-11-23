from dataclasses import dataclass


@dataclass(frozen=True)
class Market:
    name: str
    stock: str
    money: str
    stock_prec: int
    money_prec: int

    @classmethod
    def from_dict(cls, data: dict) -> "Market":
        return cls(
            name=data["name"],
            stock=data["stock"],
            money=data["money"],
            stock_prec=int(data["stockPrec"]),
            money_prec=int(data["moneyPrec"]),
        )

    def precision(self, asset: str) -> int:
        return {self.stock: self.stock_prec, self.money: self.money_prec}[asset]
