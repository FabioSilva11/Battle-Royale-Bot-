import random
from typing import Tuple
from datetime import datetime, timedelta, timezone

from models import User
from config import MAX_SHIELDS, BASE_ROUBOS, ROUBOS_RESET_INTERVAL_MINUTES


def _today_str() -> str:
    # Usa UTC para simplificar o controle por dia
    return datetime.now(timezone.utc).date().isoformat()


class GameService:
    @property
    def welcome_message(self) -> str:
        return (
            "Bem-vindo ao Battle Royale Bot!\n"
            "- 💰 Você começa com 100 moedas\n"
            "- 🔒 5 chances para roubar outros usuários\n"
            "- 🛡️ 1 escudo de proteção (máximo 3)\n"
            "- ♻️ As chances de roubar resetam a cada 2h (não acumulam)\n"
            "Use /regras para saber como jogar."
        )

    @property
    def regras_message(self) -> str:
        return (
            "Regras do jogo:\n"
            "1. Use /status para ver seu saldo, escudo e chances de roubo.\n"
            "2. Use /roubar @usuario para tentar roubar moedas.\n"
            "3. Use /doar <valor> @usuario para doar moedas. Limite: alvo pode receber até 2 doações por dia.\n"
            "4. Escudos protegem contra roubo, consumindo 1 por tentativa, até 3 (máximo).\n"
            "5. Chances de roubo resetam a cada 2 horas para o valor base e não acumulam.\n"
            "6. Use /loja para comprar escudos e /comprar_saldo <valor> para adquirir saldo via PIX (Mercado Pago).\n"
        )

    def format_status(self, user: User) -> str:
        self.reset_roubos_if_needed(user)
        return (
            f"Status de {user.user_name or user.nome or user.user_id}:\n"
            f"- 💰 Saldo: {user.saldo}\n"
            f"- 🛡️ Escudo (máximo {MAX_SHIELDS}): {user.escudo}\n"
            f"- 🔒 Chances de roubo: {user.roubos}\n"
            f"- 🎁 Recebimentos hoje: {self._recebimentos_hoje(user)} / 2\n"
        )

    def reset_roubos_if_needed(self, user: User) -> bool:
        try:
            now = datetime.utcnow()
            if user.last_roubo_reset:
                last = datetime.fromisoformat(user.last_roubo_reset)
            else:
                last = now - timedelta(minutes=ROUBOS_RESET_INTERVAL_MINUTES + 1)
            if now - last >= timedelta(minutes=ROUBOS_RESET_INTERVAL_MINUTES):
                user.roubos = BASE_ROUBOS
                user.last_roubo_reset = now.isoformat()
                return True
            return False
        except Exception:
            # Em caso de qualquer erro, garantia de não acumular: força reset
            user.roubos = BASE_ROUBOS
            user.last_roubo_reset = datetime.utcnow().isoformat()
            return True

    def _reset_recebimentos_if_needed(self, user: User) -> None:
        today = _today_str()
        if user.recebimentos_data != today:
            user.recebimentos_data = today
            user.recebimentos_hoje = 0

    def _recebimentos_hoje(self, user: User) -> int:
        self._reset_recebimentos_if_needed(user)
        return user.recebimentos_hoje

    def donate(self, donor: User, target: User, amount: int) -> Tuple[User, User, str]:
        # validações básicas
        if donor.user_id == target.user_id:
            return donor, target, "Você não pode doar para si mesmo."
        if amount <= 0:
            return donor, target, "Informe um valor positivo para doar."
        if donor.saldo < amount:
            return donor, target, "Saldo insuficiente para doar."\

        # limite de recebimentos por dia
        self._reset_recebimentos_if_needed(target)
        if target.recebimentos_hoje >= 2:
            return donor, target, "Este usuário já atingiu o limite de 2 recebimentos hoje."

        # efetiva transferência
        donor.saldo -= amount
        target.saldo += amount
        target.recebimentos_hoje += 1
        msg = (
            f"Doação realizada: {donor.user_name or donor.user_id} enviou {amount} moedas "
            f"para {target.user_name or target.user_id}."
        )
        return donor, target, msg

    def attempt_robbery(self, attacker: User, target: User) -> Tuple[User, User, str]:
        # Reset das chances do atacante se necessário
        self.reset_roubos_if_needed(attacker)

        if attacker.user_id == target.user_id:
            return attacker, target, "Você não pode roubar a si mesmo."

        if attacker.roubos <= 0:
            return attacker, target, "Você não tem mais chances para roubar. Aguarde o reset."

        if attacker.saldo <= 0:
            return attacker, target, "Você precisa ter saldo para tentar roubar."

        if target.saldo <= 0:
            attacker.roubos -= 1
            return attacker, target, "O alvo não tem saldo disponível para roubo."

        # Escudo protege e consome 1
        if target.escudo > 0:
            target.escudo -= 1
            attacker.roubos -= 1
            # atacante perde moedas para o alvo (falha forçada)
            loss = min(attacker.saldo, random.randint(1, max(1, attacker.saldo // 2)))
            attacker.saldo -= loss
            target.saldo += loss
            return (
                attacker,
                target,
                (
                    "O alvo estava protegido por escudo. O roubo foi bloqueado, "
                    f"o alvo consumiu 1 escudo e você perdeu {loss} moedas para ele."
                ),
            )

        # Sem escudo: chance 50/50
        attacker.roubos -= 1
        success = random.choice([True, False])
        if success:
            # roubado entre 1 e até metade do saldo do alvo, pelo menos 1
            amount = min(target.saldo, random.randint(1, max(1, target.saldo // 2)))
            target.saldo -= amount
            attacker.saldo += amount
            msg = (
                f"Roubo bem-sucedido! Você ganhou {amount} moedas de {target.user_name or target.user_id}."
            )
            return attacker, target, msg
        else:
            # falha: atacante perde para o alvo
            loss = min(attacker.saldo, random.randint(1, max(1, attacker.saldo // 2)))
            attacker.saldo -= loss
            target.saldo += loss
            msg = (
                f"Roubo falhou! Você perdeu {loss} moedas para {target.user_name or target.user_id}."
            )
            return attacker, target, msg