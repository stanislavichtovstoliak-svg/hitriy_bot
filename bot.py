import telebot
import random
import json
import os
from datetime import datetime, timedelta
import time
import re
import os
# ===== ВСТАВЬ СВОЙ ТОКЕН СЮДА =====
TOKEN = '8672284943:AAGHqbF-6F-JXYUAe-rgTdhiXQwwv_4nZ9k'
# ===================================

bot = telebot.TeleBot(TOKEN)

# Файл для данных
DATA_FILE = 'users.json'

# Храним активные игры
active_menus = {}
bj_games = {}

# Защита от дублей
last_command_time = {}

# Система уровней
LEVELS = {
    1: {"name": "Грузчик", "salary_min": 5, "salary_max": 50, "exp_needed": 0},
    2: {"name": "Курьер", "salary_min": 15, "salary_max": 80, "exp_needed": 100},
    3: {"name": "Автомеханик", "salary_min": 30, "salary_max": 120, "exp_needed": 300},
    4: {"name": "Кладовщик", "salary_min": 50, "salary_max": 160, "exp_needed": 600},
    5: {"name": "Менеджер", "salary_min": 80, "salary_max": 200, "exp_needed": 1000},
    6: {"name": "Бухгалтер", "salary_min": 120, "salary_max": 250, "exp_needed": 1500},
    7: {"name": "Директор", "salary_min": 180, "salary_max": 350, "exp_needed": 2200},
    8: {"name": "Магнат", "salary_min": 250, "salary_max": 500, "exp_needed": 3000},
}

def is_duplicate(user_id, command):
    now = time.time()
    key = f"{user_id}_{command}"
    if key in last_command_time and now - last_command_time[key] < 2:
        return True
    last_command_time[key] = now
    return False

def load_users():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(users, f, ensure_ascii=False, indent=2)

users = load_users()

def get_user(user_id):
    user_id = str(user_id)
    if user_id not in users:
        users[user_id] = {
            'money': 500,
            'level': 1,
            'exp': 0,
            'total_exp': 0,
            'last_work': None,
            'username': None,
            'total_earned': 0,
            'last_daily': None,
            'daily_streak': 0
        }
        save_users(users)
    return users[user_id]

def update_username(user_id, username):
    user = get_user(user_id)
    if username and user['username'] != username:
        user['username'] = username
        save_users(users)

def get_level_info(level):
    if level > max(LEVELS.keys()):
        level = max(LEVELS.keys())
    return LEVELS.get(level, LEVELS[1])

def add_exp(user_id, amount):
    user = get_user(user_id)
    user['total_exp'] += amount
    user['exp'] += amount
    
    current_level = user['level']
    next_level = current_level + 1
    
    while next_level in LEVELS and user['total_exp'] >= LEVELS[next_level]['exp_needed']:
        user['level'] = next_level
        next_level += 1
    
    if user['level'] > current_level:
        save_users(users)
        return True
    save_users(users)
    return False

def get_top_players(limit=10):
    sorted_users = []
    for user_id, data in users.items():
        name = data.get('username')
        if not name:
            name = "Игрок"
        sorted_users.append({
            'name': name,
            'money': data['money'],
            'level': data.get('level', 1)
        })
    sorted_users.sort(key=lambda x: x['money'], reverse=True)
    return sorted_users[:limit]

def keyboard():
    kb = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btns = ['🌾 Работа', '💰 Баланс', '📊 Профиль', '🏆 Топ', '🎁 Бонус']
    kb.add(*btns)
    kb.add('🎰 Слоты', '🃏 Блек Джек')
    return kb

def can_work(user_id):
    user = get_user(user_id)
    if not user['last_work']:
        return True, 0
    last = datetime.fromisoformat(user['last_work'])
    diff = (datetime.now() - last).total_seconds()
    if diff >= 600:
        return True, 0
    return False, int(600 - diff)

