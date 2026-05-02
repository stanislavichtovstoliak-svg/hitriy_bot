import telebot
import random
import json
import os
from datetime import datetime
import time
import threading

TOKEN = '8672284943:AAEVBa7F9rKGQK76pkLr0vvHyDXKFCJDFos'
bot = telebot.TeleBot(TOKEN)

DATA_FILE = 'users.json'

# ========== ЖЕЛЕЗОБЕТОННЫЕ СОХРАНЕНИЯ ==========
def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_data(data):
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except:
        return False

data = load_data()

DEFAULT_USER = {
    'money': 500, 'level': 1, 'exp': 0, 'total_exp': 0,
    'last_work': None, 'username': None, 'total_earned': 0,
    'last_daily': None, 'daily_streak': 0, 'promos': [],
    'work_count': 0, 'slot_wins': 0, 'roulette_wins': 0,
    'bet_wins': 0, 'achievements': []
}

# ========== НОВЫЕ ПРОФЕССИИ (12 УРОВНЕЙ) ==========
LEVELS = {
    1: {"name": "🫣 Грузчик", "salary_min": 5, "salary_max": 50, "exp_needed": 0},
    2: {"name": "🛵 Курьер", "salary_min": 15, "salary_max": 80, "exp_needed": 100},
    3: {"name": "🔧 Автомеханик", "salary_min": 30, "salary_max": 120, "exp_needed": 250},
    4: {"name": "📦 Кладовщик", "salary_min": 50, "salary_max": 160, "exp_needed": 450},
    5: {"name": "🍕 Доставщик", "salary_min": 70, "salary_max": 200, "exp_needed": 700},
    6: {"name": "🛠 Сварщик", "salary_min": 90, "salary_max": 240, "exp_needed": 1000},
    7: {"name": "📊 Менеджер", "salary_min": 120, "salary_max": 280, "exp_needed": 1400},
    8: {"name": "🏦 Бухгалтер", "salary_min": 150, "salary_max": 320, "exp_needed": 1900},
    9: {"name": "🏗 Прораб", "salary_min": 180, "salary_max": 360, "exp_needed": 2500},
    10: {"name": "👔 Директор", "salary_min": 220, "salary_max": 420, "exp_needed": 3200},
    11: {"name": "💎 Бизнесмен", "salary_min": 260, "salary_max": 480, "exp_needed": 4000},
    12: {"name": "👑 Магнат", "salary_min": 300, "salary_max": 600, "exp_needed": 5000},
}

ACHIEVEMENTS = {
    'work_10': {'name': "Трудоголик", 'reward': 100},
    'work_50': {'name': "Стахановец", 'reward': 500},
    'work_100': {'name': "Машина", 'reward': 1000},
    'work_500': {'name': "Терминатор", 'reward': 5000},
    'win_slot': {'name': "Счастливчик", 'reward': 50},
    'win_roulette': {'name': "Фортуна", 'reward': 50},
    'win_bet': {'name': "Лучший каппер", 'reward': 100},
    'money_1000': {'name': "Тысячник", 'reward': 200},
    'money_5000': {'name': "Богач", 'reward': 700},
    'money_10000': {'name': "Магнат", 'reward': 1500},
    'money_50000': {'name': "Крез", 'reward': 5000},
    'level_5': {'name': "Профи", 'reward': 300},
    'level_8': {'name': "Эксперт", 'reward': 700},
    'level_10': {'name': "Мастер", 'reward': 1200},
    'level_12': {'name': "Легенда", 'reward': 2000},
    'daily_streak': {'name': "Серийный", 'reward': 500},
    'daily_streak_30': {'name': "Железный", 'reward': 3000},
}

# ========== НОВЫЙ ПРОМОКОД ==========
PROMOCODES = {
    'шепельпрезидент': {'money': 2000, 'exp': 200},
    'тест': {'money': 2, 'exp': 0},
    'куниза200шекелей': {'money': 199, 'exp': 0},
    'ялюблюгрибы': {'money': 666, 'exp': 0},
    'яустал': {'money': 228, 'exp': 0},
}

