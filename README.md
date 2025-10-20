# Bot Battle Royale

Este é um bot para Telegram que simula um jogo estilo Battle Royale, onde os usuários podem interagir entre si, roubar moedas e se proteger com escudos. Desenvolvido em Python com a biblioteca `pyTelegramBotAPI` (`telebot`).

![Screenshot do jogo](https://raw.githubusercontent.com/FabioSilva11/Battle-Royale-Bot-/main/Print1.jpg)

![Screenshot do jogo](https://raw.githubusercontent.com/FabioSilva11/Battle-Royale-Bot-/main/Print2.jpg)

## Funcionalidades
- **Boas-vindas:** Novos membros recebem mensagem com benefícios iniciais.
- **Regras:** Exibe as regras do grupo (/regras).
- **Status:** Mostra saldo, roubos disponíveis e escudo (/status).
- **Roubo:** Tenta roubar moedas de outro usuário mencionado (/roubar @usuario), com sucesso/fracasso aleatórios e tratamento de escudo.
- **Top 10:** Exibe ranking dos 10 maiores saldos (/top10).
- **Loja:** Comprar escudos e visualizar preços (/loja, /comprar_escudo <quantidade>).
- **Recarga:** Recarregar saldo com limite por operação (/recarregar <valor>).

## Arquitetura (modular)
- `updat.py`: ponto de entrada. Cria o bot e registra handlers.
- `config.py`: configurações (token do bot, caminho do arquivo de usuários).
- `models.py`: dataclass `User` e conversões para/desde JSON.
- `storage.py`: `UserStorage` para persistência em `usuarios.json` e buscas.
- `game.py`: `GameService` com mensagens e lógica de roubo.
- `bot_handlers.py`: registro de comandos e eventos do bot.
- `usuarios.json`: persistência simples (criado automaticamente quando necessário).

## Instalação
1. Certifique-se de ter Python 3.10+ instalado.
2. Instale a dependência principal:
   ```bash
   pip install pyTelegramBotAPI
   ```

## Configuração
- Defina o token do BotFather (PowerShell no Windows):
  ```powershell
  $env:TELEGRAM_BOT_TOKEN = "SEU_TOKEN_AQUI"
  ```
- Opcional: personalize o caminho do arquivo de usuários:
  ```powershell
  $env:USERS_FILE = "usuarios.json"
  ```
- Loja e jogo (opcionais):
  ```powershell
  $env:BASE_ROUBOS = "5"                     # chances base por reset
  $env:ROUBOS_RESET_INTERVAL_MINUTES = "120" # intervalo do reset (minutos)
  $env:MAX_SHIELDS = "3"                     # escudos máximos por usuário
  $env:SHIELD_PRICE = "50"                   # preço por escudo (moedas)
  $env:MAX_RECHARGE_AMOUNT = "10000"         # valor máximo por recarga
  $env:MERCADO_PAGO_ACCESS_TOKEN = "SEU_TOKEN_AQUI" # token para API PIX
  ```

## Execução
```bash
python updat.py
```
- Adicione o bot ao seu grupo e conceda permissões básicas.
- Observação: o bot remove novos membros sem `username` configurado (necessita permissão de administrador). Você pode ajustar essa regra em `bot_handlers.py`.

## Como jogar
- **Roubar:**
  ```
  /roubar @usuario
  ```
  Regras resumidas:
  - Você precisa ter `roubos > 0` e `saldo > 0`.
  - Se o alvo tiver escudo, o roubo é bloqueado, 1 escudo é consumido e o atacante perde moedas para o alvo.
  - Chances de roubo resetam a cada 2 horas para o valor base (não acumulam).
  - Saldos nunca ficam negativos (lógica protegida).
  - Não é possível roubar a si mesmo.

- **Status:**
  ```
  /status
  ```
  Mostra seu saldo, roubos e escudo.

- **Doar:**
  ```
  /doar <valor> @usuario
  ```
  Transfere moedas para outro usuário. O destinatário pode receber até 2 doações por dia (limite diário reinicia à meia-noite UTC).

- **Loja:**
  ```
  /loja
  /comprar_escudo <quantidade>
  /comprar_saldo <valor>
  /verificar_pagamento <payment_id>
  ```
  Compra escudos (limite máximo 3). Compra de saldo é feita via PIX (Mercado Pago): gere o pagamento com `/comprar_saldo` e, após aprovação, credite com `/verificar_pagamento`.

- **Top 10:**
  ```
  /top10
  ```
  Exibe ranking dos maiores saldos do grupo.

## Contribuições
Contribuições são bem-vindas! Abra issues ou PRs com melhorias, correções ou novas funcionalidades.

## Autor
Este bot foi desenvolvido por [fabio silva (kirito)](https://github.com/FabioSilva11).

---
Aproveite o jogo! Se quiser evoluir o projeto (loja de escudos, cooldown de roubo, banco de dados), veja `game.py` e `storage.py` como pontos de extensão.
