import telebot
import random
import json
import os
from datetime import datetime
import time

# ===== ТОКЕН =====
TOKEN = '8672284943:AAEVBa7F9rKGQK76pkLr0vvHyDXKFCJDFos'
# =================

bot = telebot.TeleBot(TOKEN)

DATA_FILE = 'users.json'
active_menus = {}
bj_games = {}
bj_multiplayer = {}  # Для многопользовательского блекджека
roulette_waiting = {}

# Промокоды
PROMOCODES = {
    'шепельпрезидент': {'money': 2000, 'exp': 200, 'used': []},
    'тест': {'money': 2, 'exp': 0, 'used': []},
    'куниза200шекелей': {'money': 199, 'exp': 0, 'used': []},
}

LEVELS = {
    1: {"name": "🫣 Грузчик", "salary_min": 5, "salary_max": 50, "exp_needed": 0},
    2: {"name": "🛵 Курьер", "salary_min": 15, "salary_max": 80, "exp_needed": 100},
    3: {"name": "🔧 Автомеханик", "salary_min": 30, "salary_max": 120, "exp_needed": 300},
    4: {"name": "📦 Кладовщик", "salary_min": 50, "salary_max": 160, "exp_needed": 600},
    5: {"name": "📊 Менеджер", "salary_min": 80, "salary_max": 200, "exp_needed": 1000},
    6: {"name": "🏦 Бухгалтер", "salary_min": 120, "salary_max": 250, "exp_needed": 1500},
    7: {"name": "👔 Директор", "salary_min": 180, "salary_max": 350, "exp_needed": 2200},
    8: {"name": "💎 Магнат", "salary_min": 250, "salary_max": 500, "exp_needed": 3000},
}

def load_users():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_users(users):
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(users, f, ensure_ascii=False, indent=2)
        return True
    except:
        return False

users = load_users()

def get_user(user_id, username=None):
    user_id = str(user_id)
    if user_id not in users:
        users[user_id] = {
            'money': 500,
            'level': 1,
            'exp': 0,
            'total_exp': 0,
            'last_work': None,
            'username': username,
            'total_earned': 0,
            'last_daily': None,
            'daily_streak': 0,
            'promos_used': []
        }
        save_users(users)
    else:
        if username and users[user_id].get('username') != username:
            users[user_id]['username'] = username
            save_users(users)
    return users[user_id]

def get_level_info(level):
    return LEVELS.get(level, LEVELS[1])

def add_exp(user_id, amount):
    user = get_user(user_id)
    user['total_exp'] += amount
    user['exp'] += amount
    
    current_level = user['level']
    level_up = False
    
    for lvl in range(current_level + 1, 9):
        if user['total_exp'] >= LEVELS[lvl]['exp_needed']:
            user['level'] = lvl
            level_up = True
        else:
            break
    
    save_users(users)
    return level_up

def get_top_players(limit=10):
    sorted_users = []
    for user_id, data in users.items():
        name = data.get('username', 'Игрок')
        sorted_users.append({
            'name': name,
            'money': data['money'],
            'level': data.get('level', 1)
        })
    sorted_users.sort(key=lambda x: x['money'], reverse=True)
    return sorted_users[:limit]

def keyboard():
    kb = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btns = ['🌾 Работа', '💰 Баланс', '📊 Профиль', '🏆 Топ', '🎁 Бонус', '🎡 Рулетка']
    kb.add(*btns)
    kb.add('🎰 Слоты', '🃏 Блек Джек')
    return kb

def commands_list(message):
    msg = f"📋 *СПИСОК КОМАНД* 📋\n\n"
    msg += f"┌─ 🎮 *ИГРЫ*\n"
    msg += f"│  • рулетка 🎡 - игра в рулетку\n"
    msg += f"│  • слоты 🎰 - игра в слоты\n"
    msg += f"│  • блекджек / блек джек 🃏 - игра в 21\n"
    msg += f"│  • бджек Х - создать игру на Х игроков (2-4)\n"
    msg += f"├─ 💰 *ЗАРАБОТОК*\n"
    msg += f"│  • работа / фарм 🌾 - заработать (КД 10 мин)\n"
    msg += f"│  • бонус / ежедневный 🎁 - бонус (КД 12 ч)\n"
    msg += f"├─ 📊 *ИНФОРМАЦИЯ*\n"
    msg += f"│  • баланс / деньги 💰 - проверить баланс\n"
    msg += f"│  • профиль / стата 📊 - твоя статистика\n"
    msg += f"│  • топ / лидеры 🏆 - топ богатых игроков\n"
    msg += f"│  • команды 📋 - этот список\n"
    msg += f"├─ 🎁 *ПРОМОКОДЫ*\n"
    msg += f"│  • #промо код - активировать промокод\n"
    msg += f"└─ 🃏 *БЛЕКДЖЕК НА КОМПАНИЮ*\n"
    msg += f"   • бджек 2 - игра на 2 игроков\n"
    msg += f"   • бджек 3 - игра на 3 игроков\n"
    msg += f"   • бджек 4 - игра на 4 игроков\n"
    msg += f"   • войти - присоединиться к игре\n"
    msg += f"   • старт - начать игру (админ)\n\n"
    msg += f"💡 *СОВЕТ:* Чем выше уровень, тем больше зарплата!\n"
    msg += f"🎲 Удачи, братан!"
    bot.send_message(message.chat.id, msg, parse_mode='Markdown')