FAIL_MESSAGES = {
    "Грузчик": ["Уронил ящик! -{}💰", "Разбил вазу! -{}💰"],
    "Курьер": ["Проткнул колесо! -{}💰", "Потерял посылку! -{}💰"],
    "Автомеханик": ["Сорвал резьбу! -{}💰", "Забыл затянуть колесо! -{}💰"],
    "Кладовщик": ["Перепутал товар! -{}💰", "Потерял накладную! -{}💰"],
    "Доставщик": ["Пролил кофе клиенту! -{}💰", "Перепутал заказ! -{}💰"],
    "Сварщик": ["Прожег дыру! -{}💰", "Уронил баллон! -{}💰"],
    "Менеджер": ["Поссорился с клиентом! -{}💰", "Провалил презентацию! -{}💰"],
    "Бухгалтер": ["Ошибся в отчетности! -{}💰", "Потерял чеки! -{}💰"],
    "Прораб": ["Бригада не вышла! -{}💰", "Сгорел материал! -{}💰"],
    "Директор": ["Неудачная сделка! -{}💰", "Акции упали! -{}💰"],
    "Бизнесмен": ["Крипта обвалилась! -{}💰", "Партнер кинул! -{}💰"],
    "Магнат": ["Банкротство филиала! -{}💰", "Рейдерский захват! -{}💰"],
}

# ========== МАШИНЫ ДЛЯ СТАВОК ==========
CARS = [
    {"name": "🏎️ ФЕРРАРИ", "emoji": "🏎️", "coefficient": 6.0, "chance": 10},
    {"name": "🚗 ЛАМБОРДЖИНИ", "emoji": "🚗", "coefficient": 4.0, "chance": 15},
    {"name": "🚙 ПОРШЕ", "emoji": "🚙", "coefficient": 3.0, "chance": 20},
    {"name": "🚕 БМВ", "emoji": "🚕", "coefficient": 2.5, "chance": 25},
    {"name": "🚓 АУДИ", "emoji": "🚓", "coefficient": 2.0, "chance": 30},
    {"name": "🚜 ЗАПОРОЖЕЦ", "emoji": "🚜", "coefficient": 10.0, "chance": 5},
]

# ========== ПЕРЕМЕННЫЕ ==========
slot_waiting = {}
roulette_waiting = {}
race_active = False
race_bets = {}
race_events = []
race_start_time = None

# ========== ФУНКЦИИ ==========
def get_user(user_id, username=None):
    uid = str(user_id)
    if uid not in data:
        data[uid] = DEFAULT_USER.copy()
        data[uid]['username'] = username
        save_data(data)
    else:
        if username and data[uid].get('username') != username:
            data[uid]['username'] = username
            save_data(data)
        for key in DEFAULT_USER:
            if key not in data[uid]:
                data[uid][key] = DEFAULT_USER[key]
                save_data(data)
    return data[uid]

def check_achievements(uid):
    user = get_user(uid)
    new = []
    if user['work_count'] >= 10 and 'work_10' not in user['achievements']: new.append('work_10')
    if user['work_count'] >= 50 and 'work_50' not in user['achievements']: new.append('work_50')
    if user['work_count'] >= 100 and 'work_100' not in user['achievements']: new.append('work_100')
    if user['work_count'] >= 500 and 'work_500' not in user['achievements']: new.append('work_500')
    if user['slot_wins'] >= 1 and 'win_slot' not in user['achievements']: new.append('win_slot')
    if user['roulette_wins'] >= 1 and 'win_roulette' not in user['achievements']: new.append('win_roulette')
    if user['bet_wins'] >= 1 and 'win_bet' not in user['achievements']: new.append('win_bet')
    if user['money'] >= 1000 and 'money_1000' not in user['achievements']: new.append('money_1000')
    if user['money'] >= 5000 and 'money_5000' not in user['achievements']: new.append('money_5000')
    if user['money'] >= 10000 and 'money_10000' not in user['achievements']: new.append('money_10000')
    if user['money'] >= 50000 and 'money_50000' not in user['achievements']: new.append('money_50000')
    if user['level'] >= 5 and 'level_5' not in user['achievements']: new.append('level_5')
    if user['level'] >= 8 and 'level_8' not in user['achievements']: new.append('level_8')
    if user['level'] >= 10 and 'level_10' not in user['achievements']: new.append('level_10')
    if user['level'] >= 12 and 'level_12' not in user['achievements']: new.append('level_12')
    if user.get('daily_streak', 0) >= 7 and 'daily_streak' not in user['achievements']: new.append('daily_streak')
    if user.get('daily_streak', 0) >= 30 and 'daily_streak_30' not in user['achievements']: new.append('daily_streak_30')
    
    msg = ""
    for ach in new:
        user['achievements'].append(ach)
        user['money'] += ACHIEVEMENTS[ach]['reward']
        user['total_earned'] += ACHIEVEMENTS[ach]['reward']
        msg += f"\n\n🏆 {ACHIEVEMENTS[ach]['name']} +{ACHIEVEMENTS[ach]['reward']}💰"
    if msg:
        save_data(data)
    return msg

