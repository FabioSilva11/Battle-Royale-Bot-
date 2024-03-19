# Bot Battle Royale

Este é um bot para Telegram que simula um jogo estilo Battle Royale, onde os usuários podem interagir entre si, roubar moedas e se proteger com escudos. O bot foi desenvolvido em Python utilizando a biblioteca `telebot`.

## Funcionalidades

- **Boas-vindas:** Ao ingressar no grupo, os novos membros recebem uma mensagem de boas-vindas personalizada, com instruções sobre o jogo e benefícios iniciais.
- **Regras:** Os usuários podem solicitar as regras do grupo a qualquer momento, mantendo um ambiente respeitoso e seguro.
- **Status:** Os jogadores podem verificar seu saldo de moedas, quantidade de roubos disponíveis e escudos de proteção.
- **Roubo:** Os usuários podem tentar roubar moedas de outros jogadores, com chances aleatórias de sucesso.

## Como jogar

### Comando /roubar

Os jogadores podem usar o comando `/roubar` seguido do nome de usuário do jogador que desejam roubar. Por exemplo:

```
/roubar @usuario
```

Quando um jogador tenta roubar outro jogador, várias condições são verificadas, incluindo o saldo disponível para roubo, a presença de um escudo de proteção e a aleatoriedade do sucesso do roubo.

Se o roubo for bem-sucedido, o jogador ganha uma quantidade aleatória de moedas do jogador roubado. Se o roubo falhar, o jogador pode perder uma quantidade aleatória de suas próprias moedas.

## Como usar

1. Clone o repositório para sua máquina local.
2. Certifique-se de ter Python instalado.
3. Instale as dependências usando `pip install -r requirements.txt`.
4. Substitua o token fictício pelo seu token do BotFather do Telegram.
5. Execute o script Python para iniciar o bot.

```bash
python bot_battle_royale.py
```

Certifique-se de configurar corretamente o token do bot e executar o script em um ambiente adequado.

## Contribuições

Contribuições são bem-vindas! Sinta-se à vontade para abrir problemas (issues) ou enviar pull requests com melhorias, correções de bugs ou novas funcionalidades.

## Autor

Este bot foi desenvolvido por [Seu Nome](https://github.com/seu-usuario).

---

Espero que isso ajude a explicar melhor o funcionamento do jogo para os jogadores!