# ===== ПРОМОКОДЫ =====

def promo_command(message, promo_text):
    user = get_user(message.from_user.id, message.from_user.username)
    
    # Проверяем использовал ли уже
    if promo_text in user.get('promos_used', []):
        bot.send_message(message.chat.id, f"❌ Ты уже использовал промокод *{promo_text}*!", parse_mode='Markdown')
        return
    
    # Ищем промокод
    if promo_text in PROMOCODES:
        promo = PROMOCODES[promo_text]
        
        # Добавляем деньги и опыт
        user['money'] += promo['money']
        user['total_earned'] += promo['money']
        add_exp(message.from_user.id, promo['exp'])
        
        # Отмечаем как использованный
        if 'promos_used' not in user:
            user['promos_used'] = []
        user['promos_used'].append(promo_text)
        save_users(users)
        
        level_up = add_exp(message.from_user.id, promo['exp'])
        
        msg = f"🎁 *ПРОМОКОД АКТИВИРОВАН!* 🎁\n\n"
        msg += f"✅ Промокод: *{promo_text}*\n"
        msg += f"💰 +{promo['money']} шекелей\n"
        msg += f"⭐ +{promo['exp']} опыта\n"
        msg += f"💵 Новый баланс: *{user['money']}*"
        
        if level_up:
            new_level = get_level_info(user['level'])
            msg += f"\n\n🎉 *НОВЫЙ УРОВЕНЬ!* 🎉\n"
            msg += f"📈 Теперь ты *{user['level']}* - {new_level['name']}"
        
        bot.send_message(message.chat.id, msg, parse_mode='Markdown')
    else:
        bot.send_message(message.chat.id, f"❌ Промокод *{promo_text}* не найден!", parse_mode='Markdown')

# ===== МНОГОПОЛЬЗОВАТЕЛЬСКИЙ БЛЕКДЖЕК =====

def card_value(card):
    if card in ['J', 'Q', 'K']:
        return 10
    elif card == 'A':
        return 11
    else:
        return int(card)

def hand_score(hand):
    score = 0
    aces = 0
    for c in hand:
        if c in ['J', 'Q', 'K']:
            score += 10
        elif c == 'A':
            aces += 1
            score += 11
        else:
            score += int(c)
    while score > 21 and aces > 0:
        score -= 10
        aces -= 1
    return score

def new_deck():
    d = []
    for _ in range(4):
        for c in ['2','3','4','5','6','7','8','9','10','J','Q','K','A']:
            d.append(c)
    random.shuffle(d)
    return d

def bj_multi_start(message, players_count):
    user_id = message.from_user.id
    user = get_user(user_id, message.from_user.username)
    
    # Проверяем есть ли уже активная игра
    if user_id in bj_multiplayer or any(user_id in game['players'] for game in bj_multiplayer.values()):
        bot.send_message(message.chat.id, "❌ Ты уже в игре!", parse_mode='Markdown')
        return
    
    # Создаем новую игру
    game_id = str(int(time.time()))
    bj_multiplayer[game_id] = {
        'host': user_id,
        'players': {user_id: {'hand': [], 'bet': 0, 'score': 0, 'finished': False}},
        'players_count': players_count,
        'status': 'waiting',
        'deck': None,
        'dealer_hand': [],
        'current_player': None
    }
    
    msg = f"🃏 *БЛЕКДЖЕК НА {players_count} ИГРОКОВ* 🃏\n\n"
    msg += f"👑 Хост: @{message.from_user.username}\n"
    msg += f"👥 Игроки: 1/{players_count}\n\n"
    msg += f"📝 Чтобы присоединиться, напиши *войти*\n"
    msg += f"🚀 Когда все соберутся, хост пишет *старт*"
    
    bot.send_message(message.chat.id, msg, parse_mode='Markdown')

def bj_multi_join(message):
    user_id = message.from_user.id
    
    # Ищем открытую игру
    for game_id, game in bj_multiplayer.items():
        if game['status'] == 'waiting' and user_id not in game['players'] and len(game['players']) < game['players_count']:
            game['players'][user_id] = {'hand': [], 'bet': 0, 'score': 0, 'finished': False}
            
            msg = f"✅ @{message.from_user.username} присоединился!\n"
            msg += f"👥 Игроки: {len(game['players'])}/{game['players_count']}\n\n"
            
            if len(game['players']) == game['players_count']:
                msg += f"🚀 Все собрались! Хост, напиши *старт*"
            
            bot.send_message(message.chat.id, msg, parse_mode='Markdown')
            return
    
    bot.send_message(message.chat.id, "❌ Нет открытых игр или ты уже в игре!", parse_mode='Markdown')

def bj_multi_start_game(message):
    user_id = message.from_user.id
    
    for game_id, game in bj_multiplayer.items():
        if game['host'] == user_id and game['status'] == 'waiting':
            if len(game['players']) < 2:
                bot.send_message(message.chat.id, "❌ Нужно минимум 2 игрока!", parse_mode='Markdown')
                return
            
            # Запрашиваем ставки
            game['status'] = 'betting'
            game['game_id'] = game_id
            
            for player_id in game['players']:
                player = get_user(player_id)
                bot.send_message(player_id, f"🃏 *БЛЕКДЖЕК* 🃏\n\n💰 Введи свою ставку (минимум 10 шекелей):")
            
            bj_multiplayer[game_id] = game
            return
    
    bot.send_message(message.chat.id, "❌ Ты не хост или нет активной игры!", parse_mode='Markdown')