def add_exp(uid, amount):
    user = get_user(uid)
    user['exp'] += amount
    user['total_exp'] += amount
    leveled = False
    for lvl in range(user['level'] + 1, 13):
        if user['total_exp'] >= LEVELS[lvl]['exp_needed']:
            user['level'] = lvl
            leveled = True
    save_data(data)
    return leveled

def get_level_info(level):
    return LEVELS.get(level, LEVELS[1])

def get_top():
    top = []
    for uid, u in data.items():
        top.append((u.get('username', 'Игрок'), u['money']))
    top.sort(key=lambda x: x[1], reverse=True)
    return top[:10]

# ========== СОБЫТИЯ В ГОНКЕ ==========
def get_random_event():
    events = [
        {"name": "💥 АВАРИЯ! {} врезался в стену!", "effect": "slow", "value": 1.5},
        {"name": "⛽ ПИТ-СТОП! {} заехал на дозаправку!", "effect": "slow", "value": 1.3},
        {"name": "🚦 ШТРАФ! {} превысил скорость!", "effect": "slow", "value": 1.2},
        {"name": "⚡ РАЗГОН! {} поймал воздушную яму!", "effect": "slow", "value": 1.1},
        {"name": "🔥 НИТРО! {} активировал закись азота!", "effect": "fast", "value": 0.7},
        {"name": "🏎️ ОБГОН! {} совершил крутой маневр!", "effect": "fast", "value": 0.8},
        {"name": "🍀 УДАЧА! {} сократил отставание!", "effect": "fast", "value": 0.85},
        {"name": "💪 РЫВОК! {} прибавил на прямой!", "effect": "fast", "value": 0.75},
    ]
    return random.choice(events)

def race_event_loop(chat_id):
    global race_events
    start_time = time.time()
    last_event = start_time
    
    while race_active:
        now = time.time()
        if now - last_event >= 15:
            if random.randint(1, 100) <= 40:
                car = random.choice(CARS)
                event = get_random_event()
                event_text = event["name"].format(car["name"])
                race_events.append(event_text)
                try:
                    bot.send_message(chat_id, f"🏁 {event_text}")
                except:
                    pass
            last_event = now
        time.sleep(1)

# ========== КОМАНДЫ ==========

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
        f"📝 Напиши 'команды' для списка!")

@bot.message_handler(func=lambda m: m.text and m.text.lower() == 'команды')
def show_commands(message):
    msg = f"📋 СПИСОК КОМАНД 📋\n\n"
    msg += f"--- ИГРЫ ---\n"
    msg += f"• рулетка - игра в рулетку\n"
    msg += f"• слоты - слоты 3x3\n"
    msg += f"• гонка - сделать ставку на гонку\n\n"
    msg += f"--- ЗАРАБОТОК ---\n"
    msg += f"• работа - работа (КД 10 мин)\n"
    msg += f"• бонус - ежедневный (КД 12 ч)\n\n"
    msg += f"--- ИНФО ---\n"
    msg += f"• баланс - проверить деньги\n"
    msg += f"• профиль - статистика\n"
    msg += f"• топ - топ богатых\n"
    msg += f"• достижения - список ачивок\n\n"
    msg += f"--- ПРОМОКОДЫ ---\n"
    msg += f"• #промо шепельпрезидент\n"
    msg += f"• #промо тест\n"
    msg += f"• #промо куниза200шекелей\n"
    msg += f"• #промо ялюблюгрибы\n"
    msg += f"• #промо яустал\n"
    bot.send_message(message.chat.id, msg)

@bot.message_handler(func=lambda m: m.text and m.text.lower() in ['баланс', 'деньги'])
def balance_cmd(message):
    user = get_user(message.from_user.id, message.from_user.username)
    level_info = get_level_info(user['level'])
    bot.send_message(message.chat.id,
        f"💰 БАЛАНС 💰\n\n💵 {user['money']} шекелей\n\n"
        f"📊 Уровень {user['level']} - {level_info['name']}\n"
        f"⭐ Опыт: {user['exp']}\n"
        f"📈 Всего: {user['total_earned']}")