def can_get_daily(user_id):
    user = get_user(user_id)
    if not user['last_daily']:
        return True, 0, 1
    
    last = datetime.fromisoformat(user['last_daily'])
    now = datetime.now()
    seconds_passed = (now - last).total_seconds()
    
    # 12 часов = 43200 секунд
    if seconds_passed >= 43200:
        # Проверяем серию (если прошло меньше 24 часов, серия продолжается)
        if seconds_passed < 86400:
            streak = user.get('daily_streak', 0) + 1
        else:
            streak = 1
        return True, 0, streak
    
    time_left = int(43200 - seconds_passed)
    return False, time_left, user.get('daily_streak', 0)

def get_daily_bonus(streak):
    # Базовый бонус от 50 до 200
    base = random.randint(50, 200)
    # Бонус за серию (до +50% максимум)
    streak_bonus = int(base * min(streak, 10) / 20)
    total = base + streak_bonus
    return total, base, streak_bonus

# ===== ОСНОВНЫЕ КОМАНДЫ =====

@bot.message_handler(func=lambda m: True, content_types=['text'])
def handle_all_messages(message):
    user_id = message.from_user.id
    text = message.text.lower().strip()
    
    # Обновляем юзернейм
    update_username(user_id, message.from_user.username)
    
    # Проверка на дубли
    if is_duplicate(user_id, text):
        return
    
    # Обработка команд
    if text in ['/start', 'start']:
        start_command(message)
    elif text in ['работа', 'фарм', 'фармить', 'работка', '🌾 работа']:
        work_command(message)
    elif text in ['баланс', 'деньги', 'бабло', 'шекели', '💰 баланс']:
        balance_command(message)
    elif text in ['профиль', 'стата', 'инфо', '📊 профиль']:
        profile_command(message)
    elif text in ['топ', 'топ 10', 'лидеры', 'богатые', '🏆 топ']:
        top_command(message)
    elif text in ['слоты', 'слот', 'казик', '🎰 слоты']:
        slots_menu_command(message)
    elif text in ['блекджек', 'блек джек', 'blackjack', '21', '🃏 блек джек']:
        bj_menu_command(message)
    elif text in ['бонус', 'ежедневный', 'daily', 'ежедневный бонус', '🎁 бонус']:
        daily_bonus_command(message)

def start_command(message):
    user_id = message.from_user.id
    user = get_user(user_id)
    level_info = get_level_info(user['level'])
    
    bot.send_message(
        message.chat.id,
        f"🎮 ХИТРЫЙ ЕВРЕЙ 🎮\n\n"
        f"💰 Стартовый капитал: 500 шекелей\n"
        f"📊 Твой уровень: {user['level']} - {level_info['name']}\n\n"
        f"📝 ДОСТУПНЫЕ КОМАНДЫ:\n"
        f"• Работа / фарм - заработать (КД 10 мин)\n"
        f"• Бонус / ежедневный - получить бонус (КД 12 ч)\n"
        f"• Баланс - проверить деньги\n"
        f"• Профиль - твоя стата\n"
        f"• Топ - богатые игроки\n"
        f"• Слоты - играть в слоты\n"
        f"• Блекджек - играть в 21\n\n"
        f"Также есть кнопки внизу!",
        reply_markup=keyboard()
    )

def work_command(message):
    user_id = message.from_user.id
    user = get_user(user_id)
    level_info = get_level_info(user['level'])
    
    can, wait = can_work(user_id)
    if not can:
        minutes = wait // 60
        seconds = wait % 60
        bot.send_message(
            message.chat.id,
            f"⏰ Отдыхай {minutes} мин {seconds} сек\n"
            f"💪 Зарплата: {level_info['salary_min']}-{level_info['salary_max']}"
        )
        return
    
    earned = random.randint(level_info['salary_min'], level_info['salary_max'])
    user['money'] += earned
    user['total_earned'] += earned
    user['last_work'] = datetime.now().isoformat()
    
    exp_earned = earned // 2
    level_up = add_exp(user_id, exp_earned)
    save_users(users)
    
    msg = f"🌾 ТЫ ПОРАБОТАЛ!\n\n"
    msg += f"💼 {level_info['name']}\n"
    msg += f"💰 +{earned} шекелей\n"
    msg += f"⭐ +{exp_earned} опыта\n"
    msg += f"💵 Теперь: {user['money']}"
    
    if level_up:
        new_lvl = get_level_info(user['level'])
        msg += f"\n\n🎉 НОВЫЙ УРОВЕНЬ! 🎉\n"
        msg += f"Теперь ты {user['level']} - {new_lvl['name']}"
    
    bot.send_message(message.chat.id, msg)

