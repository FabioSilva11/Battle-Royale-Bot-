import telebot
import random
import json
from datetime import datetime, timedelta
from mercadopago import SDK
import schedule
import time

# Inicializa o bot com o token fictício fornecido pelo BotFather no Telegram
bot = telebot.TeleBot('6397278735')

# Arquivo para armazenar os dados dos usuários
USERS_FILE = 'usuarios.json'

# Função para carregar os dados dos usuários do arquivo
def load_users():
    try:
        with open(USERS_FILE, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

# Função para salvar os dados dos usuários no arquivo
def save_users(users_data):
    with open(USERS_FILE, 'w') as file:
        json.dump(users_data, file)



# Mensagem de boas-vindas do administrador
welcome_message = (
    f'Bem-vindo ao meu jogo eu serei sua guia, me chame de alice , a administrador do Battle Royale!\n'
    f'Parabéns,como administradora do jogo eu vou te conceder alguns benefícios:\n\n'
    f'- 💰 100 moedas de boas-vindas\n'
    f'- 🔒 5 chances para roubar outros usuários\n'
    f'- 🛡️ 1 escudo de proteção\n\n'
    f'Prepare-se para a emoção! Outros usuários podem tentar quebrar seu escudo e roubar parte do seu saldo. As chances de sucesso são tão aleatórias quanto os prêmios! 🚫💸 \n'
    f'Aqui estão os comandos presentes para interagir no jogo é no grupo:\n\n'
    f'- regras: Envia as regras do grupo.\n'
    f'- top10: Mostra os 10 usuários com os saldos mais altos.\n\n'
    f'- roubar: Permite aos usuários roubar moedas de outros usuários mencionados.\n\n'
    f'- status: Permite aos usuários ver seus status de jogo.\n\n'
    f'informação importante sobre o comando roubar, para utilizar o comando basta que seja escrito da seguinte maneira\n\n'
    f'- use o comando desse jeito /roubar seguido de @usuario\n\n'
    f'Não esqueça de ler cuidadosamente as regras antes de começar.\n\n'
    f'Explore as funcionalidades, verifique seu Status, e aproveite ao máximo esta experiência! 🚀🎮\n\n'
)

regras_message = (
    '🚀 Bem-vindo ao nosso grupo me chame de alice , a administrador do Battle Royale!🚀\n\n'
        
    'Para garantir um ambiente agradável e respeitoso para todos, por favor, siga estas regras:\n\n'
        
    '- 1. Respeito mútuo: Seja cortês e respeitoso com todos os membros. Evite linguagem ofensiva, discriminação ou comportamento inadequado.\n\n'
    '- 2. Conteúdo relevante: Mantenha as conversas relacionadas ao tema do grupo. Evite compartilhar conteúdo fora do contexto.\n\n'
    '- 3. Sem spam: Não faça spam de mensagens, links ou qualquer tipo de promoção não autorizada. Qualquer forma de autopromoção deve ser aprovada pelos administradores.\n\n'
    '- 4. Sem conteúdo impróprio: Não compartilhe imagens, vídeos ou textos impróprios. Mantenha o grupo seguro para todas as idades.\n\n'
    '- 5. Sem divulgação de informações pessoais: Evite divulgar informações pessoais suas ou de outros membros no grupo.\n\n'
    '- 6. Respeite os administradores: Siga as instruções dos administradores. Se tiver dúvidas ou preocupações, entre em contato diretamente com eles.\n\n'
    'Ao aderir a este grupo, você concorda em seguir estas regras. Aqueles que violarem as regras podem ser removidos do grupo sem aviso prévio.\n\n'
    'Agradecemos a sua cooperação! Divirta-se e aproveite as conversas no nosso grupo. 🎉'
)        

# Função para obter o ID do usuário pelo nome de usuário
def get_user_id_by_username(username):
    users_data = load_users()
    for user_id, user_info in users_data.items():
        if user_info.get('user_name') == username:
            return user_info.get('user_id')
    return None  # Se o nome de usuário não for encontrado, retorne None

# Função para adicionar um usuário ao grupo
def adicionar_usuario(group_id, user_id, full_name, last_name, user_name):
    users_data = load_users()  # Carrega os dados dos usuários
    if any(users_data[key].get("user_id") == user_id for key in users_data):
        print(f"Usuário com user_id {user_id} já existe. Não foi adicionado novamente.")  
    else:
        users_data[user_id] = {
            'group_id': group_id,
            'user_id': user_id,
            'nome': full_name,
            'sobrenome': last_name,
            'user_name': user_name,
            'saldo': 100,
            'roubos': 5,
            'escudo': 1
        }
        save_users(users_data)  # Salva os dados dos usuários atualizados
        print(f"Usuário com user_id {user_id} adicionado com sucesso.")

# Função para lidar com o comando "/regras" apenas em grupos
@bot.message_handler(commands=['regras'])
def enviar_regras(message):
    # Verifica se a mensagem não é de uma conversa privada
    if message.chat.type != "private":
        # Envia as regras para o usuário
        bot.reply_to(message, regras_message)
    else:
        bot.reply_to(message, "Este comando só pode ser usado em grupos!")

@bot.message_handler(content_types=['new_chat_members'])
def welcome_message_handler(message):
    new_members = message.new_chat_members
    for member in new_members:
        user_id = member.id
        first_name = member.first_name
        last_name = member.last_name 
        username = member.username  
        
        if username is not None:
            welcome_text = f"Bem-vindo, {first_name} {last_name} (@{username})!, 🎉.\n\n{welcome_message}"
            adicionar_usuario(message.chat.id, user_id, first_name, last_name , username)
            bot.reply_to(message, welcome_text)
            bot.reply_to(message, regras_message)
        else:
            bot.send_message(message.chat.id, f"Removendo usuário {first_name} por não ter username configurado.")
            bot.kick_chat_member(message.chat.id, user_id)

# Função para lidar com o comando "/status" apenas em grupos
@bot.message_handler(commands=['status'])
def enviar_status(message):
    # Verifica se a mensagem não é de uma conversa privada
    if message.chat.type != "private":
        # Carrega os dados dos usuários
        users_data = load_users()
        
        # Obtendo o ID do usuário que enviou a mensagem
        user_id = str(message.from_user.id)

        # Verificando se o ID do usuário está nos dados
        if user_id in users_data:
            # Obtendo os dados do usuário
            user_info = users_data[user_id]
            # Enviando os dados do usuário de volta como mensagem
            reply = f"🛡️ Bem-vindo de volta ao campo de batalha, {user_info['nome']}!\n\n Aqui estão seus status atualizados no Battle Royale:\n\n Nome de Guerra: {user_info['user_name']}\n💰 Moedas no Cofre: {user_info['saldo']}\n🔫 Roubos Disponíveis: {user_info['roubos']}\n🛡️ Escudo de Defesa: {user_info['escudo']}"

        else:
            reply = "Usuário não encontrado."

        # Enviando a mensagem de resposta
            
        bot.reply_to(message, reply)
    else:
        bot.reply_to(message, "Este comando só pode ser usado em grupos!")

# Função para lidar com o comando /roubar
@bot.message_handler(commands=['roubar'])
def handle_roubar(message):
    if message.chat.type != "private":
        from_user_name = message.from_user.username
        mentioned_user_name = None
        
        if message.caption_entities or message.entities:
            entities = message.caption_entities or message.entities

            for entity in entities:
                if entity.type == 'mention':
                    mentioned_user_name = message.text[entity.offset + 1:entity.offset + entity.length]

        from_user_id = message.from_user.id
        mentioned_user_id = get_user_id_by_username(mentioned_user_name)

        users_data = load_users()
        from_user_data = users_data.get(str(from_user_id), {})
        mentioned_user_data = users_data.get(str(mentioned_user_id), {})

       # Informações do usuário atual
        user_id = from_user_id
        nome = from_user_data.get("nome", None)
        saldo = from_user_data.get("saldo", None)
        roubos = from_user_data.get("roubos", None)
        escudo = from_user_data.get("escudo", None)
    
        # Informações do usuário mencionado
        mentioned_user_id = mentioned_user_id
        mentioned_nome = mentioned_user_data.get("nome", None)
        mentioned_saldo = mentioned_user_data.get("saldo", None)
        mentioned_escudo = mentioned_user_data.get("escudo", None)


        # Verificações antes de realizar o roubo
        if roubos  > 0:
            if mentioned_saldo > 0:
                if saldo > 0:
                    if mentioned_escudo > 0:
                        if random.randint(0, 100) < 50:
                            # Roubo bem-sucedido
                            mentioned_escudo -= 1
                            roubos -= 1
                            roubo = random.randint(0, mentioned_saldo)
                            mentioned_saldo -= roubo
                            saldo  += roubo
                            bot.reply_to(message, f"Parabéns,{mentioned_nome} estava com escudo e você conseguiu quebrar  conseguindo roubar {roubo} moedas! Que grande feito!")
                        else:
                            # O roubo falha
                            mentioned_escudo -= 1
                            roubos -= 1
                            roubo = random.randint(0, saldo)
                            mentioned_saldo += roubo
                            saldo  -= roubo  
                            bot.reply_to(message, f"Infelizmente, apesar de quebrar o escudo, você não conseguiu roubar com sucesso e perdeu {roubo} moedas para {mentioned_nome}")                  
                    else:
                        if random.randint(0, 100) < 50:
                            # Roubo bem-sucedido
                            roubo = random.randint(0, mentioned_saldo)
                            mentioned_saldo -= roubo
                            roubos -= 1
                            saldo  += roubo
                            bot.reply_to(message, f"Parabéns,{mentioned_nome} estava sem escudo e conseguiu roubar {roubo} moedas! Que grande feito!")
                        else:
                            # O roubo falha
                            roubo = random.randint(0, saldo)
                            mentioned_saldo += roubo
                            saldo  -= roubo
                            roubos -= 1
                            bot.reply_to(message, f"Infelizmente, apesar de o usuário não ter o escudo, você não conseguiu roubar com sucesso e perdeu {roubo} moedas para {mentioned_nome}")               
                else:
                    bot.reply_to(message, f"Infelizmente, {from_user_name} não tem saldo suficiente para fazer uma tentativa de roubo.")
            else:
                bot.reply_to(message, f"Infelizmente, {mentioned_user_name} não tem saldo suficiente para fazer uma tentativa de roubo.")
        else:
            bot.reply_to(message, f"Infelizmente, {from_user_name} não tem saldo de roubos para fazer uma tentativa de roubo.")


        # Atualização dos dados dos usuários após o roubo bem-sucedido ou falha
        users_data[str(from_user_id)] = {
            "group_id": from_user_data.get("group_id"),
            "user_id": from_user_id,
            "nome": nome,
            "sobrenome": from_user_data.get("sobrenome"),
            "user_name": from_user_name,
            "saldo": saldo,
            "roubos": roubos,
            "escudo": escudo
        }

        users_data[str(mentioned_user_id)] = {
            "group_id": mentioned_user_data.get("group_id"),
            "user_id": mentioned_user_id,
            "nome": mentioned_nome,
            "sobrenome": mentioned_user_data.get("sobrenome"),
            "user_name": mentioned_user_name,
            "saldo": mentioned_saldo,
            "roubos": mentioned_user_data.get("roubos"),
            "escudo": mentioned_escudo
        }

        # Salvando os dados atualizados no arquivo
        save_users(users_data)

# Inicia o bot
bot.polling()
