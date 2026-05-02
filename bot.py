import telebot
import random
import json
import os
from datetime import datetime
import time

# ===== ТОКЕН (ПРЯМО В КОДЕ) =====
TOKEN = '8672284943:AAGr068cDybidNBehyS0Dcst5wj0BcGjLAU'
# =================================

bot = telebot.TeleBot(TOKEN)

DATA_FILE = 'users.json'
active_menus = {}
bj_games = {}
last_command_time = {}

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

def keyboard():
    kb = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btns = ['🌾 Работа', '💰 Баланс', '📊 Профиль', '🏆 Топ', '🎁 Бонус']
    kb.add(*btns)
    kb.add('🎰 Слоты', '🃏 Блек Джек')
    return kb

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    user = get_user(user_id)
    user['username'] = message.from_user.username
    save_users(users)
    
    bot.send_message(
        message.chat.id,
        f"🎮 ХИТРЫЙ ЕВРЕЙ 🎮\n\n"
        f"💰 Стартовый капитал: 500 шекелей\n"
        f"📊 Твой уровень: {user['level']} - {LEVELS[user['level']]['name']}\n\n"
        f"📝 КОМАНДЫ:\n"
        f"• Работа - заработать (КД 10 мин)\n"
        f"• Бонус - ежедневный (КД 12 ч)\n"
        f"• Баланс - проверить деньги\n"
        f"• Профиль - твоя стата\n"
        f"• Топ - богатые игроки\n"
        f"• Слоты - играть\n"
        f"• Блекджек - играть в 21",
        reply_markup=keyboard()
    )

@bot.message_handler(func=lambda m: m.text == '💰 Баланс')
def balance(message):
    user = get_user(message.from_user.id)
    bot.send_message(
        message.chat.id,
        f"💰 Баланс: {user['money']} шекелей\n"
        f"📊 Уровень: {user['level']} - {LEVELS[user['level']]['name']}"
    )

@bot.message_handler(func=lambda m: m.text == '📊 Профиль')
def profile(message):
    user = get_user(message.from_user.id)
    msg = f"📊 ПРОФИЛЬ 📊\n\n"
    msg += f"👤 Игрок: @{user['username'] or 'Нет имени'}\n"
    msg += f"🏆 Уровень: {user['level']} - {LEVELS[user['level']]['name']}\n"
    msg += f"💰 Денег: {user['money']} шекелей\n"
    msg += f"⭐ Опыт: {user['exp']}\n"
    msg += f"📈 Всего заработал: {user['total_earned']}"
    bot.send_message(message.chat.id, msg)

@bot.message_handler(func=lambda m: m.text == '🏆 Топ')
def top_command(message):
    top = []
    for uid, data in users.items():
        name = data.get('username', 'Игрок')
        top.append({'name': name, 'money': data['money']})
    top.sort(key=lambda x: x['money'], reverse=True)
    top = top[:10]
    
    if not top:
        bot.send_message(message.chat.id, "🏆 Топ пока пуст!")
        return
    
    msg = "🏆 ТОП БОГАТЫХ 🏆\n\n"
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