@bot.message_handler(func=lambda m: m.text and m.text.lower() in ['профиль', 'стата'])
def profile_cmd(message):
    user = get_user(message.from_user.id, message.from_user.username)
    level_info = get_level_info(user['level'])
    
    next_lvl = user['level'] + 1
    if next_lvl <= 12:
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
    msg += f"💰 Денег: {user['money']}\n"
    msg += f"⭐ Опыт: {user['exp']}\n"
    msg += f"📈 Всего заработал: {user['total_earned']}\n"
    msg += f"🎁 Серия бонусов: {user.get('daily_streak', 0)}\n"
    msg += f"📦 Работ выполнено: {user.get('work_count', 0)}\n"
    msg += f"🏆 Достижений: {len(user.get('achievements', []))}"
    
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
            msg += f"👑 {i}. @{name} - {money} 💰\n"
        elif i == 2:
            msg += f"🥈 {i}. @{name} - {money} 💰\n"
        elif i == 3:
            msg += f"🥉 {i}. @{name} - {money} 💰\n"
        else:
            msg += f"{i}. @{name} - {money} 💰\n"
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
            m, s = rem // 60, rem % 60
            bot.send_message(message.chat.id, f"⏰ Отдыхай {m} мин {s} сек")
            return
    
    base = random.randint(level_info['salary_min'], level_info['salary_max'])
    fail = random.randint(1, 100) <= 5
    
    if fail:
        penalty = random.randint(int(base * 0.3), int(base * 0.7))
        user['money'] -= penalty
        user['total_earned'] -= penalty
        fail_msgs = FAIL_MESSAGES.get(level_info['name'], ["Ошибка! -{}💰"])
        msg = f"😫 НЕУДАЧА!\n\n💼 {level_info['name']}\n{random.choice(fail_msgs).format(penalty)}\n💵 Баланс: {user['money']}"
    else:
        user['money'] += base
        user['total_earned'] += base
        user['work_count'] += 1
        exp_gain = base // 2
        user['exp'] += exp_gain
        user['total_exp'] += exp_gain
        msg = f"🌾 ТЫ ПОРАБОТАЛ! 🌾\n\n💼 {level_info['name']}\n💰 +{base} шекелей\n⭐ +{exp_gain} опыта\n💵 Баланс: {user['money']}"
        
        leveled = False
        for lvl in range(user['level'] + 1, 13):
            if user['total_exp'] >= LEVELS[lvl]['exp_needed']:
                user['level'] = lvl
                leveled = True
        if leveled:
            msg += f"\n\n🎉 НОВЫЙ УРОВЕНЬ! {user['level']} - {LEVELS[user['level']]['name']}"
    
    user['last_work'] = datetime.now().isoformat()
    save_data(data)
    
    ach = check_achievements(uid)
    if ach:
        msg += ach
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
    
    msg = f"🎁 ЕЖЕДНЕВНЫЙ БОНУС 🎁\n\n💰 +{bonus} шекелей\n⭐ +{bonus//3} опыта\n🔥 Серия: {user['daily_streak']} дней\n💵 Баланс: {user['money']}"
    if leveled:
        msg += f"\n\n🎉 НОВЫЙ УРОВЕНЬ! {user['level']} - {LEVELS[user['level']]['name']}"
    
    ach = check_achievements(uid)
    if ach:
        msg += ach
    save_data(data)
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
        save_data(data)
        msg = f"🎁 ПРОМОКОД АКТИВИРОВАН!\n\n✅ {promo}\n💰 +{p['money']}"
        if p['exp'] > 0:
            leveled = add_exp(uid, p['exp'])
            msg += f"\n⭐ +{p['exp']}"
            if leveled:
                msg += f"\n\n🎉 НОВЫЙ УРОВЕНЬ! {user['level']} - {LEVELS[user['level']]['name']}"
        msg += f"\n💵 Баланс: {user['money']}"
        bot.send_message(message.chat.id, msg)
    else:
        bot.send_message(message.chat.id, f"❌ Промокод {promo} не найден!")

