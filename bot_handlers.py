import telebot
from telebot import types

from storage import UserStorage
from game import GameService
from shop import ShopService
from models import User


class BotHandlers:
    def __init__(self, bot: telebot.TeleBot, storage: UserStorage, game: GameService):
        self.bot = bot
        self.storage = storage
        self.game = game
        self.shop = ShopService()

    def _extract_mention(self, text: str) -> str:
        if not text:
            return ""
        parts = text.strip().split()
        for p in parts:
            if p.startswith("@"):
                return p[1:]
        return ""

    def register(self):
        bot = self.bot

        @bot.message_handler(commands=['regras'])
        def regras_handler(message):
            bot.reply_to(message, self.game.regras_message)

        @bot.message_handler(content_types=['new_chat_members'])
        def welcome_handler(message):
            for user in message.new_chat_members:
                if not user.username:
                    bot.kick_chat_member(message.chat.id, user.id)
                    bot.reply_to(message, "Usuário sem @username removido. Configure um @ para jogar.")
                    continue
                # criar usuário se não existir
                u = self.storage.get(user.id)
                if not u:
                    u = User(
                        group_id=message.chat.id,
                        user_id=user.id,
                        nome=user.first_name,
                        sobrenome=user.last_name,
                        user_name=user.username,
                        saldo=100,
                        escudo=1,
                        roubos=5,
                    )
                    self.storage.add_if_absent(u)
                bot.send_message(message.chat.id, self.game.welcome_message)

        @bot.message_handler(commands=['status'])
        def status_handler(message):
            u = self.storage.get(message.from_user.id)
            if not u:
                bot.reply_to(message, "Você ainda não está registrado. Envie uma mensagem no grupo primeiro.")
                return
            # reseta chances se preciso
            if self.game.reset_roubos_if_needed(u):
                self.storage.upsert(u)
            bot.reply_to(message, self.game.format_status(u))

        @bot.message_handler(commands=['roubar'])
        def roubar_handler(message):
            attacker = self.storage.get(message.from_user.id)
            if not attacker:
                bot.reply_to(message, "Você ainda não está registrado.")
                return
            mention = self._extract_mention(message.text or "")
            if not mention:
                bot.reply_to(message, "Use: /roubar @usuario")
                return
            target = self.storage.get_by_username(mention)
            if not target:
                bot.reply_to(message, "Alvo não encontrado. Certifique-se que o usuário tem @username e já interagiu no grupo.")
                return

            # reset chances do atacante se preciso
            self.game.reset_roubos_if_needed(attacker)
            attacker, target, msg = self.game.attempt_robbery(attacker, target)
            self.storage.upsert(attacker)
            self.storage.upsert(target)
            bot.reply_to(message, msg)

        @bot.message_handler(commands=['doar'])
        def doar_handler(message):
            donor = self.storage.get(message.from_user.id)
            if not donor:
                bot.reply_to(message, "Você ainda não está registrado.")
                return
            parts = (message.text or '').split()
            if len(parts) < 3:
                bot.reply_to(message, "Uso: /doar <valor> @usuario")
                return
            try:
                amount = int(parts[1])
            except Exception:
                bot.reply_to(message, "Valor inválido. Ex: /doar 100 @usuario")
                return
            mention = self._extract_mention(message.text or "")
            if not mention:
                bot.reply_to(message, "Informe o usuário destino. Ex: /doar 100 @usuario")
                return
            target = self.storage.get_by_username(mention)
            if not target:
                bot.reply_to(message, "Alvo não encontrado. Certifique-se que o usuário tem @username e já interagiu no grupo.")
                return

            donor, target, msg = self.game.donate(donor, target, amount)
            self.storage.upsert(donor)
            self.storage.upsert(target)
            bot.reply_to(message, msg)

        @bot.message_handler(commands=['top10'])
        def top10_handler(message):
            users = list(self.storage.all_users().values())
            users.sort(key=lambda u: u.saldo, reverse=True)
            lines = ["Top 10 saldos:"]
            for i, u in enumerate(users[:10], start=1):
                lines.append(f"{i}. {u.user_name or u.nome or u.user_id} - {u.saldo}")
            bot.reply_to(message, "\n".join(lines))

        @bot.message_handler(commands=['loja'])
        def loja_handler(message):
            text = (
                "Loja do Battle Royale:\n"
                f"- Escudo: {self.shop_price_text()} (máximo 3)\n"
                "  Comando: /comprar_escudo <quantidade>\n"
                "- Comprar saldo via PIX: /comprar_saldo <valor>\n"
                "- Verificar pagamento: /verificar_pagamento <payment_id>\n"
            )
            bot.reply_to(message, text)

        @bot.message_handler(commands=['comprar_escudo'])
        def comprar_escudo_handler(message):
            u = self.storage.get(message.from_user.id)
            if not u:
                bot.reply_to(message, "Você ainda não está registrado.")
                return
            try:
                parts = (message.text or '').split()
                qty = int(parts[1]) if len(parts) > 1 else 1
            except Exception:
                bot.reply_to(message, "Uso: /comprar_escudo <quantidade> (ex: /comprar_escudo 2)")
                return
            u, msg = self.shop.buy_shield(u, qty)
            self.storage.upsert(u)
            bot.reply_to(message, msg)

        # PIX compra de saldo
        from payments import PaymentService
        pay = PaymentService()

        @bot.message_handler(commands=['comprar_saldo'])
        def comprar_saldo_handler(message):
            u = self.storage.get(message.from_user.id)
            if not u:
                bot.reply_to(message, "Você ainda não está registrado.")
                return
            try:
                parts = (message.text or '').split()
                amount = int(parts[1]) if len(parts) > 1 else 0
            except Exception:
                bot.reply_to(message, "Uso: /comprar_saldo <valor> (ex: /comprar_saldo 100)")
                return
            pid, info, img_bytes = pay.create_pix_payment(amount, u)
            if img_bytes:
                bot.send_photo(message.chat.id, img_bytes, caption=info)
            else:
                bot.reply_to(message, info)

        @bot.message_handler(commands=['verificar_pagamento'])
        def verificar_pagamento_handler(message):
            u = self.storage.get(message.from_user.id)
            if not u:
                bot.reply_to(message, "Você ainda não está registrado.")
                return
            parts = (message.text or '').split()
            if len(parts) < 2:
                bot.reply_to(message, "Uso: /verificar_pagamento <payment_id>")
                return
            payment_id = parts[1]
            status, credited, amount = pay.check_payment_status(payment_id)
            if status == 'approved' and credited:
                u.saldo += amount
                self.storage.upsert(u)
                bot.reply_to(message, f"Pagamento aprovado! Saldo adicionado: +{amount}. Saldo atual: {u.saldo}.")
            else:
                bot.reply_to(message, f"Status do pagamento: {status}. Quando for aprovado, use novamente este comando para creditar.")

    def shop_price_text(self) -> str:
        from config import SHIELD_PRICE
        return f"{SHIELD_PRICE} moedas por escudo"