def balance_command(message):
    user_id = message.from_user.id
    user = get_user(user_id)
    level_info = get_level_info(user['level'])
    
    bot.send_message(
        message.chat.id,
        f"💰 ТВОЙ БАЛАНС 💰\n\n"
        f"Денег: {user['money']} шекелей\n"
        f"Уровень: {user['level']} ({level_info['name']})\n"
        f"Опыт: {user['exp']}\n"
        f"Всего заработал: {user['total_earned']}"
    )

def profile_command(message):
    user_id = message.from_user.id
    user = get_user(user_id)
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
    
    # Получаем серию бонусов
    streak = user.get('daily_streak', 0)
    
    msg = f"📊 ТВОЙ ПРОФИЛЬ 📊\n\n"
    msg += f"👤 Имя: @{user['username'] or 'Нет имени'}\n"
    msg += f"🏆 Уровень: {user['level']} - {level_info['name']}\n"
    msg += f"💰 Денег: {user['money']} шекелей\n"
    msg += f"⭐ Опыт: {user['exp']}\n"
    msg += f"📈 Всего заработал: {user['total_earned']}\n"
    msg += f"🎁 Серия бонусов: {streak} дней"
    
    if left > 0:
        msg += f"\n\n📊 До {next_level} уровня: {left} опыта ({prog}%)"
    
    bot.send_message(message.chat.id, msg)

def top_command(message):
    top = get_top_players(10)
    
    if not top:
        bot.send_message(message.chat.id, "🏆 Топ пока пуст!")
        return
    
    msg = "🏆 ТОП БОГАТЫХ ИГРОКОВ 🏆\n\n"
    
    for i, p in enumerate(top, 1):
        if i == 1:
            msg += f"👑 {i}. @{p['name']} - {p['money']} 💰\n"
        elif i == 2:
            msg += f"🥈 {i}. @{p['name']} - {p['money']} 💰\n"
        elif i == 3:
            msg += f"🥉 {i}. @{p['name']} - {p['money']} 💰\n"
        else:
            msg += f"{i}. @{p['name']} - {p['money']} 💰\n"
    
    bot.send_message(message.chat.id, msg)

def daily_bonus_command(message):
    user_id = message.from_user.id
    user = get_user(user_id)
    
    can, wait, streak = can_get_daily(user_id)
    
    if not can:
        hours = wait // 3600
        minutes = (wait % 3600) // 60
        bot.send_message(
            message.chat.id,
            f"🎁 ЕЖЕДНЕВНЫЙ БОНУС 🎁\n\n"
            f"⏰ Следующий бонус через: {hours} ч {minutes} мин\n"
            f"🔥 Твоя серия: {streak} дней\n\n"
            f"Заходи каждый день, чтобы увеличить серию!"
        )
        return
    
    total, base, streak_bonus = get_daily_bonus(streak)
    
    user['money'] += total
    user['total_earned'] += total
    user['last_daily'] = datetime.now().isoformat()
    user['daily_streak'] = streak
    save_users(users)
    
    # Добавляем опыт за бонус
    exp_gained = total // 3
    level_up = add_exp(user_id, exp_gained)
    
    msg = f"🎁 ЕЖЕДНЕВНЫЙ БОНУС 🎁\n\n"
    msg += f"💰 Ты получил: +{total} шекелей\n"
    msg += f"📦 Базовая награда: {base}\n"
    
    if streak_bonus > 0:
        msg += f"🔥 Бонус за серию ({streak} дн): +{streak_bonus}\n"
    
    msg += f"⭐ Опыт: +{exp_gained}\n"
    msg += f"💵 Теперь у тебя: {user['money']} шекелей\n\n"
    msg += f"🎯 Завтра бонус будет еще больше!"
    
    if level_up:
        new_lvl = get_level_info(user['level'])
        msg += f"\n\n🎉 НОВЫЙ УРОВЕНЬ! 🎉\n"
        msg += f"Теперь ты {user['level']} - {new_lvl['name']}"
    
    bot.send_message(message.chat.id, msg)

