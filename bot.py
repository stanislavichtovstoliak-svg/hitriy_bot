import telebot
import random
import json
import os
from datetime import datetime
import time

TOKEN = '8672284943:AAEVBa7F9rKGQK76pkLr0vvHyDXKFCJDFos'
bot = telebot.TeleBot(TOKEN)

DATA_FILE = 'users.json'
data = {}
roulette_waiting = {}
slot_waiting = {}
bj_games = {}
duels = {}

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

PROMOCODES = {
    'шепельпрезидент': {'money': 2000, 'exp': 200},
    'тест': {'money': 2, 'exp': 0},
    'куниза200шекелей': {'money': 199, 'exp': 0},
    'ялюблюгрибы': {'money': 666, 'exp': 0},
}

FAIL_MESSAGES = {
    "Грузчик": ["💥 Уронил ящик! Штраф {} шекелей!", "📦 Разбил вазу! -{} шекелей!"],
    "Курьер": ["🛵 Проткнул колесо! Штраф {} шекелей!", "📬 Потерял посылку! -{} шекелей!"],
    "Автомеханик": ["🔧 Сорвал резьбу! Штраф {} шекелей!", "⚡ Забыл затянуть колесо! -{} шекелей!"],
    "Кладовщик": ["📦 Перепутал товар! Штраф {} шекелей!", "🏷 Потерял накладную! -{} шекелей!"],
    "Менеджер": ["📞 Поссорился с клиентом! Штраф {} шекелей!", "💼 Провалил презентацию! -{} шекелей!"],
    "Бухгалтер": ["📊 Ошибся в отчетности! Штраф {} шекелей!", "🧾 Потерял чеки! -{} шекелей!"],
    "Директор": ["🏢 Неудачная сделка! Штраф {} шекелей!", "📉 Акции упали! -{} шекелей!"],
    "Магнат": ["💎 Крипта провалилась! Штраф {} шекелей!", "🏭 Завод встал! -{} шекелей!"]
}

def load_data():
    global data
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
    else:
        data = {}

def save_data():
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_user(user_id, username=None):
    uid = str(user_id)
    if uid not in data:
        data[uid] = {
            'money': 500, 'level': 1, 'exp': 0, 'total_exp': 0,
            'last_work': None, 'username': username, 'total_earned': 0,
            'last_daily': None, 'daily_streak': 0, 'promos': []
        }
        save_data()
    else:
        if username and data[uid].get('username') != username:
            data[uid]['username'] = username
            save_data()
    return data[uid]

def add_exp(user_id, amount):
    user = get_user(user_id)
    user['exp'] += amount
    user['total_exp'] += amount
    leveled = False
    for lvl in range(user['level'] + 1, 9):
        if user['total_exp'] >= LEVELS[lvl]['exp_needed']:
            user['level'] = lvl
            leveled = True
    save_data()
    return leveled

def get_level_info(level):
    return LEVELS.get(level, LEVELS[1])

def get_top():
    top_list = [(u.get('username', 'Игрок'), u['money']) for u in data.values()]
    top_list.sort(key=lambda x: x[1], reverse=True)
    return top_list[:10]

# ========== СЛОТЫ С АНИМАЦИЕЙ ==========

SLOT_SYMBOLS = ['🍒', '🍊', '🍋', '🍉', '🍇', '💰', '💎', '🎰', '7️⃣']
SLOT_PAYOUTS = {
    ('7️⃣', '7️⃣', '7️⃣'): 50,
    ('🎰', '🎰', '🎰'): 40,
    ('💎', '💎', '💎'): 30,
    ('💰', '💰', '💰'): 25,
    ('🍇', '🍇', '🍇'): 20,
    ('🍉', '🍉', '🍉'): 15,
    ('🍒', '🍒', '🍒'): 10,
    ('🍊', '🍊', '🍊'): 10,
    ('🍋', '🍋', '🍋'): 10,
    ('🍒', '🍒', '🍊'): 5,
    ('🍊', '🍊', '🍒'): 5,
    ('🍒', '🍊', '🍋'): 3,
}

