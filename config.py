import os

# Token do bot do Telegram: usa variável de ambiente se existir, caso contrário mantém o valor atual
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "6397278735")

# Caminho do arquivo de usuários
USERS_FILE = os.getenv("USERS_FILE", "usuarios.json")

# Jogo
BASE_ROUBOS = int(os.getenv("BASE_ROUBOS", "5"))
ROUBOS_RESET_INTERVAL_MINUTES = int(os.getenv("ROUBOS_RESET_INTERVAL_MINUTES", "120"))
MAX_SHIELDS = int(os.getenv("MAX_SHIELDS", "3"))

# Loja
SHIELD_PRICE = int(os.getenv("SHIELD_PRICE", "50"))
MAX_RECHARGE_AMOUNT = int(os.getenv("MAX_RECHARGE_AMOUNT", "10000"))

# Mercado Pago
MERCADO_PAGO_ACCESS_TOKEN = os.getenv("MERCADO_PAGO_ACCESS_TOKEN", "")