def slots_menu_command(message):
    user_id = message.from_user.id
    active_menus[user_id] = 'slots'
    
    kb = telebot.types.InlineKeyboardMarkup()
    kb.add(telebot.types.InlineKeyboardButton("10 💰", callback_data='slot_10'))
    kb.add(telebot.types.InlineKeyboardButton("50 💰", callback_data='slot_50'))
    kb.add(telebot.types.InlineKeyboardButton("100 💰", callback_data='slot_100'))
    bot.send_message(message.chat.id, "🎰 ВЫБЕРИ СТАВКУ:", reply_markup=kb)

def bj_menu_command(message):
    user_id = message.from_user.id
    active_menus[user_id] = 'bj'
    
    kb = telebot.types.InlineKeyboardMarkup()
    kb.add(telebot.types.InlineKeyboardButton("10 💰", callback_data='bj_10'))
    kb.add(telebot.types.InlineKeyboardButton("50 💰", callback_data='bj_50'))
    kb.add(telebot.types.InlineKeyboardButton("100 💰", callback_data='bj_100'))
    bot.send_message(message.chat.id, "🃏 ВЫБЕРИ СТАВКУ:", reply_markup=kb)

# ===== СЛОТЫ =====

@bot.callback_query_handler(func=lambda call: call.data.startswith('slot_'))
def slots_play(call):
    user_id = call.from_user.id
    
    if user_id not in active_menus or active_menus[user_id] != 'slots':
        bot.answer_callback_query(call.id, "❌ Нажми 'Слоты' сначала!", show_alert=True)
        return
    
    bet = int(call.data.split('_')[1])
    user = get_user(user_id)
    
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
        msg = f"🎰 {res[0]} | {res[1]} | {res[2]}\n\n✨ ПОБЕДА! +{win} ✨\n💰 {user['money']}"
    else:
        msg = f"🎰 {res[0]} | {res[1]} | {res[2]}\n\n💔 ПРОИГРЫШ\n💰 {user['money']}"
    
    save_users(users)
    
    try:
        bot.edit_message_text(msg, call.message.chat.id, call.message.message_id)
    except:
        bot.send_message(call.message.chat.id, msg)
    
    bot.answer_callback_query(call.id)
    
    if user_id in active_menus:
        del active_menus[user_id]

# ===== БЛЕК ДЖЕК =====

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

def format_cards(h):
    return ' '.join(h)

def new_deck():
    d = []
    for _ in range(4):
        for c in ['2','3','4','5','6','7','8','9','10','J','Q','K','A']:
            d.append(c)
    random.shuffle(d)
    return d