@bot.message_handler(func=lambda m: m.text and m.text.lower() in ['слоты', 'слот', 'казик'])
def slots_start(message):
    uid = message.from_user.id
    slot_waiting[uid] = 'waiting_bet'
    bot.send_message(message.chat.id, "🎰 Введи сумму ставки (минимум 10):")

@bot.message_handler(func=lambda m: m.from_user.id in slot_waiting and slot_waiting[m.from_user.id] == 'waiting_bet')
def slots_get_bet(message):
    uid = message.from_user.id
    try:
        bet = int(message.text.strip())
        if bet < 10:
            bot.send_message(message.chat.id, "❌ Минимум 10 шекелей!")
            return
    except:
        bot.send_message(message.chat.id, "❌ Введи число!")
        return
    
    user = get_user(uid, message.from_user.username)
    if user['money'] < bet:
        bot.send_message(message.chat.id, f"❌ Не хватает {bet} шекелей!")
        del slot_waiting[uid]
        return
    
    user['money'] -= bet
    save_data()
    
    slot_waiting[uid] = {'bet': bet, 'step': 0}
    
    # Анимация: 3 быстрых прокрутки
    msg = bot.send_message(message.chat.id, "🎰 КРУТИМ... 🎰\n\n🌀 | 🌀 | 🌀")
    time.sleep(0.5)
    
    for step in range(3):
        spin1 = random.choice(SLOT_SYMBOLS)
        spin2 = random.choice(SLOT_SYMBOLS)
        spin3 = random.choice(SLOT_SYMBOLS)
        bot.edit_message_text(f"🎰 КРУТИМ... 🎰\n\n{spin1} | {spin2} | {spin3}", message.chat.id, msg.message_id)
        time.sleep(0.4)
    
    # Финальный результат
    result = [random.choice(SLOT_SYMBOLS) for _ in range(3)]
    win = 0
    win_type = "💔 ПРОИГРЫШ"
    
    for combo, multiplier in SLOT_PAYOUTS.items():
        if tuple(result) == combo:
            win = bet * multiplier
            win_type = f"✨ ПОБЕДА! x{multiplier} ✨"
            break
    
    if win > 0:
        user['money'] += win
        user['total_earned'] += win
        add_exp(uid, win // 4)
        save_data()
    
    msg_text = f"🎰 РЕЗУЛЬТАТ 🎰\n\n"
    msg_text += f"┌───┬───┬───┐\n"
    msg_text += f"│ {result[0]} │ {result[1]} │ {result[2]} │\n"
    msg_text += f"└───┴───┴───┘\n\n"
    msg_text += f"{win_type}\n"
    if win > 0:
        msg_text += f"💰 +{win} шекелей!\n"
    msg_text += f"💵 Баланс: {user['money']}"
    
    bot.edit_message_text(msg_text, message.chat.id, msg.message_id)
    del slot_waiting[uid]

# ========== ДУЭЛИ (ПРОСТАЯ РАБОЧАЯ) ==========

@bot.message_handler(func=lambda m: m.text and m.text.lower().startswith('дуэль'))
def duel_start(message):
    uid = message.from_user.id
    user = get_user(uid, message.from_user.username)
    
    parts = message.text.split()
    if len(parts) < 3:
        bot.send_message(message.chat.id, "❌ Используй: дуэль @username сумма\nПример: дуэль @vanya 100")
        return
    
    target = parts[1].replace('@', '')
    try:
        bet = int(parts[2])
        if bet < 10:
            bot.send_message(message.chat.id, "❌ Минимальная ставка 10 шекелей!")
            return
    except:
        bot.send_message(message.chat.id, "❌ Введи число!")
        return
    
    if user['money'] < bet:
        bot.send_message(message.chat.id, f"❌ У тебя только {user['money']} шекелей!")
        return
    
    target_uid = None
    for uid_check, u in data.items():
        if u.get('username') == target:
            target_uid = uid_check
            break
    
    if not target_uid:
        bot.send_message(message.chat.id, f"❌ Игрок @{target} не найден!")
        return
    
    if str(target_uid) == str(uid):
        bot.send_message(message.chat.id, "❌ Нельзя дуэлиться с самим собой!")
        return
    
    target_user = get_user(target_uid)
    
    if target_user['money'] < bet:
        bot.send_message(message.chat.id, f"❌ У @{target} не хватает {bet} шекелей!")
        return
    
    duel_id = str(int(time.time()))
    duels[duel_id] = {
        'p1': uid, 'p2': target_uid, 'bet': bet, 'status': 'waiting', 'chat_id': message.chat.id
    }
    
    user['money'] -= bet
    target_user['money'] -= bet
    save_data()
    
    kb = telebot.types.InlineKeyboardMarkup()
    kb.add(
        telebot.types.InlineKeyboardButton("✅ ПРИНЯТЬ", callback_data=f'accept_{duel_id}'),
        telebot.types.InlineKeyboardButton("❌ ОТКАЗАТЬ", callback_data=f'decline_{duel_id}')
    )
    
    bot.send_message(message.chat.id,
        f"🥊 ДУЭЛЬ 🥊\n\n"
        f"👤 @{message.from_user.username} vs @{target}\n"
        f"💰 Ставка: {bet}\n\n"
        f"У обоих списано {bet}\n"
        f"Победитель забирает {bet*2}!",
        reply_markup=kb)

@bot.callback_query_handler(func=lambda call: call.data.startswith('accept_') or call.data.startswith('decline_'))
def duel_handler(call):
    action = 'accept' if 'accept' in call.data else 'decline'
    duel_id = call.data.split('_')[1]
    duel = duels.get(duel_id)
    
    if not duel:
        bot.answer_callback_query(call.id, "❌ Дуэль не найдена!", show_alert=True)
        return
    
    if call.from_user.id != duel['p2']:
        bot.answer_callback_query(call.id, "❌ Это не твоя дуэль!", show_alert=True)
        return
    
    if duel['status'] != 'waiting':
        bot.answer_callback_query(call.id, "❌ Дуэль уже завершена!", show_alert=True)
        return
    
    if action == 'accept':
        duel['status'] = 'active'
        p1 = get_user(duel['p1'])
        p2 = get_user(duel['p2'])
        
        r1 = random.randint(1, 6)
        r2 = random.randint(1, 6)
        
        msg = f"🎲 РЕЗУЛЬТАТ ДУЭЛИ 🎲\n\n"
        msg += f"🥊 @{p1['username']} vs @{p2['username']}\n"
        msg += f"💰 Ставка: {duel['bet']}\n\n"
        msg += f"🎲 @{p1['username']}: {r1}\n"
        msg += f"🎲 @{p2['username']}: {r2}\n\n"
        
        if r1 > r2:
            p1['money'] += duel['bet'] * 2
            msg += f"🏆 ПОБЕДА @{p1['username']}! +{duel['bet']*2}"
        elif r2 > r1:
            p2['money'] += duel['bet'] * 2
            msg += f"🏆 ПОБЕДА @{p2['username']}! +{duel['bet']*2}"
        else:
            p1['money'] += duel['bet']
            p2['money'] += duel['bet']
            msg += f"🤝 НИЧЬЯ! Деньги возвращены"
        
        save_data()
        bot.edit_message_text(msg, duel['chat_id'], call.message.message_id)
        bot.answer_callback_query(call.id, "✅ Дуэль началась!", show_alert=True)
        
    else:
        p1 = get_user(duel['p1'])
        p2 = get_user(duel['p2'])
        p1['money'] += duel['bet']
        p2['money'] += duel['bet']
        save_data()
        bot.edit_message_text(f"❌ @{p2['username']} отказался!\n💰 Деньги возвращены", 
                              duel['chat_id'], call.message.message_id)
        bot.answer_callback_query(call.id, "❌ Ты отказался!", show_alert=True)
    
    del duels[duel_id]

# ========== ОСТАЛЬНЫЕ КОМАНДЫ ==========

@bot.message_handler(commands=['start'])
def start_cmd(message):
    uid = message.from_user.id
    user = get_user(uid, message.from_user.username)
    level_info = get_level_info(user['level'])
    bot.send_message(message.chat.id,
        f"🎮 ХИТРЫЙ ЕВРЕЙ 🎮\n\n"
        f"👋 Привет, @{message.from_user.username}!\n"
        f"💰 Баланс: {user['money']} шекелей\n"
        f"📊 Уровень: {user['level']} - {level_info['name']}\n\n"
        f"📝 Напиши 'команды' для списка!\n\n"
        f"🎲 Удачи!")

@bot.message_handler(func=lambda m: m.text and m.text.lower() == 'команды')
def show_commands(message):
    msg = f"📋 СПИСОК КОМАНД 📋\n\n"
    msg += f"--- ИГРЫ ---\n"
    msg += f"• рулетка - игра в рулетку\n"
    msg += f"• слоты - слоты с анимацией\n"
    msg += f"• блекджек - игра в 21\n"
    msg += f"• дуэль @user сумма - дуэль\n\n"
    msg += f"--- ЗАРАБОТОК ---\n"
    msg += f"• работа / фарм - работа (КД 10 мин)\n"
    msg += f"• бонус - ежедневный (КД 12 ч)\n\n"
    msg += f"--- ИНФО ---\n"
    msg += f"• баланс - проверить деньги\n"
    msg += f"• профиль - статистика\n"
    msg += f"• топ - топ богатых\n\n"
    msg += f"--- ПРОМОКОДЫ ---\n"
    msg += f"#промо шепельпрезидент - 2000💰\n"
    msg += f"#промо тест - 2💰\n"
    msg += f"#промо куниза200шекелей - 199💰\n"
    msg += f"#промо ялюблюгрибы - 666💰"
    bot.send_message(message.chat.id, msg)

@bot.message_handler(func=lambda m: m.text and m.text.lower() in ['работа', 'фарм', 'работка'])
def work_cmd(message):
    uid = message.from_user.id
    user = get_user(uid, message.from_user.username)
    level_info = get_level_info(user['level'])
    
    if user['last_work']:
        last = datetime.fromisoformat(user['last_work'])
        diff = (datetime.now() - last).total_seconds()
        if diff < 600:
            rem = int(600 - diff)
            m = rem // 60
            s = rem % 60
            bot.send_message(message.chat.id, f"⏰ Отдыхай {m} мин {s} сек")
            return
    
    base = random.randint(level_info['salary_min'], level_info['salary_max'])
    fail = random.randint(1, 100) <= 5
    
    if fail:
        penalty = random.randint(int(base * 0.3), int(base * 0.7))
        earned = -penalty
        user['money'] += earned
        user['total_earned'] += earned
        messages = FAIL_MESSAGES.get(level_info['name'], ["Ошибка! Штраф {}"])
        fail_text = random.choice(messages)
        msg = f"😫 НЕУДАЧА!\n\n💼 {level_info['name']}\n{fail_text.format(penalty)}\n💵 Баланс: {user['money']}"
        exp_change = -penalty // 4
    else:
        earned = base
        user['money'] += earned
        user['total_earned'] += earned
        msg = f"🌾 ТЫ ПОРАБОТАЛ! 🌾\n\n💼 {level_info['name']}\n💰 +{earned} шекелей"
        exp_change = earned // 2
    
    user['last_work'] = datetime.now().isoformat()
    leveled = add_exp(uid, exp_change)
    msg += f"\n⭐ {exp_change:+} опыта\n💵 Баланс: {user['money']}"
    
    if leveled and earned > 0:
        new_level = get_level_info(user['level'])
        msg += f"\n\n🎉 НОВЫЙ УРОВЕНЬ! {user['level']} - {new_level['name']}"
    
    save_data()
    bot.send_message(message.chat.id, msg)

@bot.message_handler(func=lambda m: m.text and m.text.lower() in ['баланс', 'деньги'])
def balance_cmd(message):
    user = get_user(message.from_user.id, message.from_user.username)
    level_info = get_level_info(user['level'])
    bot.send_message(message.chat.id,
        f"💰 БАЛАНС 💰\n\n💵 {user['money']} шекелей\n📊 Уровень {user['level']} - {level_info['name']}\n⭐ Опыт: {user['exp']}\n📈 Всего: {user['total_earned']}")

@bot.message_handler(func=lambda m: m.text and m.text.lower() in ['профиль', 'стата'])
def profile_cmd(message):
    user = get_user(message.from_user.id, message.from_user.username)
    level_info = get_level_info(user['level'])
    
    next_lvl = user['level'] + 1
    if next_lvl <= 8:
        need = LEVELS[next_lvl]['exp_needed']
        have = user['total_exp']
        left = need - have
        prog = int((have / need) * 100) if need > 0 else 100
        bar = '▓' * (prog // 10) + '░' * (10 - (prog // 10))
    else:
        left, prog, bar = 0, 100, '▓▓▓▓▓▓▓▓▓▓'
    
    msg = f"📊 ПРОФИЛЬ 📊\n\n"
    msg += f"👤 @{user.get('username') or 'Нет имени'}\n"
    msg += f"🏆 Уровень {user['level']} - {level_info['name']}\n"
    msg += f"💰 {user['money']} шекелей\n"
    msg += f"⭐ Опыт: {user['exp']}\n"
    msg += f"📈 Всего: {user['total_earned']}\n"
    msg += f"🎁 Серия: {user.get('daily_streak', 0)}"
    if left > 0:
        msg += f"\n\n📊 До {next_lvl} уровня:\n{bar} {prog}%\nОсталось: {left} опыта"
    bot.send_message(message.chat.id, msg)

@bot.message_handler(func=lambda m: m.text and m.text.lower() in ['топ', 'топ10', 'лидеры'])
def top_cmd(message):
    top = get_top()
    if not top:
        bot.send_message(message.chat.id, "🏆 Топ пока пуст!")
        return
    msg = "🏆 ТОП БОГАТЫХ 🏆\n\n"
    for i, (name, money) in enumerate(top, 1):
        if i == 1:
            msg += f"👑 {i}. @{name} - {money}\n"
        elif i == 2:
            msg += f"🥈 {i}. @{name} - {money}\n"
        elif i == 3:
            msg += f"🥉 {i}. @{name} - {money}\n"
        else:
            msg += f"{i}. @{name} - {money}\n"
    bot.send_message(message.chat.id, msg)

@bot.message_handler(func=lambda m: m.text and m.text.lower() in ['бонус', 'ежедневный', 'daily'])
def daily_cmd(message):
    uid = message.from_user.id
    user = get_user(uid, message.from_user.username)
    
    if user.get('last_daily'):
        last = datetime.fromisoformat(user['last_daily'])
        diff = (datetime.now() - last).total_seconds()
        if diff < 43200:
            h = int((43200 - diff) // 3600)
            m = int(((43200 - diff) % 3600) // 60)
            bot.send_message(message.chat.id, f"🎁 Бонус через {h}ч {m}мин\n🔥 Серия: {user.get('daily_streak', 0)}")
            return
    
    bonus = random.randint(50, 200)
    user['money'] += bonus
    user['total_earned'] += bonus
    user['last_daily'] = datetime.now().isoformat()
    user['daily_streak'] = user.get('daily_streak', 0) + 1
    leveled = add_exp(uid, bonus // 3)
    
    msg = f"🎁 ЕЖЕДНЕВНЫЙ БОНУС 🎁\n\n💰 +{bonus}\n⭐ +{bonus//3}\n🔥 Серия: {user['daily_streak']}\n💵 Баланс: {user['money']}"
    if leveled:
        new_level = get_level_info(user['level'])
        msg += f"\n\n🎉 НОВЫЙ УРОВЕНЬ! {user['level']} - {new_level['name']}"
    save_data()
    bot.send_message(message.chat.id, msg)

@bot.message_handler(func=lambda m: m.text and m.text.lower().startswith('#промо'))
def promo_cmd(message):
    uid = message.from_user.id
    user = get_user(uid, message.from_user.username)
    promo = message.text.lower().replace('#промо', '').strip()
    
    if promo in user.get('promos', []):
        bot.send_message(message.chat.id, f"❌ Промокод {promo} уже использован!")
        return
    
    if promo in PROMOCODES:
        p = PROMOCODES[promo]
        user['money'] += p['money']
        user['total_earned'] += p['money']
        user['promos'].append(promo)
        leveled = add_exp(uid, p['exp'])
        msg = f"🎁 ПРОМОКОД АКТИВИРОВАН!\n✅ {promo}\n💰 +{p['money']}"
        if p['exp'] > 0:
            msg += f"\n⭐ +{p['exp']}"
        msg += f"\n💵 Баланс: {user['money']}"
        if leveled:
            new_level = get_level_info(user['level'])
            msg += f"\n\n🎉 НОВЫЙ УРОВЕНЬ! {user['level']} - {new_level['name']}"
        save_data()
        bot.send_message(message.chat.id, msg)
    else:
        bot.send_message(message.chat.id, f"❌ Промокод {promo} не найден!")

# ========== РУЛЕТКА ==========

@bot.message_handler(func=lambda m: m.text and m.text.lower() in ['рулетка', 'рулетку'])
def roulette_menu(message):
    kb = telebot.types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        telebot.types.InlineKeyboardButton("🔴 КРАСНОЕ", callback_data='roul_red'),
        telebot.types.InlineKeyboardButton("⚫ ЧЕРНОЕ", callback_data='roul_black'),
        telebot.types.InlineKeyboardButton("🟢 ЗЕЛЕНЫЙ", callback_data='roul_green'),
        telebot.types.InlineKeyboardButton("📊 ЧЕТ", callback_data='roul_even'),
        telebot.types.InlineKeyboardButton("📊 НЕЧЕТ", callback_data='roul_odd')
    )
    bot.send_message(message.chat.id, "🎡 РУЛЕТКА 🎡\nВыбери тип ставки:", reply_markup=kb)

@bot.callback_query_handler(func=lambda call: call.data.startswith('roul_'))
def roulette_bet(call):
    uid = call.from_user.id
    bet_type = call.data.split('_')[1]
    roulette_waiting[uid] = bet_type
    bot.edit_message_text("🎡 РУЛЕТКА 🎡\n\n💰 Введи сумму (мин 10):", call.message.chat.id, call.message.message_id)
    bot.answer_callback_query(call.id)

@bot.message_handler(func=lambda m: m.from_user.id in roulette_waiting)
def roulette_amount(message):
    uid = message.from_user.id
    bet_type = roulette_waiting[uid]
    try:
        bet = int(message.text.strip())
        if bet < 10:
            bot.send_message(message.chat.id, "❌ Минимум 10!")
            return
    except:
        bot.send_message(message.chat.id, "❌ Введи число!")
        del roulette_waiting[uid]
        return
    
    user = get_user(uid, message.from_user.username)
    if user['money'] < bet:
        bot.send_message(message.chat.id, f"❌ Не хватает {bet}!")
        del roulette_waiting[uid]
        return
    
    user['money'] -= bet
    save_data()
    
    num = random.randint(0, 36)
    if num == 0:
        color, emoji = 'green', '🟢'
    elif num in [1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36]:
        color, emoji = 'red', '🔴'
    else:
        color, emoji = 'black', '⚫'
    
    win = 0
    if bet_type == 'red' and color == 'red':
        win = bet * 2
    elif bet_type == 'black' and color == 'black':
        win = bet * 2
    elif bet_type == 'green' and num == 0:
        win = bet * 35
    elif bet_type == 'even' and num > 0 and num % 2 == 0:
        win = bet * 2
    elif bet_type == 'odd' and num > 0 and num % 2 == 1:
        win = bet * 2
    
    names = {'red':'КРАСНОЕ', 'black':'ЧЕРНОЕ', 'green':'ЗЕЛЕНЫЙ', 'even':'ЧЕТ', 'odd':'НЕЧЕТ'}
    
    if win > 0:
        user['money'] += win
        user['total_earned'] += win
        add_exp(uid, win // 4)
        msg = f"🎡 РУЛЕТКА 🎡\n\n🎲 {emoji} {num}\n🎯 {names[bet_type]} {bet}\n💰 ВЫИГРЫШ: +{win}\n💵 Баланс: {user['money']}"
    else:
        msg = f"🎡 РУЛЕТКА 🎡\n\n🎲 {emoji} {num}\n🎯 {names[bet_type]} {bet}\n💔 ПРОИГРЫШ\n💵 Баланс: {user['money']}"
    
    save_data()
    bot.send_message(message.chat.id, msg)
    del roulette_waiting[uid]

# ========== БЛЕКДЖЕК ==========

def card_val(c):
    if c in ['J', 'Q', 'K']: return 10
    elif c == 'A': return 11
    else: return int(c)

def hand_sum(hand):
    s = sum(card_val(c) for c in hand)
    aces = hand.count('A')
    while s > 21 and aces > 0:
        s -= 10
        aces -= 1
    return s

def new_deck():
    d = []
    for _ in range(4):
        for c in ['2','3','4','5','6','7','8','9','10','J','Q','K','A']:
            d.append(c)
    random.shuffle(d)
    return d

@bot.message_handler(func=lambda m: m.text and m.text.lower() in ['блекджек', 'блек джек', 'blackjack', '21'])
def bj_start(message):
    kb = telebot.types.InlineKeyboardMarkup()
    kb.add(
        telebot.types.InlineKeyboardButton("🔟", callback_data='bj_10'),
        telebot.types.InlineKeyboardButton("5️⃣0️⃣", callback_data='bj_50'),
        telebot.types.InlineKeyboardButton("1️⃣0️⃣0️⃣", callback_data='bj_100')
    )
    bot.send_message(message.chat.id, "🃏 ВЫБЕРИ СТАВКУ", reply_markup=kb)

@bot.callback_query_handler(func=lambda call: call.data.startswith('bj_'))
def bj_new(call):
    uid = call.from_user.id
    bet = int(call.data.split('_')[1])
    user = get_user(uid, call.from_user.username)
    if user['money'] < bet:
        bot.answer_callback_query(call.id, f"❌ Не хватает {bet}!", show_alert=True)
        return
    user['money'] -= bet
    save_data()
    deck = new_deck()
    bj_games[uid] = {
        'bet': bet, 'player': [deck.pop(), deck.pop()], 'dealer': [deck.pop(), deck.pop()],
        'deck': deck, 'chat_id': call.message.chat.id, 'msg_id': call.message.message_id
    }
    bj_show(call.message.chat.id, uid, call.message.message_id)
    bot.answer_callback_query(call.id)

def bj_show(chat_id, uid, msg_id):
    g = bj_games.get(uid)
    if not g: return
    ps = hand_sum(g['player'])
    ds = hand_sum([g['dealer'][0]])
    msg = f"🃏 БЛЕК ДЖЕК 🃏\n\n💰 СТАВКА: {g['bet']}\n\n"
    msg += f"👨‍💼 ДИЛЕР: {g['dealer'][0]} | ?\n⭐ {ds} + ?\n\n"
    msg += f"🎲 ТЫ: {' '.join(g['player'])}\n⭐ {ps}"
    kb = telebot.types.InlineKeyboardMarkup()
    kb.add(
        telebot.types.InlineKeyboardButton("🎴 ЕЩЕ", callback_data='bj_hit'),
        telebot.types.InlineKeyboardButton("✋ ХВАТИТ", callback_data='bj_stand')
    )
    try:
        bot.edit_message_text(msg, chat_id, msg_id, reply_markup=kb)
    except: pass

@bot.callback_query_handler(func=lambda call: call.data == 'bj_hit')
def bj_hit(call):
    uid = call.from_user.id
    g = bj_games.get(uid)
    if not g:
        bot.answer_callback_query(call.id, "❌ Игра не найдена!", show_alert=True)
        return
    card = g['deck'].pop()
    g['player'].append(card)
    ps = hand_sum(g['player'])
    if ps > 21:
        msg = f"🃏 БЛЕК ДЖЕК 🃏\n\n💰 СТАВКА: {g['bet']}\n\n🎲 {' '.join(g['player'])}\n⭐ {ps} ❌ ПЕРЕБОР!\n\n💔 ТЫ ПРОИГРАЛ {g['bet']}!"
        try:
            bot.edit_message_text(msg, g['chat_id'], g['msg_id'])
        except: pass
        bot.answer_callback_query(call.id, "ПЕРЕБОР!", show_alert=True)
        del bj_games[uid]
        return
    bj_games[uid] = g
    msg = f"🃏 БЛЕК ДЖЕК 🃏\n\n💰 СТАВКА: {g['bet']}\n\n"
    msg += f"👨‍💼 ДИЛЕР: {g['dealer'][0]} | ?\n"
    msg += f"🎲 ТЫ: {' '.join(g['player'])}\n⭐ {ps}"
    kb = telebot.types.InlineKeyboardMarkup()
    kb.add(
        telebot.types.InlineKeyboardButton("🎴 ЕЩЕ", callback_data='bj_hit'),
        telebot.types.InlineKeyboardButton("✋ ХВАТИТ", callback_data='bj_stand')
    )
    try:
        bot.edit_message_text(msg, g['chat_id'], g['msg_id'], reply_markup=kb)
    except: pass
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data == 'bj_stand')
def bj_stand(call):
    uid = call.from_user.id
    g = bj_games.get(uid)
    if not g:
        bot.answer_callback_query(call.id, "❌ Игра не найдена!", show_alert=True)
        return
    ps = hand_sum(g['player'])
    ds = hand_sum(g['dealer'])
    while ds < 17:
        ds = hand_sum(g['dealer'])
    user = get_user(uid, call.from_user.username)
    if ds > 21 or ps > ds:
        win = g['bet'] * 2
        user['money'] += win
        user['total_earned'] += win
        add_exp(uid, win // 4)
        res = f"🎉 ПОБЕДА! +{win}"
    elif ps < ds:
        res = f"💔 ПРОИГРЫШ! -{g['bet']}"
    else:
        user['money'] += g['bet']
        res = f"🤝 НИЧЬЯ! +{g['bet']}"
    save_data()
    msg = f"🃏 БЛЕК ДЖЕК 🃏\n\n💰 СТАВКА: {g['bet']}\n\n"
    msg += f"👨‍💼 ДИЛЕР: {' '.join(g['dealer'])}\n⭐ {ds}\n\n"
    msg += f"🎲 ТЫ: {' '.join(g['player'])}\n⭐ {ps}\n\n{res}\n💰 БАЛАНС: {user['money']}"
    try:
        bot.edit_message_text(msg, g['chat_id'], g['msg_id'])
    except: pass
    bot.answer_callback_query(call.id)
    del bj_games[uid]

# ========== ЗАПУСК ==========

load_data()
print("=" * 50)
print("ХИТРЫЙ ЕВРЕЙ БОТ ЗАПУЩЕН!")
print("Слоты с анимацией - работают")
print("Дуэли - работают")
print("=" * 50)

bot.infinity_polling()