def bj_multi_place_bet(message):
    user_id = message.from_user.id
    
    # Проверяем есть ли игра где игрок еще не поставил
    for game_id, game in bj_multiplayer.items():
        if game['status'] == 'betting' and user_id in game['players'] and game['players'][user_id]['bet'] == 0:
            try:
                bet = int(message.text.strip())
                if bet < 10:
                    bot.send_message(message.chat.id, "❌ Минимальная ставка 10 шекелей!", parse_mode='Markdown')
                    return
            except:
                bot.send_message(message.chat.id, "❌ Введи число!", parse_mode='Markdown')
                return
            
            user = get_user(user_id)
            if user['money'] < bet:
                bot.send_message(message.chat.id, f"❌ Не хватает {bet} шекелей!", parse_mode='Markdown')
                return
            
            user['money'] -= bet
            save_users(users)
            
            game['players'][user_id]['bet'] = bet
            bot.send_message(message.chat.id, f"✅ Ставка *{bet}* принята!", parse_mode='Markdown')
            
            # Проверяем все ли поставили
            all_bet = all(p['bet'] > 0 for p in game['players'].values())
            if all_bet:
                bj_multi_deal(game_id)
            return

def bj_multi_deal(game_id):
    game = bj_multiplayer[game_id]
    deck = new_deck()
    game['deck'] = deck
    game['status'] = 'playing'
    
    # Раздаем карты
    for player_id in game['players']:
        game['players'][player_id]['hand'] = [deck.pop(), deck.pop()]
        game['players'][player_id]['score'] = hand_score(game['players'][player_id]['hand'])
    
    game['dealer_hand'] = [deck.pop(), deck.pop()]
    
    # Начинаем с первого игрока
    players_list = list(game['players'].keys())
    game['current_player'] = players_list[0]
    
    bj_multi_show_turn(game_id)

def bj_multi_show_turn(game_id):
    game = bj_multiplayer[game_id]
    current_player = game['current_player']
    player_data = game['players'][current_player]
    player = get_user(current_player)
    
    dealer_score = hand_score([game['dealer_hand'][0]])
    
    msg = f"🃏 *БЛЕКДЖЕК* 🃏\n\n"
    msg += f"💰 Твоя ставка: *{player_data['bet']}* шекелей\n\n"
    msg += f"🤵 *ДИЛЕР:* {game['dealer_hand'][0]} | ❓\n"
    msg += f"⭐ Очки: *{dealer_score}* + ?\n\n"
    msg += f"🎲 *ТВОИ КАРТЫ:* {' '.join(player_data['hand'])}\n"
    msg += f"⭐ Очки: *{player_data['score']}*\n"
    
    kb = telebot.types.InlineKeyboardMarkup()
    kb.add(
        telebot.types.InlineKeyboardButton("🎴 ЕЩЕ", callback_data=f'bjm_hit_{game_id}'),
        telebot.types.InlineKeyboardButton("✋ ХВАТИТ", callback_data=f'bjm_stand_{game_id}')
    )
    
    bot.send_message(current_player, msg, parse_mode='Markdown', reply_markup=kb)

@bot.callback_query_handler(func=lambda call: call.data.startswith('bjm_'))
def bj_multi_action(call):
    action, game_id = call.data.split('_')[1], call.data.split('_')[2]
    user_id = call.from_user.id
    game = bj_multiplayer.get(game_id)
    
    if not game or game['status'] != 'playing' or game['current_player'] != user_id:
        bot.answer_callback_query(call.id, "❌ Не твой ход!", show_alert=True)
        return
    
    player_data = game['players'][user_id]
    
    if action == 'hit':
        card = game['deck'].pop()
        player_data['hand'].append(card)
        player_data['score'] = hand_score(player_data['hand'])
        
        if player_data['score'] > 21:
            # Перебор
            msg = f"🃏 *БЛЕКДЖЕК* 🃏\n\n"
            msg += f"💰 Ставка: *{player_data['bet']}* шекелей\n\n"
            msg += f"🎲 *ТВОИ КАРТЫ:* {' '.join(player_data['hand'])}\n"
            msg += f"⭐ Очки: *{player_data['score']}* ❌ *ПЕРЕБОР!*\n\n"
            msg += f"💔 *ТЫ ПРОИГРАЛ* {player_data['bet']} шекелей!"
            
            bot.edit_message_text(msg, call.message.chat.id, call.message.message_id, parse_mode='Markdown')
            player_data['finished'] = True
            
            # Следующий игрок
            bj_multi_next_player(game_id, call.message.chat.id)
        else:
            # Обновляем сообщение
            msg = f"🃏 *БЛЕКДЖЕК* 🃏\n\n"
            msg += f"💰 Ставка: *{player_data['bet']}* шекелей\n\n"
            msg += f"🤵 *ДИЛЕР:* {game['dealer_hand'][0]} | ❓\n"
            msg += f"⭐ Очки: *{hand_score([game['dealer_hand'][0]])}* + ?\n\n"
            msg += f"🎲 *ТВОИ КАРТЫ:* {' '.join(player_data['hand'])}\n"
            msg += f"⭐ Очки: *{player_data['score']}*\n"
            
            kb = telebot.types.InlineKeyboardMarkup()
            kb.add(
                telebot.types.InlineKeyboardButton("🎴 ЕЩЕ", callback_data=f'bjm_hit_{game_id}'),
                telebot.types.InlineKeyboardButton("✋ ХВАТИТ", callback_data=f'bjm_stand_{game_id}')
            )
            
            bot.edit_message_text(msg, call.message.chat.id, call.message.message_id, parse_mode='Markdown', reply_markup=kb)
    
    elif action == 'stand':
        player_data['finished'] = True
        bot.edit_message_text(f"✋ Ты остановился с *{player_data['score']}* очками", 
                              call.message.chat.id, call.message.message_id, parse_mode='Markdown')
        bj_multi_next_player(game_id, call.message.chat.id)
    
    bot.answer_callback_query(call.id)

