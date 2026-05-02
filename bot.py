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
    'bet_wins': 0, 'coin_wins': 0, 'achievements': []
}

# ========== ПРОФЕССИИ (12 УРОВНЕЙ) ==========
LEVELS = {
    1: {"name": "Грузчик", "salary_min": 5, "salary_max": 50, "exp_needed": 0},
    2: {"name": "Курьер", "salary_min": 15, "salary_max": 80, "exp_needed": 100},
    3: {"name": "Автомеханик", "salary_min": 30, "salary_max": 120, "exp_needed": 250},
    4: {"name": "Кладовщик", "salary_min": 50, "salary_max": 160, "exp_needed": 450},
    5: {"name": "Доставщик", "salary_min": 70, "salary_max": 200, "exp_needed": 700},
    6: {"name": "Сварщик", "salary_min": 90, "salary_max": 240, "exp_needed": 1000},
    7: {"name": "Менеджер", "salary_min": 120, "salary_max": 280, "exp_needed": 1400},
    8: {"name": "Бухгалтер", "salary_min": 150, "salary_max": 320, "exp_needed": 1900},
    9: {"name": "Прораб", "salary_min": 180, "salary_max": 360, "exp_needed": 2500},
    10: {"name": "Директор", "salary_min": 220, "salary_max": 420, "exp_needed": 3200},
    11: {"name": "Бизнесмен", "salary_min": 260, "salary_max": 480, "exp_needed": 4000},
    12: {"name": "Магнат", "salary_min": 300, "salary_max": 600, "exp_needed": 5000},
}