@bot.message_handler(func=lambda m: m.text and m.text.lower() in ['достижения', 'ачивки'])
def achievements_cmd(message):
    user = get_user(message.from_user.id, message.from_user.username)
    completed = user.get('achievements', [])
    
    msg = f"🏆 ДОСТИЖЕНИЯ 🏆\n\n"
    for ach_id, ach in ACHIEVEMENTS.items():
        if ach_id in completed:
            msg += f"✅ {ach['name']} (+{ach['reward']}💰)\n"
        else:
            msg += f"❌ {ach['name']} (+{ach['reward']}💰)\n"
    
    msg += f"\n📊 Получено: {len(completed)}/{len(ACHIEVEMENTS)}"
    bot.send_message(message.chat.id, msg)

# ========== СЕКРЕТНАЯ АЧИВКА ==========
@bot.message_handler(func=lambda m: m.text and all(w in m.text.lower() for w in ['шепель', 'лох', 'нищий', 'бомж']))
def secret_achievement(message):
    uid = message.from_user.id
    user = get_user(uid, message.from_user.username)
    
    if 'secret' in user.get('achievements', []):
        bot.send_message(message.chat.id, "❌ Ты уже получил секретную награду!")
        return
    
    user['achievements'].append('secret')
    user['money'] += 5555
    user['total_earned'] += 5555
    add_exp(uid, 555)
    save_data(data)
    bot.send_message(message.chat.id, f"🔓 СЕКРЕТНАЯ АЧИВКА!\n\n🏆 ШЕПЕЛЬФЕСТ\n💰 +5555💰\n⭐ +555⭐\n💵 Баланс: {user['money']}")

# ========== СЛОТЫ ==========
SLOT_SYMBOLS = ['🍒', '🍊', '🍋', '🍉', '🍇', '💰', '💎', '🎰', '7️⃣']
SLOT_PAYOUTS = {
    ('7️⃣', '7️⃣', '7️⃣'): 50, ('🎰', '🎰', '🎰'): 40, ('💎', '💎', '💎'): 30,
    ('💰', '💰', '💰'): 25, ('🍇', '🍇', '🍇'): 20, ('🍉', '🍉', '🍉'): 15,
    ('🍒', '🍒', '🍒'): 10, ('🍊', '🍊', '🍊'): 10, ('🍋', '🍋', '🍋'): 10,
}