@bot.callback_query_handler(func=lambda call: call.data.startswith('bj_') and len(call.data) < 7)
def bj_new(call):
    user_id = call.from_user.id
    
    if user_id not in active_menus or active_menus[user_id] != 'bj':
        bot.answer_callback_query(call.id, "❌ Нажми 'Блек Джек' сначала!", show_alert=True)
        return
    
    bet = int(call.data.split('_')[1])
    user = get_user(user_id)
    
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
    
    msg = f"🃏 БЛЕК ДЖЕК\n\n"
    msg += f"💰 Ставка: {g['bet']}\n\n"
    msg += f"🤵 ДИЛЕР: {g['dealer'][0]} | ?\n"
    msg += f"Очки: {ds} + ?\n\n"
    msg += f"🎲 ТЫ: {format_cards(g['player'])}\n"
    msg += f"Очки: {ps}\n"
    
    kb = telebot.types.InlineKeyboardMarkup()
    kb.add(
        telebot.types.InlineKeyboardButton("🎴 ЕЩЕ", callback_data='bj_hit'),
        telebot.types.InlineKeyboardButton("✋ ХВАТИТ", callback_data='bj_stand')
    )
    
    try:
        bot.edit_message_text(msg, g['chat_id'], g['msg_id'], reply_markup=kb)
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
        msg = f"🃏 БЛЕК ДЖЕК\n\n"
        msg += f"💰 Ставка: {g['bet']}\n\n"
        msg += f"🎲 ТВОИ КАРТЫ: {format_cards(g['player'])}\n"
        msg += f"Очки: {ps} ❌ ПЕРЕБОР!\n\n"
        msg += f"💔 ТЫ ПРОИГРАЛ {g['bet']}!"
        
        try:
            bot.edit_message_text(msg, g['chat_id'], g['msg_id'])
        except:
            bot.send_message(g['chat_id'], msg)
        
        bot.answer_callback_query(call.id, "ПЕРЕБОР!", show_alert=True)
        del bj_games[user_id]
        return
    
    bj_games[user_id] = g
    
    msg = f"🃏 БЛЕК ДЖЕК\n\n"
    msg += f"💰 Ставка: {g['bet']}\n\n"
    msg += f"🤵 ДИЛЕР: {g['dealer'][0]} | ?\n"
    msg += f"🎲 ТЫ: {format_cards(g['player'])}\n"
    msg += f"Очки: {ps}\n"
    
    kb = telebot.types.InlineKeyboardMarkup()
    kb.add(
        telebot.types.InlineKeyboardButton("🎴 ЕЩЕ", callback_data='bj_hit'),
        telebot.types.InlineKeyboardButton("✋ ХВАТИТ", callback_data='bj_stand')
    )
    
    try:
        bot.edit_message_text(msg, g['chat_id'], g['msg_id'], reply_markup=kb)
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
    
    user = get_user(user_id)
    
    if ds > 21:
        win = g['bet'] * 2
        user['money'] += win
        user['total_earned'] += win
        add_exp(user_id, win // 4)
        res = f"🎉 ПОБЕДА! +{win}"
    elif ps > ds:
        win = g['bet'] * 2
        user['money'] += win
        user['total_earned'] += win
        add_exp(user_id, win // 4)
        res = f"🎉 ПОБЕДА! +{win}"
    elif ps < ds:
        res = f"💔 ПРОИГРЫШ! -{g['bet']}"
    else:
        user['money'] += g['bet']
        res = f"🤝 НИЧЬЯ! +{g['bet']}"
    
    save_users(users)
    
    msg = f"🃏 БЛЕК ДЖЕК\n\n"
    msg += f"💰 Ставка: {g['bet']}\n\n"
    msg += f"🤵 ДИЛЕР: {format_cards(g['dealer'])}\n"
    msg += f"Очки: {ds}\n\n"
    msg += f"🎲 ТЫ: {format_cards(g['player'])}\n"
    msg += f"Очки: {ps}\n\n"
    msg += f"{res}\n"
    msg += f"💰 Баланс: {user['money']}"
    
    try:
        bot.edit_message_text(msg, g['chat_id'], g['msg_id'])
    except:
        bot.send_message(g['chat_id'], msg)
    
    bot.answer_callback_query(call.id)
    del bj_games[user_id]

# ===== ЗАПУСК =====

print("=" * 40)
print("ХИТРЫЙ ЕВРЕЙ БОТ ЗАПУЩЕН!")
print("Текстовые команды: работа, баланс, профиль, топ, слоты, блекджек, бонус")
print("Ежедневный бонус: КД 12 часов")
print("=" * 40)

bot.infinity_polling()
