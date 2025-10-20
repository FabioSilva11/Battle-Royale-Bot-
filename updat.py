import telebot

from config import TELEGRAM_TOKEN
from storage import UserStorage
from game import GameService
from bot_handlers import BotHandlers


def create_bot() -> telebot.TeleBot:
    return telebot.TeleBot(TELEGRAM_TOKEN)


def main() -> None:
    bot = create_bot()

    storage = UserStorage()
    game = GameService()
    handlers = BotHandlers(bot, storage, game)

    handlers.register()
    bot.polling()


if __name__ == "__main__":
    main()
