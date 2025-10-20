from typing import Tuple
from datetime import datetime

from models import User
from config import SHIELD_PRICE, MAX_SHIELDS, MAX_RECHARGE_AMOUNT


class ShopService:
    def __init__(self) -> None:
        pass

    def buy_shield(self, user: User, quantity: int) -> Tuple[User, str]:
        if quantity <= 0:
            return user, "Informe uma quantidade válida maior que 0."

        available_slots = MAX_SHIELDS - user.escudo
        if available_slots <= 0:
            return user, f"Você já está com o máximo de escudos ({MAX_SHIELDS})."

        grant = min(available_slots, quantity)
        cost = SHIELD_PRICE * grant

        if user.saldo < cost:
            return user, (
                f"Saldo insuficiente. Você precisa de {cost} moedas para comprar {grant} escudo(s), "
                f"mas tem apenas {user.saldo}. Preço por escudo: {SHIELD_PRICE}."
            )

        user.saldo -= cost
        user.escudo += grant
        return user, f"Compra realizada: +{grant} escudo(s). Saldo restante: {user.saldo}."

    def recharge_balance(self, user: User, amount: int) -> Tuple[User, str]:
        if amount <= 0:
            return user, "Informe um valor positivo para recarregar."
        if amount > MAX_RECHARGE_AMOUNT:
            return user, f"Valor máximo por recarga é {MAX_RECHARGE_AMOUNT}."
        user.saldo += amount
        return user, f"Saldo recarregado com sucesso: +{amount}. Saldo atual: {user.saldo}."