@bot.message_handler(func=lambda m: m.text and m.text.lower() in ['слоты', 'слот', 'казик'])
def slots_start(message):
    slot_waiting[message.from_user.id] = 'waiting_bet'
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
    save_data(data)
    
    msg = bot.send_message(message.chat.id, "🎰 КРУТИМ... 🎰\n\n🌀 | 🌀 | 🌀")
    time.sleep(0.5)
    
    for _ in range(3):
        spin = [random.choice(SLOT_SYMBOLS) for _ in range(3)]
        bot.edit_message_text(f"🎰 КРУТИМ... 🎰\n\n{spin[0]} | {spin[1]} | {spin[2]}", message.chat.id, msg.message_id)
        time.sleep(0.4)
    
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
        user['slot_wins'] += 1
        add_exp(uid, win // 4)
        save_data(data)
    
    msg_text = f"🎰 РЕЗУЛЬТАТ 🎰\n\n"
    msg_text += f"┌───┬───┬───┐\n│ {result[0]} │ {result[1]} │ {result[2]} │\n└───┴───┴───┘\n\n"
    msg_text += f"{win_type}\n"
    if win > 0:
        msg_text += f"💰 +{win} шекелей!\n"
    msg_text += f"💵 Баланс: {user['money']}"
    
    ach = check_achievements(uid)
    if ach:
        msg_text += ach
    
    bot.edit_message_text(msg_text, message.chat.id, msg.message_id)
    del slot_waiting[uid]

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
    save_data(data)
    
    num = random.randint(0, 36)
    if num == 0:
        color, emoji = 'green', '🟢'
    elif num in [1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36]:
        color, emoji = 'red', '🔴'
    else:
        color, emoji = 'black', '⚫'
    
    win = 0
    if bet_type == 'red' and color == 'red': win = bet * 2
    elif bet_type == 'black' and color == 'black': win = bet * 2
    elif bet_type == 'green' and num == 0: win = bet * 35
    elif bet_type == 'even' and num > 0 and num % 2 == 0: win = bet * 2
    elif bet_type == 'odd' and num > 0 and num % 2 == 1: win = bet * 2
    
    names = {'red':'КРАСНОЕ', 'black':'ЧЕРНОЕ', 'green':'ЗЕЛЕНЫЙ', 'even':'ЧЕТ', 'odd':'НЕЧЕТ'}
    
    if win > 0:
        user['money'] += win
        user['total_earned'] += win
        user['roulette_wins'] += 1
        add_exp(uid, win // 4)
        msg = f"🎡 РУЛЕТКА 🎡\n\n🎲 {emoji} {num}\n🎯 {names[bet_type]} {bet}\n💰 ВЫИГРЫШ: +{win}\n💵 Баланс: {user['money']}"
    else:
        msg = f"🎡 РУЛЕТКА 🎡\n\n🎲 {emoji} {num}\n🎯 {names[bet_type]} {bet}\n💔 ПРОИГРЫШ\n💵 Баланс: {user['money']}"
    
    save_data(data)
    ach = check_achievements(uid)
    if ach:
        msg += ach
    bot.send_message(message.chat.id, msg)
    del roulette_waiting[uid]

# ========== ГОНКИ (СТАВКИ) ==========

def start_race(chat_id):
    global race_active, race_bets, race_events, race_start_time
    time.sleep(60)
    
    if not race_active:
        return
    
    # Итоги гонки
    total_chance = sum(c['chance'] for c in CARS)
    roll = random.randint(1, total_chance)
    cum = 0
    winner = None
    for car in CARS:
        cum += car['chance']
        if roll <= cum:
            winner = car
            break
    
    # Формируем результаты
    results = f"🏁 ГОНКА ЗАВЕРШЕНА! 🏁\n\n"
    results += f"🥇 ПОБЕДИТЕЛЬ: {winner['emoji']} {winner['name']} (коэф. x{winner['coefficient']})\n\n"
    
    if race_events:
        results += f"📋 СОБЫТИЯ ГОНКИ:\n"
        for event in race_events[-5:]:  # последние 5 событий
            results += f"• {event}\n"
        results += f"\n"
    
    winners_list = []
    for car_name, bet_data in race_bets.items():
        if car_name == winner['name']:
            for bet in bet_data['bets']:
                uid = bet['uid']
                amount = bet['amount']
                user = get_user(uid)
                win_amount = int(amount * winner['coefficient'])
                user['money'] += win_amount
                user['total_earned'] += win_amount
                user['bet_wins'] += 1
                add_exp(uid, win_amount // 4)
                winners_list.append(f"✅ @{user['username']} +{win_amount}💰")
    
    if winners_list:
        results += "💰 ВЫИГРЫШИ:\n" + "\n".join(winners_list)
    else:
        results += "💔 НЕТ ВЫИГРЫШЕЙ"
    
    # Рассылаем
    for car_name, bet_data in race_bets.items():
        try:
            bot.send_message(bet_data['chat_id'], results)
        except:
            pass
    
    # Сбрасываем
    race_active = False
    race_bets = {}
    race_events = []
    save_data(data)

def race_event_loop(chat_id):
    global race_events, race_active
    last_event = time.time()
    
    while race_active:
        now = time.time()
        if now - last_event >= 15:
            if random.randint(1, 100) <= 40:
                car = random.choice(CARS)
                events = [
                    f"💥 {car['name']} врезался в стену!",
                    f"⛽ {car['name']} заехал на пит-стоп!",
                    f"🚦 {car['name']} получил штраф!",
                    f"⚡ {car['name']} поймал воздушную яму!",
                    f"🔥 {car['name']} активировал нитро!",
                    f"🏎️ {car['name']} совершил обгон!",
                    f"🍀 {car['name']} повезло на трассе!",
                    f"💪 {car['name']} прибавил на прямой!",
                ]
                event_text = random.choice(events)
                race_events.append(event_text)
                try:
                    bot.send_message(chat_id, f"🏁 {event_text}")
                except:
                    pass
            last_event = now
        time.sleep(1)

@bot.message_handler(func=lambda m: m.text and m.text.lower() in ['гонка', 'ставка', 'ставки'])
def race_bet_menu(message):
    global race_active, race_bets, race_start_time, race_events
    uid = message.from_user.id
    user = get_user(uid, message.from_user.username)
    
    if race_active:
        # Показываем меню ставок
        kb = telebot.types.InlineKeyboardMarkup(row_width=2)
        for car in CARS:
            kb.add(telebot.types.InlineKeyboardButton(f"{car['emoji']} {car['name']} x{car['coefficient']}", callback_data=f'race_{car["name"]}'))
        bot.send_message(message.chat.id, "🏁 СТАВКИ НА ГОНКУ 🏁\n\nВыбери машину:", reply_markup=kb)
        return
    
    # Начинаем новую гонку
    race_active = True
    race_bets = {}
    race_events = []
    race_start_time = time.time()
    
    # Запускаем таймер
    timer_thread = threading.Thread(target=start_race, args=(message.chat.id,), daemon=True)
    timer_thread.start()
    
    # Запускаем события
    event_thread = threading.Thread(target=race_event_loop, args=(message.chat.id,), daemon=True)
    event_thread.start()
    
    msg = "🏁 НОВАЯ ГОНКА НАЧАЛАСЬ! 🏁\n\n"
    msg += "⏰ 1 минута на ставки!\n\n"
    msg += "🏎️ МАШИНЫ И КОЭФФИЦИЕНТЫ:\n"
    for car in CARS:
        msg += f"{car['emoji']} {car['name']} - x{car['coefficient']} (шанс {car['chance']}%)\n"
    
    msg += f"\n⏳ Гонка начнется через 60 секунд!\n"
    msg += f"📝 Делай ставку командой 'гонка'"
    
    bot.send_message(message.chat.id, msg)

@bot.callback_query_handler(func=lambda call: call.data.startswith('race_'))
def race_choose_car(call):
    uid = call.from_user.id
    car_name = call.data.split('_')[1]
    
    car = None
    for c in CARS:
        if c['name'] == car_name:
            car = c
            break
    
    if not car:
        bot.answer_callback_query(call.id, "❌ Машина не найдена!", show_alert=True)
        return
    
    bot.edit_message_text(f"🏁 СТАВКА НА {car['emoji']} {car['name']} 🏁\n\n💰 Введи сумму ставки (мин 10):", 
                          call.message.chat.id, call.message.message_id)
    bot.answer_callback_query(call.id)
    
    slot_waiting[uid] = f'race_bet_{car["name"]}'

@bot.message_handler(func=lambda m: m.from_user.id in slot_waiting and slot_waiting[m.from_user.id].startswith('race_bet_'))
def race_get_bet(message):
    uid = message.from_user.id
    car_name = slot_waiting[uid].replace('race_bet_', '')
    
    try:
        amount = int(message.text.strip())
        if amount < 10:
            bot.send_message(message.chat.id, "❌ Минимальная ставка 10 шекелей!")
            return
    except:
        bot.send_message(message.chat.id, "❌ Введи число!")
        return
    
    user = get_user(uid, message.from_user.username)
    if user['money'] < amount:
        bot.send_message(message.chat.id, f"❌ Не хватает {amount} шекелей!")
        del slot_waiting[uid]
        return
    
    if not race_active:
        bot.send_message(message.chat.id, "❌ Гонка уже началась! Жди следующей!")
        del slot_waiting[uid]
        return
    
    user['money'] -= amount
    save_data(data)
    
    if car_name not in race_bets:
        race_bets[car_name] = {'bets': [], 'chat_id': message.chat.id}
    race_bets[car_name]['bets'].append({'uid': uid, 'amount': amount})
    
    car = next((c for c in CARS if c['name'] == car_name), None)
    
    bot.send_message(message.chat.id, 
        f"✅ СТАВКА ПРИНЯТА!\n\n"
        f"🏎️ {car['emoji']} {car_name}\n"
        f"💰 Сумма: {amount} шекелей\n"
        f"📊 Коэффициент: x{car['coefficient']}\n"
        f"💵 Ваш баланс: {user['money']}")
    
    del slot_waiting[uid]

# ========== ЗАПУСК ==========
print("=" * 50)
print("ХИТРЫЙ ЕВРЕЙ БОТ ЗАПУЩЕН!")
print("12 УРОВНЕЙ ПРОФЕССИЙ!")
print("НОВЫЙ ПРОМОКОД: #промо яустал (228💰)")
print("Слоты - работают")
print("Рулетка - работает")
print("Гонки - работают")
print("Сохранения - железобетонные")
print("=" * 50)

bot.infinity_polling()