@bot.message_handler(func=lambda m: m.text == '🌾 Работа')
def work(message):
    user = get_user(message.from_user.id)
    level = LEVELS[user['level']]
    
    if user['last_work']:
        last = datetime.fromisoformat(user['last_work'])
        diff = (datetime.now() - last).total_seconds()
        if diff < 600:
            rem = 600 - diff
            m = int(rem // 60)
            s = int(rem % 60)
            bot.send_message(message.chat.id, f"⏰ Отдыхай {m} мин {s} сек")
            return
    
    earned = random.randint(level['salary_min'], level['salary_max'])
    user['money'] += earned
    user['total_earned'] += earned
    user['exp'] += earned // 2
    user['last_work'] = datetime.now().isoformat()
    
    # Проверка повышения уровня
    for lvl in range(user['level'] + 1, 9):
        if user['total_earned'] >= LEVELS[lvl]['exp_needed']:
            user['level'] = lvl
        else:
            break
    
    save_users(users)
    bot.send_message(message.chat.id, f"🌾 +{earned} шекелей!\n💰 Баланс: {user['money']}")

@bot.message_handler(func=lambda m: m.text == '🎁 Бонус')
def daily_bonus(message):
    user = get_user(message.from_user.id)
    
    if user['last_daily']:
        last = datetime.fromisoformat(user['last_daily'])
        diff = (datetime.now() - last).total_seconds()
        if diff < 43200:
            hours = int((43200 - diff) // 3600)
            minutes = int(((43200 - diff) % 3600) // 60)
            bot.send_message(message.chat.id, f"🎁 Бонус через {hours} ч {minutes} мин")
            return
    
    bonus = random.randint(50, 200)
    user['money'] += bonus
    user['total_earned'] += bonus
    user['last_daily'] = datetime.now().isoformat()
    if 'daily_streak' not in user:
        user['daily_streak'] = 0
    user['daily_streak'] += 1
    save_users(users)
    
    bot.send_message(message.chat.id, f"🎁 +{bonus} шекелей!\n💰 Баланс: {user['money']}\n🔥 Серия: {user['daily_streak']} дней")

@bot.message_handler(func=lambda m: m.text == '🎰 Слоты')
def slots_menu(message):
    user_id = message.from_user.id
    active_menus[user_id] = 'slots'
    
    kb = telebot.types.InlineKeyboardMarkup()
    kb.add(telebot.types.InlineKeyboardButton("10 💰", callback_data='slot_10'))
    kb.add(telebot.types.InlineKeyboardButton("50 💰", callback_data='slot_50'))
    kb.add(telebot.types.InlineKeyboardButton("100 💰", callback_data='slot_100'))
    bot.send_message(message.chat.id, "🎰 ВЫБЕРИ СТАВКУ:", reply_markup=kb)

@bot.callback_query_handler(func=lambda call: call.data.startswith('slot_'))
def slots_play(call):
    user_id = call.from_user.id
    
    if user_id not in active_menus or active_menus[user_id] != 'slots':
        bot.answer_callback_query(call.id, "❌ Не твоя кнопка!", show_alert=True)
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
        msg = f"✨ ПОБЕДА! +{win} ✨\n💰 {user['money']}"
    else:
        msg = f"💔 ПРОИГРЫШ\n💰 {user['money']}"
    
    save_users(users)
    
    try:
        bot.edit_message_text(f"🎰 {res[0]} | {res[1]} | {res[2]}\n\n{msg}", 
                              call.message.chat.id, call.message.message_id)
    except:
        pass
    
    bot.answer_callback_query(call.id)
    
    if user_id in active_menus:
        del active_menus[user_id]

@bot.message_handler(func=lambda m: m.text == '🃏 Блек Джек')
def bj_menu(message):
    user_id = message.from_user.id
    active_menus[user_id] = 'bj'
    
    kb = telebot.types.InlineKeyboardMarkup()
    kb.add(telebot.types.InlineKeyboardButton("10 💰", callback_data='bj_10'))
    kb.add(telebot.types.InlineKeyboardButton("50 💰", callback_data='bj_50'))
    kb.add(telebot.types.InlineKeyboardButton("100 💰", callback_data='bj_100'))
    bot.send_message(message.chat.id, "🃏 ВЫБЕРИ СТАВКУ:", reply_markup=kb)

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
    msg += f"🎲 ТЫ: {' '.join(g['player'])}\n"
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
        msg += f"🎲 ТВОИ КАРТЫ: {' '.join(g['player'])}\n"
        msg += f"Очки: {ps} ❌ ПЕРЕБОР!\n\n"
        msg += f"💔 ТЫ ПРОИГРАЛ {g['bet']}!"
        
        try:
            bot.edit_message_text(msg, g['chat_id'], g['msg_id'])
        except:
            pass
        
        bot.answer_callback_query(call.id, "ПЕРЕБОР!", show_alert=True)
        del bj_games[user_id]
        return
    
    bj_games[user_id] = g
    
    msg = f"🃏 БЛЕК ДЖЕК\n\n"
    msg += f"💰 Ставка: {g['bet']}\n\n"
    msg += f"🤵 ДИЛЕР: {g['dealer'][0]} | ?\n"
    msg += f"🎲 ТЫ: {' '.join(g['player'])}\n"
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
        res = f"🎉 ПОБЕДА! +{win}"
    elif ps > ds:
        win = g['bet'] * 2
        user['money'] += win
        user['total_earned'] += win
        res = f"🎉 ПОБЕДА! +{win}"
    elif ps < ds:
        res = f"💔 ПРОИГРЫШ! -{g['bet']}"
    else:
        user['money'] += g['bet']
        res = f"🤝 НИЧЬЯ! +{g['bet']}"
    
    save_users(users)
    
    msg = f"🃏 БЛЕК ДЖЕК\n\n"
    msg += f"💰 Ставка: {g['bet']}\n\n"
    msg += f"🤵 ДИЛЕР: {' '.join(g['dealer'])}\n"
    msg += f"Очки: {ds}\n\n"
    msg += f"🎲 ТЫ: {' '.join(g['player'])}\n"
    msg += f"Очки: {ps}\n\n"
    msg += f"{res}\n"
    msg += f"💰 Баланс: {user['money']}"
    
    try:
        bot.edit_message_text(msg, g['chat_id'], g['msg_id'])
    except:
        pass
    
    bot.answer_callback_query(call.id)
    del bj_games[user_id]

print("🤖 ХИТРЫЙ ЕВРЕЙ БОТ ЗАПУЩЕН!")
print(f"💬 Бот: @{bot.get_me().username}")

bot.infinity_polling()