ACHIEVEMENTS = {
    'work_10': {'name': "Трудоголик", 'reward': 100},
    'work_50': {'name': "Стахановец", 'reward': 500},
    'work_100': {'name': "Машина", 'reward': 1000},
    'work_500': {'name': "Терминатор", 'reward': 5000},
    'win_slot': {'name': "Счастливчик", 'reward': 50},
    'win_roulette': {'name': "Фортуна", 'reward': 50},
    'win_bet': {'name': "Лучший каппер", 'reward': 100},
    'win_coin': {'name': "Орлянщик", 'reward': 50},
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

# ========== ЛОШАДИ ДЛЯ СТАВОК ==========
HORSES = [
    {"name": "🐎 МОЛНИЯ", "emoji": "🐎", "coefficient": 6.0, "chance": 10},
    {"name": "🐎 ВЕТЕР", "emoji": "🐎", "coefficient": 4.0, "chance": 15},
    {"name": "🐎 ГРОМ", "emoji": "🐎", "coefficient": 3.0, "chance": 20},
    {"name": "🐎 МОЛОТ", "emoji": "🐎", "coefficient": 2.5, "chance": 25},
    {"name": "🐎 СТРЕЛА", "emoji": "🐎", "coefficient": 2.0, "chance": 30},
    {"name": "🐎 ТИХОНЯ", "emoji": "🐎", "coefficient": 10.0, "chance": 5},
]

# ========== ПЕРЕМЕННЫЕ ==========
slot_waiting = {}
roulette_waiting = {}
coin_waiting = {}
horse_race_active = False
horse_race_bets = {}
horse_race_events = []
horse_race_start_time = None

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
    if user['coin_wins'] >= 1 and 'win_coin' not in user['achievements']: new.append('win_coin')
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
    msg += f"• орел / решка - игра с монеткой\n"
    msg += f"• скачки - сделать ставку на скачки\n\n"
    msg += f"--- ЗАРАБОТОК ---\n"
    msg += f"• работа - работа (КД 10 мин)\n"
    msg += f"• бонус - ежедневный (КД 12 ч)\n\n"
    msg += f"--- ИНФО ---\n"
    msg += f"• баланс - проверить деньги\n"
    msg += f"• профиль - статистика\n"
    msg += f"• топ - топ богатых\n"
    msg += f"• достижения - список ачивок\n\n"
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

# ========== ОРЁЛ/РЕШКА ==========

@bot.message_handler(func=lambda m: m.text and m.text.lower() in ['орел', 'решка', 'орел/решка', 'монетка'])
def coin_game(message):
    uid = message.from_user.id
    coin_waiting[uid] = 'waiting_bet'
    bot.send_message(message.chat.id, "🪙 ОРЁЛ/РЕШКА 🪙\n\n💰 Введи сумму ставки (мин 10):")

@bot.message_handler(func=lambda m: m.from_user.id in coin_waiting and coin_waiting[m.from_user.id] == 'waiting_bet')
def coin_get_bet(message):
    uid = message.from_user.id
    try:
        bet = int(message.text.strip())
        if bet < 10:
            bot.send_message(message.chat.id, "❌ Минимальная ставка 10 шекелей!")
            return
    except:
        bot.send_message(message.chat.id, "❌ Введи число!")
        del coin_waiting[uid]
        return
    
    user = get_user(uid, message.from_user.username)
    if user['money'] < bet:
        bot.send_message(message.chat.id, f"❌ Не хватает {bet} шекелей!")
        del coin_waiting[uid]
        return
    
    coin_waiting[uid] = bet

@bot.message_handler(func=lambda m: m.from_user.id in coin_waiting and isinstance(coin_waiting[m.from_user.id], int))
def coin_choose(message):
    uid = message.from_user.id
    bet = coin_waiting[uid]
    choice = message.text.lower()
    
    if choice not in ['орел', 'решка']:
        bot.send_message(message.chat.id, "❌ Выбери 'орел' или 'решка'!")
        return
    
    # Подбрасываем монетку
    result = random.choice(['орел', 'решка'])
    win = 0
    
    if choice == result:
        win = bet * 2
        user = get_user(uid, message.from_user.username)
        user['money'] += win
        user['total_earned'] += win
        user['coin_wins'] += 1
        add_exp(uid, win // 4)
        save_data(data)
        msg = f"🪙 ОРЁЛ/РЕШКА 🪙\n\n"
        msg += f"🎲 Ты выбрал: {choice.upper()}\n"
        msg += f"🎲 Выпало: {result.upper()}\n"
        msg += f"✨ ПОБЕДА! +{win} шекелей ✨\n"
        msg += f"💵 Баланс: {user['money']}"
        
        ach = check_achievements(uid)
        if ach:
            msg += ach
    else:
        user = get_user(uid, message.from_user.username)
        user['money'] -= bet
        user['total_earned'] -= bet
        save_data(data)
        msg = f"🪙 ОРЁЛ/РЕШКА 🪙\n\n"
        msg += f"🎲 Ты выбрал: {choice.upper()}\n"
        msg += f"🎲 Выпало: {result.upper()}\n"
        msg += f"💔 ПРОИГРЫШ! -{bet} шекелей 💔\n"
        msg += f"💵 Баланс: {user['money']}"
    
    bot.send_message(message.chat.id, msg)
    del coin_waiting[uid]

# ========== СКАЧКИ ==========

def start_horse_race(chat_id):
    global horse_race_active, horse_race_bets, horse_race_events
    time.sleep(60)
    
    if not horse_race_active:
        return
    
    total_chance = sum(h['chance'] for h in HORSES)
    roll = random.randint(1, total_chance)
    cum = 0
    winner = None
    for horse in HORSES:
        cum += horse['chance']
        if roll <= cum:
            winner = horse
            break
    
    results = f"🏁 СКАЧКИ ЗАВЕРШЕНЫ! 🏁\n\n"
    results += f"🥇 ПОБЕДИТЕЛЬ: {winner['emoji']} {winner['name']} (коэф. x{winner['coefficient']})\n\n"
    
    if horse_race_events:
        results += f"📋 СОБЫТИЯ СКАЧЕК:\n"
        for event in horse_race_events[-5:]:
            results += f"• {event}\n"
        results += f"\n"
    
    winners_list = []
    for horse_name, bet_data in horse_race_bets.items():
        if horse_name == winner['name']:
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
    
    for horse_name, bet_data in horse_race_bets.items():
        try:
            bot.send_message(bet_data['chat_id'], results)
        except:
            pass
    
    horse_race_active = False
    horse_race_bets = {}
    horse_race_events = []
    save_data(data)

def horse_race_event_loop(chat_id):
    global horse_race_events, horse_race_active
    last_event = time.time()
    
    while horse_race_active:
        now = time.time()
        if now - last_event >= 15:
            if random.randint(1, 100) <= 40:
                horse = random.choice(HORSES)
                events = [
                    f"💥 {horse['name']} споткнулся!",
                    f"🏇 {horse['name']} ускорился!",
                    f"🐎 {horse['name']} обошел соперника!",
                    f"⚡ {horse['name']} набрал скорость!",
                    f"💪 {horse['name']} делает рывок!",
                    f"🍀 {horse['name']} повезло на финише!",
                ]
                event_text = random.choice(events)
                horse_race_events.append(event_text)
                try:
                    bot.send_message(chat_id, f"🏁 {event_text}")
                except:
                    pass
            last_event = now
        time.sleep(1)

@bot.message_handler(func=lambda m: m.text and m.text.lower() in ['скачки', 'ставка', 'тотализатор'])
def horse_race_bet_menu(message):
    global horse_race_active, horse_race_bets, horse_race_events
    
    if horse_race_active:
        kb = telebot.types.InlineKeyboardMarkup(row_width=2)
        for horse in HORSES:
            kb.add(telebot.types.InlineKeyboardButton(f"{horse['emoji']} {horse['name']} x{horse['coefficient']}", callback_data=f'hrace_{horse["name"]}'))
        bot.send_message(message.chat.id, "🏁 СТАВКИ НА СКАЧКИ 🏁\n\nВыбери лошадь:", reply_markup=kb)
        return
    
    horse_race_active = True
    horse_race_bets = {}
    horse_race_events = []
    
    timer_thread = threading.Thread(target=start_horse_race, args=(message.chat.id,), daemon=True)
    timer_thread.start()
    
    event_thread = threading.Thread(target=horse_race_event_loop, args=(message.chat.id,), daemon=True)
    event_thread.start()
    
    msg = "🏁 НОВЫЕ СКАЧКИ НАЧАЛИСЬ! 🏁\n\n"
    msg += "⏰ 1 минута на ставки!\n\n"
    msg += "🐎 УЧАСТНИКИ И КОЭФФИЦИЕНТЫ:\n"
    for horse in HORSES:
        msg += f"{horse['emoji']} {horse['name']} - x{horse['coefficient']} (шанс {horse['chance']}%)\n"
    
    msg += f"\n⏳ Скачки начнутся через 60 секунд!\n"
    msg += f"📝 Делай ставку командой 'скачки'"
    
    bot.send_message(message.chat.id, msg)

@bot.callback_query_handler(func=lambda call: call.data.startswith('hrace_'))
def horse_race_choose(call):
    uid = call.from_user.id
    horse_name = call.data.split('_')[1]
    
    horse = None
    for h in HORSES:
        if h['name'] == horse_name:
            horse = h
            break
    
    if not horse:
        bot.answer_callback_query(call.id, "❌ Лошадь не найдена!", show_alert=True)
        return
    
    bot.edit_message_text(f"🏁 СТАВКА НА {horse['emoji']} {horse['name']} 🏁\n\n💰 Введи сумму ставки (мин 10):", 
                          call.message.chat.id, call.message.message_id)
    bot.answer_callback_query(call.id)
    
    slot_waiting[uid] = f'hrace_bet_{horse["name"]}'

@bot.message_handler(func=lambda m: m.from_user.id in slot_waiting and slot_waiting[m.from_user.id].startswith('hrace_bet_'))
def horse_race_get_bet(message):
    uid = message.from_user.id
    horse_name = slot_waiting[uid].replace('hrace_bet_', '')
    
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
    
    if not horse_race_active:
        bot.send_message(message.chat.id, "❌ Скачки уже начались! Жди следующих!")
        del slot_waiting[uid]
        return
    
    user['money'] -= amount
    save_data(data)
    
    if horse_name not in horse_race_bets:
        horse_race_bets[horse_name] = {'bets': [], 'chat_id': message.chat.id}
    horse_race_bets[horse_name]['bets'].append({'uid': uid, 'amount': amount})
    
    horse = next((h for h in HORSES if h['name'] == horse_name), None)
    
    bot.send_message(message.chat.id, 
        f"✅ СТАВКА ПРИНЯТА!\n\n"
        f"🐎 {horse['emoji']} {horse_name}\n"
        f"💰 Сумма: {amount} шекелей\n"
        f"📊 Коэффициент: x{horse['coefficient']}\n"
        f"💵 Ваш баланс: {user['money']}")
    
    del slot_waiting[uid]

# ========== ЗАПУСК ==========
print("=" * 50)
print("ХИТРЫЙ ЕВРЕЙ БОТ ЗАПУЩЕН!")
print("12 УРОВНЕЙ ПРОФЕССИЙ!")
print("ОРЁЛ/РЕШКА - работает!")
print("СКАЧКИ - работают!")
print("Слоты - работают")
print("Рулетка - работает")
print("Сохранения - железобетонные")
print("=" * 50)

bot.infinity_polling()