def bj_multi_next_player(game_id, chat_id):
    game = bj_multiplayer[game_id]
    players_list = list(game['players'].keys())
    current_idx = players_list.index(game['current_player'])
    
    # Ищем следующего непрошедшего игрока
    for i in range(current_idx + 1, len(players_list)):
        if not game['players'][players_list[i]]['finished']:
            game['current_player'] = players_list[i]
            bj_multi_show_turn(game_id)
            return
    
    # Все игроки закончили, ход дилера
    bj_multi_dealer_turn(game_id)

def bj_multi_dealer_turn(game_id):
    game = bj_multiplayer[game_id]
    dealer_score = hand_score(game['dealer_hand'])
    
    while dealer_score < 17:
        card = game['deck'].pop()
        game['dealer_hand'].append(card)
        dealer_score = hand_score(game['dealer_hand'])
    
    # Подводим итоги
    results = []
    for player_id, player_data in game['players'].items():
        user = get_user(player_id)
        player_score = player_data['score']
        
        if player_score > 21:
            # Уже проиграл
            results.append(f"💔 @{user['username']} - ПЕРЕБОР (проиграл {player_data['bet']})")
        elif dealer_score > 21:
            win = player_data['bet'] * 2
            user['money'] += win
            user['total_earned'] += win
            add_exp(player_id, win // 4)
            results.append(f"🎉 @{user['username']} - ПОБЕДА! +{win}")
        elif player_score > dealer_score:
            win = player_data['bet'] * 2
            user['money'] += win
            user['total_earned'] += win
            add_exp(player_id, win // 4)
            results.append(f"🎉 @{user['username']} - ПОБЕДА! +{win}")
        elif player_score < dealer_score:
            results.append(f"💔 @{user['username']} - ПРОИГРЫШ (-{player_data['bet']})")
        else:
            user['money'] += player_data['bet']
            results.append(f"🤝 @{user['username']} - НИЧЬЯ (вернули {player_data['bet']})")
        
        save_users(users)
    
    msg = f"🃏 *РЕЗУЛЬТАТ ИГРЫ* 🃏\n\n"
    msg += f"🤵 *ДИЛЕР:* {' '.join(game['dealer_hand'])}\n"
    msg += f"⭐ Очки дилера: *{dealer_score}*\n\n"
    msg += f"📊 *РЕЗУЛЬТАТЫ:*\n"
    for r in results:
        msg += f"{r}\n"
    
    for player_id in game['players']:
        try:
            bot.send_message(player_id, msg, parse_mode='Markdown')
        except:
            pass
    
    del bj_multiplayer[game_id]

# ===== ОСТАЛЬНЫЕ КОМАНДЫ =====

@bot.message_handler(func=lambda m: True, content_types=['text'])
def handle_all_messages(message):
    user_id = message.from_user.id
    username = message.from_user.username
    text = message.text.lower().strip()
    
    user = get_user(user_id, username)
    
    # Промокоды
    if text.startswith('#промо'):
        promo_text = text.replace('#промо', '').strip().lower()
        promo_command(message, promo_text)
        return
    
    # Блекджек на компанию
    if text == 'бджек 2':
        bj_multi_start(message, 2)
        return
    elif text == 'бджек 3':
        bj_multi_start(message, 3)
        return
    elif text == 'бджек 4':
        bj_multi_start(message, 4)
        return
    elif text == 'войти':
        bj_multi_join(message)
        return
    elif text == 'старт':
        bj_multi_start_game(message)
        return
    
    # Ставки для многопользовательского блекджека
    for game_id, game in bj_multiplayer.items():
        if game['status'] == 'betting' and user_id in game['players'] and game['players'][user_id]['bet'] == 0:
            try:
                bet = int(message.text)
                if bet >= 10:
                    bj_multi_place_bet(message)
                return
            except:
                pass
    
    # Обычные команды
    if text in ['/start', 'start']:
        start_command(message, user)
    elif text in ['команды', 'commands', 'help', 'помощь', 'помоги']:
        commands_list(message)
    elif text in ['работа', 'фарм', 'фармить', 'работка', '🌾 работа']:
        work_command(message, user)
    elif text in ['баланс', 'деньги', 'бабло', 'шекели', '💰 баланс']:
        balance_command(message, user)
    elif text in ['профиль', 'стата', 'инфо', '📊 профиль']:
        profile_command(message, user)
    elif text in ['топ', 'топ10', 'лидеры', 'богатые', '🏆 топ']:
        top_command(message)
    elif text in ['бонус', 'ежедневный', 'ежедневный бонус', 'daily', '🎁 бонус']:
        daily_bonus_command(message, user)
    elif text in ['рулетка', 'рулетку', '🎡 рулетка']:
        roulette_menu_command(message)
    elif text in ['слоты', 'слот', 'казик', '🎰 слоты']:
        slots_menu_command(message)
    elif text in ['блекджек', 'блек джек', 'blackjack', '21', '🃏 блек джек']:
        bj_menu_command(message)

def start_command(message, user):
    level_info = get_level_info(user['level'])
    
    bot.send_message(
        message.chat.id,
        f"🎮 *ХИТРЫЙ ЕВРЕЙ* 🎮\n\n"
        f"👋 Привет, @{message.from_user.username}!\n"
        f"💰 Стартовый капитал: *500 шекелей*\n"
        f"📊 Твой уровень: *{user['level']}* - {level_info['name']}\n\n"
        f"📝 Напиши *'команды'* чтобы увидеть все команды!\n\n"
        f"🎲 Удачи, братан!",
        parse_mode='Markdown'
    )

def work_command(message, user):
    level_info = get_level_info(user['level'])
    
    if user['last_work']:
        last = datetime.fromisoformat(user['last_work'])
        diff = (datetime.now() - last).total_seconds()
        if diff < 600:
            rem = 600 - diff
            minutes = int(rem // 60)
            seconds = int(rem % 60)
            bot.send_message(message.chat.id, f"⏰ Отдыхай *{minutes} мин {seconds} сек*", parse_mode='Markdown')
            return
    
    earned = random.randint(level_info['salary_min'], level_info['salary_max'])
    user['money'] += earned
    user['total_earned'] += earned
    user['last_work'] = datetime.now().isoformat()
    
    exp_earned = earned // 2
    level_up = add_exp(message.from_user.id, exp_earned)
    save_users(users)
    
    msg = f"🌾 *ТЫ ПОРАБОТАЛ!* 🌾\n\n"
    msg += f"💼 Профессия: {level_info['name']}\n"
    msg += f"💰 Зарплата: *+{earned} шекелей*\n"
    msg += f"⭐ Опыт: *+{exp_earned}*\n"
    msg += f"💵 Теперь у тебя: *{user['money']} шекелей*"
    
    if level_up:
        new_level = get_level_info(user['level'])
        msg += f"\n\n🎉 *НОВЫЙ УРОВЕНЬ!* 🎉\n"
        msg += f"📈 Теперь ты *{user['level']}* - {new_level['name']}"
    
    bot.send_message(message.chat.id, msg, parse_mode='Markdown')

def balance_command(message, user):
    level_info = get_level_info(user['level'])
    bot.send_message(
        message.chat.id,
        f"💰 *ТВОЙ БАЛАНС* 💰\n\n"
        f"💵 Денег: *{user['money']} шекелей*\n"
        f"📊 Уровень: *{user['level']}* ({level_info['name']})\n"
        f"⭐ Опыт: *{user['exp']}*\n"
        f"📈 Всего заработал: *{user['total_earned']}*",
        parse_mode='Markdown'
    )

def profile_command(message, user):
    level_info = get_level_info(user['level'])
    
    next_level = user['level'] + 1
    if next_level in LEVELS:
        need = LEVELS[next_level]['exp_needed']
        have = user['total_exp']
        left = need - have
        if need > 0:
            prog = int((have / need) * 100)
        else:
            prog = 100
    else:
        left = 0
        prog = 100
    
    streak = user.get('daily_streak', 0)
    username = user.get('username') or message.from_user.username or 'Нет имени'
    
    msg = f"📊 *ТВОЙ ПРОФИЛЬ* 📊\n\n"
    msg += f"👤 Игрок: @{username}\n"
    msg += f"🏆 Уровень: *{user['level']}* - {level_info['name']}\n"
    msg += f"💰 Денег: *{user['money']} шекелей*\n"
    msg += f"⭐ Опыт: *{user['exp']}*\n"
    msg += f"📈 Всего заработал: *{user['total_earned']}*\n"
    msg += f"🎁 Серия бонусов: *{streak}* дней"
    
    if left > 0:
        msg += f"\n\n📊 До *{next_level}* уровня: *{left}* опыта (*{prog}%*)"
    
    bot.send_message(message.chat.id, msg, parse_mode='Markdown')

def top_command(message):
    top = get_top_players(10)
    
    if not top:
        bot.send_message(message.chat.id, "🏆 Топ пока пуст!")
        return
    
    msg = "🏆 *ТОП БОГАТЫХ ИГРОКОВ* 🏆\n\n"
    for i, p in enumerate(top, 1):
        if i == 1:
            msg += f"👑 *{i}. @{p['name']}* - {p['money']} 💰\n"
        elif i == 2:
            msg += f"🥈 *{i}. @{p['name']}* - {p['money']} 💰\n"
        elif i == 3:
            msg += f"🥉 *{i}. @{p['name']}* - {p['money']} 💰\n"
        else:
            msg += f"{i}. @{p['name']} - {p['money']} 💰\n"
    
    bot.send_message(message.chat.id, msg, parse_mode='Markdown')

def daily_bonus_command(message, user):
    if user['last_daily']:
        last = datetime.fromisoformat(user['last_daily'])
        diff = (datetime.now() - last).total_seconds()
        if diff < 43200:
            hours = int((43200 - diff) // 3600)
            minutes = int(((43200 - diff) % 3600) // 60)
            bot.send_message(message.chat.id, f"🎁 Бонус через *{hours} ч {minutes} мин*\n🔥 Серия: *{user.get('daily_streak', 0)}* дней", parse_mode='Markdown')
            return
    
    bonus = random.randint(50, 200)
    user['money'] += bonus
    user['total_earned'] += bonus
    user['last_daily'] = datetime.now().isoformat()
    user['daily_streak'] = user.get('daily_streak', 0) + 1
    
    exp_gained = bonus // 3
    level_up = add_exp(message.from_user.id, exp_gained)
    save_users(users)
    
    msg = f"🎁 *ЕЖЕДНЕВНЫЙ БОНУС* 🎁\n\n"
    msg += f"💰 *+{bonus} шекелей!*\n"
    msg += f"⭐ *+{exp_gained} опыта*\n"
    msg += f"🔥 Серия: *{user['daily_streak']}* дней\n"
    msg += f"💵 Баланс: *{user['money']}*"
    
    if level_up:
        new_level = get_level_info(user['level'])
        msg += f"\n\n🎉 *НОВЫЙ УРОВЕНЬ!* 🎉\n"
        msg += f"📈 Теперь ты *{user['level']}* - {new_level['name']}"
    
    bot.send_message(message.chat.id, msg, parse_mode='Markdown')

# ===== РУЛЕТКА =====

def roulette_menu_command(message):
    user_id = message.from_user.id
    
    kb = telebot.types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        telebot.types.InlineKeyboardButton("🔴 КРАСНОЕ", callback_data='roulette_red'),
        telebot.types.InlineKeyboardButton("⚫ ЧЕРНОЕ", callback_data='roulette_black')
    )
    kb.add(
        telebot.types.InlineKeyboardButton("🟢 ЗЕЛЕНЫЙ", callback_data='roulette_green'),
        telebot.types.InlineKeyboardButton("📊 ЧЕТ", callback_data='roulette_even')
    )
    kb.add(
        telebot.types.InlineKeyboardButton("📊 НЕЧЕТ", callback_data='roulette_odd')
    )
    
    bot.send_message(message.chat.id, "🎡 *РУЛЕТКА* 🎡\n\nВыбери тип ставки:", parse_mode='Markdown', reply_markup=kb)

@bot.callback_query_handler(func=lambda call: call.data.startswith('roulette_'))
def roulette_choose_bet(call):
    user_id = call.from_user.id
    bet_type = call.data.split('_')[1]
    
    roulette_waiting[user_id] = bet_type
    
    bot.edit_message_text("🎡 *РУЛЕТКА* 🎡\n\n💰 Введи сумму ставки (минимум 10 шекелей):", 
                          call.message.chat.id, call.message.message_id, parse_mode='Markdown')
    bot.answer_callback_query(call.id)

@bot.message_handler(func=lambda m: m.from_user.id in roulette_waiting)
def roulette_place_bet(message):
    user_id = message.from_user.id
    bet_type = roulette_waiting[user_id]
    
    try:
        bet = int(message.text.strip())
        if bet < 10:
            bot.send_message(message.chat.id, "❌ Минимальная ставка *10 шекелей*!", parse_mode='Markdown')
            return
    except:
        bot.send_message(message.chat.id, "❌ Введи *число*!", parse_mode='Markdown')
        del roulette_waiting[user_id]
        return
    
    user = get_user(user_id, message.from_user.username)
    
    if user['money'] < bet:
        bot.send_message(message.chat.id, f"❌ Не хватает *{bet}* шекелей! У тебя *{user['money']}*", parse_mode='Markdown')
        del roulette_waiting[user_id]
        return
    
    user['money'] -= bet
    save_users(users)
    
    result_num = random.randint(0, 36)
    
    if result_num == 0:
        result_color = 'green'
        color_emoji = '🟢'
    elif result_num in [1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36]:
        result_color = 'red'
        color_emoji = '🔴'
    else:
        result_color = 'black'
        color_emoji = '⚫'
    
    win = 0
    if bet_type == 'red' and result_color == 'red':
        win = bet * 2
    elif bet_type == 'black' and result_color == 'black':
        win = bet * 2
    elif bet_type == 'green' and result_num == 0:
        win = bet * 35
    elif bet_type == 'even' and result_num > 0 and result_num % 2 == 0:
        win = bet * 2
    elif bet_type == 'odd' and result_num > 0 and result_num % 2 == 1:
        win = bet * 2
    
    bet_names = {
        'red': '🔴 КРАСНОЕ', 
        'black': '⚫ ЧЕРНОЕ', 
        'green': '🟢 ЗЕЛЕНЫЙ', 
        'even': '📊 ЧЕТ', 
        'odd': '📊 НЕЧЕТ'
    }
    
    if win > 0:
        user['money'] += win
        user['total_earned'] += win
        add_exp(user_id, win // 4)
        save_users(users)
        
        msg = f"🎡 *РУЛЕТКА* 🎡\n\n"
        msg += f"🎲 Выпало: {color_emoji} *{result_num}*\n"
        msg += f"🎯 Твоя ставка: {bet_names[bet_type]}\n"
        msg += f"✅ Ставка: *{bet}* шекелей\n"
        msg += f"💰 *ВЫИГРЫШ: +{win} шекелей!*\n"
        msg += f"💵 Новый баланс: *{user['money']}*"
    else:
        save_users(users)
        
        msg = f"🎡 *РУЛЕТКА* 🎡\n\n"
        msg += f"🎲 Выпало: {color_emoji} *{result_num}*\n"
        msg += f"🎯 Твоя ставка: {bet_names[bet_type]}\n"
        msg += f"💔 *ПРОИГРЫШ: -{bet} шекелей*\n"
        msg += f"💵 Новый баланс: *{user['money']}*"
    
    bot.send_message(message.chat.id, msg, parse_mode='Markdown')
    del roulette_waiting[user_id]

# ===== СЛОТЫ =====

def slots_menu_command(message):
    user_id = message.from_user.id
    active_menus[user_id] = 'slots'
    
    kb = telebot.types.InlineKeyboardMarkup()
    kb.add(
        telebot.types.InlineKeyboardButton("10 💰", callback_data='slot_10'),
        telebot.types.InlineKeyboardButton("50 💰", callback_data='slot_50'),
        telebot.types.InlineKeyboardButton("100 💰", callback_data='slot_100')
    )
    bot.send_message(message.chat.id, "🎰 *ВЫБЕРИ СТАВКУ:*", parse_mode='Markdown', reply_markup=kb)

@bot.callback_query_handler(func=lambda call: call.data.startswith('slot_'))
def slots_play(call):
    user_id = call.from_user.id
    
    if user_id not in active_menus or active_menus[user_id] != 'slots':
        bot.answer_callback_query(call.id, "❌ Не твоя кнопка!", show_alert=True)
        return
    
    bet = int(call.data.split('_')[1])
    user = get_user(user_id, call.from_user.username)
    
    if user['money'] < bet:
        bot.answer_callback_query(call.id, f"❌ Не хватает {bet}!", show_alert=True)
        if user_id in active_menus:
            del active_menus[user_id]
        return
    
    user['money'] -= bet
    
    icons = ['🍒', '🍊', '🍋', '💰', '💎']
    res = [random.choice(icons) for _ in range(3)]
    
    win = 0
    if res[0] == res[1] == res[2]:
        if res[0] == '🍒':
            win = bet * 2
        elif res[0] == '💰':
            win = bet * 5
        elif res[0] == '💎':
            win = bet * 10
        else:
            win = bet * 2
    
    if win > 0:
        user['money'] += win
        user['total_earned'] += win
        add_exp(user_id, win // 4)
        msg = f"✨ *ПОБЕДА!* ✨\n💰 *+{win}* шекелей\n💵 Баланс: *{user['money']}*"
    else:
        msg = f"💔 *ПРОИГРЫШ*\n💰 Баланс: *{user['money']}*"
    
    save_users(users)
    
    try:
        bot.edit_message_text(f"🎰 *{res[0]} | {res[1]} | {res[2]}*\n\n{msg}", 
                              call.message.chat.id, call.message.message_id, parse_mode='Markdown')
    except:
        pass
    
    bot.answer_callback_query(call.id)
    
    if user_id in active_menus:
        del active_menus[user_id]

# ===== ОДИНОЧНЫЙ БЛЕКДЖЕК =====

def bj_menu_command(message):
    user_id = message.from_user.id
    active_menus[user_id] = 'bj'
    
    kb = telebot.types.InlineKeyboardMarkup()
    kb.add(
        telebot.types.InlineKeyboardButton("10 💰", callback_data='bj_10'),
        telebot.types.InlineKeyboardButton("50 💰", callback_data='bj_50'),
        telebot.types.InlineKeyboardButton("100 💰", callback_data='bj_100')
    )
    bot.send_message(message.chat.id, "🃏 *ВЫБЕРИ СТАВКУ:*", parse_mode='Markdown', reply_markup=kb)

@bot.callback_query_handler(func=lambda call: call.data.startswith('bj_') and len(call.data) < 7)
def bj_new(call):
    user_id = call.from_user.id
    
    if user_id not in active_menus or active_menus[user_id] != 'bj':
        bot.answer_callback_query(call.id, "❌ Нажми 'Блек Джек' сначала!", show_alert=True)
        return
    
    bet = int(call.data.split('_')[1])
    user = get_user(user_id, call.from_user.username)
    
    if user['money'] < bet:
        bot.answer_callback_query(call.id, f"❌ Нужно {bet}!", show_alert=True)
        if user_id in active_menus:
            del active_menus[user_id]
        return
    
    user['money'] -= bet
    save_users(users)
    
    deck = new_deck()
    player = [deck.pop(), deck.pop()]
    dealer = [deck.pop(), deck.pop()]
    
    bj_games[user_id] = {
        'bet': bet,
        'player': player,
        'dealer': dealer,
        'deck': deck,
        'chat_id': call.message.chat.id,
        'msg_id': call.message.message_id
    }
    
    if user_id in active_menus:
        del active_menus[user_id]
    
    bj_show(call)
    bot.answer_callback_query(call.id)

def bj_show(call):
    user_id = call.from_user.id
    g = bj_games.get(user_id)
    if not g:
        return
    
    ps = hand_score(g['player'])
    ds = hand_score([g['dealer'][0]])
    
    msg = f"🃏 *БЛЕК ДЖЕК* 🃏\n\n"
    msg += f"💰 Ставка: *{g['bet']}* шекелей\n\n"
    msg += f"🤵 *ДИЛЕР:* {g['dealer'][0]} | ❓\n"
    msg += f"⭐ Очки: *{ds}* + ?\n\n"
    msg += f"🎲 *ТЫ:* {' '.join(g['player'])}\n"
    msg += f"⭐ Очки: *{ps}*\n"
    
    kb = telebot.types.InlineKeyboardMarkup()
    kb.add(
        telebot.types.InlineKeyboardButton("🎴 ЕЩЕ", callback_data='bj_hit'),
        telebot.types.InlineKeyboardButton("✋ ХВАТИТ", callback_data='bj_stand')
    )
    
    try:
        bot.edit_message_text(msg, g['chat_id'], g['msg_id'], parse_mode='Markdown', reply_markup=kb)
    except:
        pass

@bot.callback_query_handler(func=lambda call: call.data == 'bj_hit')
def bj_hit(call):
    user_id = call.from_user.id
    g = bj_games.get(user_id)
    
    if not g:
        bot.answer_callback_query(call.id, "❌ Игра не найдена!", show_alert=True)
        return
    
    card = g['deck'].pop()
    g['player'].append(card)
    ps = hand_score(g['player'])
    
    if ps > 21:
        msg = f"🃏 *БЛЕК ДЖЕК* 🃏\n\n"
        msg += f"💰 Ставка: *{g['bet']}* шекелей\n\n"
        msg += f"🎲 *ТВОИ КАРТЫ:* {' '.join(g['player'])}\n"
        msg += f"⭐ Очки: *{ps}* ❌ *ПЕРЕБОР!*\n\n"
        msg += f"💔 *ТЫ ПРОИГРАЛ* {g['bet']} шекелей!"
        
        try:
            bot.edit_message_text(msg, g['chat_id'], g['msg_id'], parse_mode='Markdown')
        except:
            pass
        
        bot.answer_callback_query(call.id, "ПЕРЕБОР!", show_alert=True)
        del bj_games[user_id]
        return
    
    bj_games[user_id] = g
    
    msg = f"🃏 *БЛЕК ДЖЕК* 🃏\n\n"
    msg += f"💰 Ставка: *{g['bet']}* шекелей\n\n"
    msg += f"🤵 *ДИЛЕР:* {g['dealer'][0]} | ❓\n"
    msg += f"🎲 *ТЫ:* {' '.join(g['player'])}\n"
    msg += f"⭐ Очки: *{ps}*\n"
    
    kb = telebot.types.InlineKeyboardMarkup()
    kb.add(
        telebot.types.InlineKeyboardButton("🎴 ЕЩЕ", callback_data='bj_hit'),
        telebot.types.InlineKeyboardButton("✋ ХВАТИТ", callback_data='bj_stand')
    )
    
    try:
        bot.edit_message_text(msg, g['chat_id'], g['msg_id'], parse_mode='Markdown', reply_markup=kb)
    except:
        pass
    
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data == 'bj_stand')
def bj_stand(call):
    user_id = call.from_user.id
    g = bj_games.get(user_id)
    
    if not g:
        bot.answer_callback_query(call.id, "❌ Игра не найдена!", show_alert=True)
        return
    
    ps = hand_score(g['player'])
    ds = hand_score(g['dealer'])
    
    while ds < 17:
        card = g['deck'].pop()
        g['dealer'].append(card)
        ds = hand_score(g['dealer'])
    
    user = get_user(user_id, call.from_user.username)
    
    if ds > 21:
        win = g['bet'] * 2
        user['money'] += win
        user['total_earned'] += win
        add_exp(user_id, win // 4)
        res = f"🎉 *ПОБЕДА!* +{win} шекелей"
    elif ps > ds:
        win = g['bet'] * 2
        user['money'] += win
        user['total_earned'] += win
        add_exp(user_id, win // 4)
        res = f"🎉 *ПОБЕДА!* +{win} шекелей"
    elif ps < ds:
        res = f"💔 *ПРОИГРЫШ!* -{g['bet']} шекелей"
    else:
        user['money'] += g['bet']
        res = f"🤝 *НИЧЬЯ!* +{g['bet']} шекелей"
    
    save_users(users)
    
    msg = f"🃏 *БЛЕК ДЖЕК* 🃏\n\n"
    msg += f"💰 Ставка: *{g['bet']}* шекелей\n\n"
    msg += f"🤵 *ДИЛЕР:* {' '.join(g['dealer'])}\n"
    msg += f"⭐ Очки: *{ds}*\n\n"
    msg += f"🎲 *ТЫ:* {' '.join(g['player'])}\n"
    msg += f"⭐ Очки: *{ps}*\n\n"
    msg += f"{res}\n"
    msg += f"💰 Баланс: *{user['money']}*"
    
    try:
        bot.edit_message_text(msg, g['chat_id'], g['msg_id'], parse_mode='Markdown')
    except:
        pass
    
    bot.answer_callback_query(call.id)
    del bj_games[user_id]

# ===== ЗАПУСК =====

print("=" * 50)
print("🤖 ХИТРЫЙ ЕВРЕЙ БОТ ЗАПУЩЕН!")
print("🎮 Блекджек на 2-4 игрока - работает!")
print("🎁 Промокоды: #промо шепельпрезидент, #промо тест, #промо куниза200шекелей")
print("=" * 50)

bot.infinity_polling()
