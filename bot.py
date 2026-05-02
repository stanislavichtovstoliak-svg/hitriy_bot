import telebot
import random
import json
import os
from datetime import datetime
import time

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
            print("Ошибка загрузки, создаю новый файл")
            return {}
    return {}

def save_data(data):
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except:
        print("Ошибка сохранения")
        return False

data = load_data()

# ========== ДАННЫЕ ПО УМОЛЧАНИЮ ==========
DEFAULT_USER = {
    'money': 500,
    'level': 1,
    'exp': 0,
    'total_exp': 0,
    'last_work': None,
    'username': None,
    'total_earned': 0,
    'last_daily': None,
    'daily_streak': 0,
    'promos': [],
    'work_count': 0,
    'slot_wins': 0,
    'bj_wins': 0,
    'roulette_wins': 0,
    'achievements': [],
    'today_transfer': 0
}

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

ACHIEVEMENTS = {
    'work_10': {'name': "Трудоголик", 'desc': "10 работ", 'reward': 100},
    'work_50': {'name': "Стахановец", 'desc': "50 работ", 'reward': 500},
    'work_100': {'name': "Машина", 'desc': "100 работ", 'reward': 1000},
    'win_slot': {'name': "Счастливчик", 'desc': "Выиграть в слотах", 'reward': 50},
    'win_bj': {'name': "Картежник", 'desc': "Выиграть в блекджек", 'reward': 50},
    'win_roulette': {'name': "Фортуна", 'desc': "Выиграть в рулетку", 'reward': 50},
    'money_1000': {'name': "Тысячник", 'desc': "1000💰", 'reward': 200},
    'money_5000': {'name': "Богач", 'desc': "5000💰", 'reward': 700},
    'money_10000': {'name': "Магнат", 'desc': "10000💰", 'reward': 1500},
    'level_5': {'name': "Профи", 'desc': "5 уровень", 'reward': 300},
    'level_8': {'name': "Легенда", 'desc': "8 уровень", 'reward': 1000},
    'daily_streak': {'name': "Серийный", 'desc': "7 дней бонуса", 'reward': 500},
}

FORTUNE_REWARDS = [
    {"name": "50💰", "money": 50, "exp": 0, "prob": 25},
    {"name": "100💰", "money": 100, "exp": 0, "prob": 20},
    {"name": "200💰", "money": 200, "exp": 0, "prob": 15},
    {"name": "500💰", "money": 500, "exp": 0, "prob": 8},
    {"name": "1000💰 ДЖЕКПОТ!", "money": 1000, "exp": 0, "prob": 2},
    {"name": "50⭐", "money": 0, "exp": 50, "prob": 15},
    {"name": "100⭐", "money": 0, "exp": 100, "prob": 10},
    {"name": "200⭐", "money": 0, "exp": 200, "prob": 5},
]

PROMOCODES = {
    'шепельпрезидент': {'money': 2000, 'exp': 200},
    'тест': {'money': 2, 'exp': 0},
    'куниза200шекелей': {'money': 199, 'exp': 0},
    'ялюблюгрибы': {'money': 666, 'exp': 0},
}

FAIL_MESSAGES = {
    "Грузчик": ["Уронил ящик! -{}💰", "Разбил вазу! -{}💰"],
    "Курьер": ["Проткнул колесо! -{}💰", "Потерял посылку! -{}💰"],
    "Автомеханик": ["Сорвал резьбу! -{}💰", "Забыл затянуть колесо! -{}💰"],
    "Кладовщик": ["Перепутал товар! -{}💰", "Потерял накладную! -{}💰"],
    "Менеджер": ["Поссорился с клиентом! -{}💰", "Провалил презентацию! -{}💰"],
    "Бухгалтер": ["Ошибся в отчетности! -{}💰", "Потерял чеки! -{}💰"],
    "Директор": ["Неудачная сделка! -{}💰", "Акции упали! -{}💰"],
    "Магнат": ["Крипта провалилась! -{}💰", "Завод встал! -{}💰"]
}

# ========== ФУНКЦИИ ==========

def get_user(user_id, username=None):
    uid = str(user_id)
    if uid not in data:
        data[uid] = DEFAULT_USER.copy()
        data[uid]['username'] = username
        save_data(data)
        print(f"🆕 Новый игрок: @{username}")
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
    if user['slot_wins'] >= 1 and 'win_slot' not in user['achievements']: new.append('win_slot')
    if user['bj_wins'] >= 1 and 'win_bj' not in user['achievements']: new.append('win_bj')
    if user['roulette_wins'] >= 1 and 'win_roulette' not in user['achievements']: new.append('win_roulette')
    if user['money'] >= 1000 and 'money_1000' not in user['achievements']: new.append('money_1000')
    if user['money'] >= 5000 and 'money_5000' not in user['achievements']: new.append('money_5000')
    if user['money'] >= 10000 and 'money_10000' not in user['achievements']: new.append('money_10000')
    if user['level'] >= 5 and 'level_5' not in user['achievements']: new.append('level_5')
    if user['level'] >= 8 and 'level_8' not in user['achievements']: new.append('level_8')
    if user.get('daily_streak', 0) >= 7 and 'daily_streak' not in user['achievements']: new.append('daily_streak')
    
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
    for lvl in range(user['level'] + 1, 9):
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

def get_bot_stats():
    return len(data), sum(u['money'] for u in data.values()), sum(u.get('total_earned', 0) for u in data.values()), max((u.get('level', 1) for u in data.values()), default=1)

# ========== ПЕРЕМЕННЫЕ ДЛЯ ИГР ==========
slot_waiting = {}
bj_games = {}
roulette_waiting = {}
fortune_cooldown = {}
daily_transfer = {}

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
        f"📝 Напиши 'команды' для списка!\n\n"
        f"🎲 Удачи!")

@bot.message_handler(func=lambda m: m.text and m.text.lower() == 'команды')
def show_commands(message):
    msg = f"📋 СПИСОК КОМАНД 📋\n\n"
    msg += f"--- ИГРЫ ---\n"
    msg += f"• рулетка - игра в рулетку\n"
    msg += f"• слоты - слоты 3x3\n"
    msg += f"• блекджек - игра в 21\n"
    msg += f"• колесо - халява раз в час\n\n"
    msg += f"--- ЗАРАБОТОК ---\n"
    msg += f"• работа - работа (КД 10 мин)\n"
    msg += f"• бонус - ежедневный (КД 12 ч)\n\n"
    msg += f"--- ИНФО ---\n"
    msg += f"• баланс - проверить деньги\n"
    msg += f"• профиль - статистика\n"
    msg += f"• топ - топ богатых\n"
    msg += f"• достижения - список ачивок\n"
    msg += f"• стата - статистика бота\n\n"
    msg += f"--- ПЕРЕВОДЫ ---\n"
    msg += f"• дать [сумма] - ответом на сообщение\n\n"
    msg += f"--- ПРОМОКОДЫ ---\n"
    msg += f"• #промо код"
    bot.send_message(message.chat.id, msg)

@bot.message_handler(func=lambda m: m.text and m.text.lower() in ['баланс', 'деньги'])
def balance_cmd(message):
    user = get_user(message.from_user.id, message.from_user.username)
    level_info = get_level_info(user['level'])
    bot.send_message(message.chat.id,
        f"💰 БАЛАНС 💰\n\n"
        f"💵 {user['money']} шекелей\n\n"
        f"📊 Уровень {user['level']} - {level_info['name']}\n"
        f"⭐ Опыт: {user['exp']}\n"
        f"📈 Всего: {user['total_earned']}")

@bot.message_handler(func=lambda m: m.text and m.text.lower() in ['профиль', 'стата'])
def profile_cmd(message):
    uid = message.from_user.id
    user = get_user(uid, message.from_user.username)
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
        msg = f"😫 НЕУДАЧА!\n\n💼 {level_info['name']}\n{random.choice(FAIL_MESSAGES[level_info['name']]).format(penalty)}\n💵 Баланс: {user['money']}"
    else:
        user['money'] += base
        user['total_earned'] += base
        user['work_count'] += 1
        exp_gain = base // 2
        user['exp'] += exp_gain
        user['total_exp'] += exp_gain
        msg = f"🌾 ТЫ ПОРАБОТАЛ! 🌾\n\n💼 {level_info['name']}\n💰 +{base} шекелей\n⭐ +{exp_gain} опыта\n💵 Баланс: {user['money']}"
        
        leveled = False
        for lvl in range(user['level'] + 1, 9):
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
            msg += f"✅ {ach['name']} - {ach['desc']} (+{ach['reward']}💰)\n"
        else:
            msg += f"❌ {ach['name']} - {ach['desc']} (+{ach['reward']}💰)\n"
    
    msg += f"\n📊 Получено: {len(completed)}/{len(ACHIEVEMENTS)}"
    bot.send_message(message.chat.id, msg)

@bot.message_handler(func=lambda m: m.text and m.text.lower() in ['стата', 'статистика', 'статистика бота'])
def stats_cmd(message):
    total_users, total_money, total_earned, top_level = get_bot_stats()
    
    msg = f"📊 СТАТИСТИКА БОТА 📊\n\n"
    msg += f"👥 Всего игроков: {total_users}\n"
    msg += f"💰 Всего денег: {total_money}\n"
    msg += f"💵 Всего заработано: {total_earned}\n"
    msg += f"🏆 Максимальный уровень: {top_level}"
    bot.send_message(message.chat.id, msg)

# ========== ПЕРЕВОД ДЕНЕГ ==========

@bot.message_handler(func=lambda m: m.text and m.text.lower().startswith('дать') and m.reply_to_message)
def transfer_money(message):
    uid = message.from_user.id
    user = get_user(uid, message.from_user.username)
    target_uid = message.reply_to_message.from_user.id
    target_user = get_user(target_uid, message.reply_to_message.from_user.username)
    
    if str(target_uid) == str(uid):
        bot.send_message(message.chat.id, "❌ Нельзя дать деньги самому себе!")
        return
    
    parts = message.text.split()
    if len(parts) < 2:
        bot.send_message(message.chat.id, "❌ Укажи сумму! Пример: дать 500")
        return
    
    try:
        amount = int(parts[1])
        if amount <= 0:
            bot.send_message(message.chat.id, "❌ Сумма должна быть положительной!")
            return
    except:
        bot.send_message(message.chat.id, "❌ Введи число!")
        return
    
    if user['money'] < amount:
        bot.send_message(message.chat.id, f"❌ У тебя только {user['money']} шекелей!")
        return
    
    today = datetime.now().strftime('%Y%m%d')
    key = f"{uid}_{today}"
    if key not in daily_transfer:
        daily_transfer[key] = 0
    
    if daily_transfer[key] + amount > 10000:
        remaining = 10000 - daily_transfer[key]
        bot.send_message(message.chat.id, f"❌ Лимит 10000💰/день! Осталось: {remaining}")
        return
    
    user['money'] -= amount
    target_user['money'] += amount
    daily_transfer[key] += amount
    save_data(data)
    
    bot.send_message(message.chat.id, 
        f"💸 ПЕРЕВОД 💸\n\n"
        f"👤 @{message.from_user.username} → @{message.reply_to_message.from_user.username}\n"
        f"💰 Сумма: {amount} шекелей\n"
        f"💵 Ваш баланс: {user['money']}")

# ========== КОЛЕСО ФОРТУНЫ ==========

@bot.message_handler(func=lambda m: m.text and m.text.lower() in ['колесо', 'фортуна', 'колесо фортуны'])
def fortune_cmd(message):
    uid = message.from_user.id
    user = get_user(uid, message.from_user.username)
    now = time.time()
    
    if uid in fortune_cooldown:
        last = fortune_cooldown[uid]
        if now - last < 3600:
            left = int(3600 - (now - last))
            h, m = left // 3600, (left % 3600) // 60
            bot.send_message(message.chat.id, f"🎡 Колесо Фортуны доступно через {h}ч {m}мин!")
            return
    
    total_prob = sum(r['prob'] for r in FORTUNE_REWARDS)
    roll = random.randint(1, total_prob)
    cum = 0
    reward = None
    for r in FORTUNE_REWARDS:
        cum += r['prob']
        if roll <= cum:
            reward = r
            break
    
    if reward['money'] > 0:
        user['money'] += reward['money']
        user['total_earned'] += reward['money']
        msg = f"🎡 КОЛЕСО ФОРТУНЫ 🎡\n\n💰 Выпало: {reward['name']}!\n💵 Баланс: {user['money']}"
    elif reward['exp'] > 0:
        leveled = add_exp(uid, reward['exp'])
        msg = f"🎡 КОЛЕСО ФОРТУНЫ 🎡\n\n⭐ Выпало: {reward['name']}!"
        if leveled:
            msg += f"\n\n🎉 НОВЫЙ УРОВЕНЬ! {user['level']} - {LEVELS[user['level']]['name']}"
    else:
        msg = f"🎡 КОЛЕСО ФОРТУНЫ 🎡\n\n{reward['name']}!"
    
    fortune_cooldown[uid] = now
    save_data(data)
    bot.send_message(message.chat.id, msg)

# ========== СЕКРЕТНАЯ АЧИВКА ==========

@bot.message_handler(func=lambda m: m.text and all(w in m.text.lower() for w in ['шепель', 'лох', 'нищий', 'бомж']))
def secret_achievement(message):
    uid = message.from_user.id
    user = get_user(uid, message.from_user.username)
    
    if 'secret_insult' in user.get('achievements', []):
        bot.send_message(message.chat.id, "❌ Ты уже получил эту секретную награду!")
        return
    
    user['achievements'].append('secret_insult')
    user['money'] += 5555
    user['total_earned'] += 5555
    add_exp(uid, 555)
    save_data(data)
    
    bot.send_message(message.chat.id, 
        f"🔓 СЕКРЕТНАЯ АЧИВКА РАЗБЛОКИРОВАНА! 🔓\n\n"
        f"🏆 ШЕПЕЛЬФЕСТ\n"
        f"💰 +5555 шекелей!\n"
        f"⭐ +555 опыта!\n"
        f"💵 Новый баланс: {user['money']}")

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

# ========== БЛЕКДЖЕК ==========

def card_val(c):
    if c in ['J', 'Q', 'K']: return 10
    elif c == 'A': return 11
    else: return int(c)

def hand_sum(hand):
    s, aces = 0, 0
    for c in hand:
        if c in ['J', 'Q', 'K']:
            s += 10
        elif c == 'A':
            aces += 1
            s += 11
        else:
            s += int(c)
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
        telebot.types.InlineKeyboardButton("10", callback_data='bj_10'),
        telebot.types.InlineKeyboardButton("50", callback_data='bj_50'),
        telebot.types.InlineKeyboardButton("100", callback_data='bj_100')
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
    save_data(data)
    
    deck = new_deck()
    bj_games[uid] = {
        'bet': bet, 'player': [deck.pop(), deck.pop()], 'dealer': [deck.pop(), deck.pop()],
        'deck': deck, 'chat_id': call.message.chat.id, 'msg_id': call.message.message_id
    }
    
    bj_show(uid)
    bot.answer_callback_query(call.id)

def bj_show(uid):
    g = bj_games.get(uid)
    if not g: return
    
    ps = hand_sum(g['player'])
    ds = hand_sum([g['dealer'][0]])
    
    msg = f"🃏 БЛЕК ДЖЕК 🃏\n\n"
    msg += f"💰 СТАВКА: {g['bet']}\n\n"
    msg += f"👨‍💼 ДИЛЕР: {g['dealer'][0]} | ?\n⭐ {ds} + ?\n\n"
    msg += f"🎲 ТЫ: {' '.join(g['player'])}\n⭐ {ps}"
    
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
    uid = call.from_user.id
    g = bj_games.get(uid)
    if not g:
        bot.answer_callback_query(call.id, "❌ Игра не найдена!", show_alert=True)
        return
    
    g['player'].append(g['deck'].pop())
    ps = hand_sum(g['player'])
    
    if ps > 21:
        msg = f"🃏 БЛЕК ДЖЕК 🃏\n\n💰 СТАВКА: {g['bet']}\n\n🎲 {' '.join(g['player'])}\n⭐ {ps} ❌ ПЕРЕБОР!\n\n💔 ТЫ ПРОИГРАЛ {g['bet']}!"
        try:
            bot.edit_message_text(msg, g['chat_id'], g['msg_id'])
        except:
            pass
        bot.answer_callback_query(call.id, "ПЕРЕБОР!", show_alert=True)
        del bj_games[uid]
        return
    
    bj_games[uid] = g
    bj_show(uid)
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
        g['dealer'].append(g['deck'].pop())
        ds = hand_sum(g['dealer'])
    
    user = get_user(uid, call.from_user.username)
    
    if ds > 21 or ps > ds:
        win = g['bet'] * 2
        user['money'] += win
        user['total_earned'] += win
        user['bj_wins'] += 1
        add_exp(uid, win // 4)
        res = f"🎉 ПОБЕДА! +{win}"
    elif ps < ds:
        res = f"💔 ПРОИГРЫШ! -{g['bet']}"
    else:
        user['money'] += g['bet']
        res = f"🤝 НИЧЬЯ! +{g['bet']}"
    
    save_data(data)
    
    msg = f"🃏 БЛЕК ДЖЕК 🃏\n\n"
    msg += f"💰 СТАВКА: {g['bet']}\n\n"
    msg += f"👨‍💼 ДИЛЕР: {' '.join(g['dealer'])}\n⭐ {ds}\n\n"
    msg += f"🎲 ТЫ: {' '.join(g['player'])}\n⭐ {ps}\n\n"
    msg += f"{res}\n💰 БАЛАНС: {user['money']}"
    
    ach = check_achievements(uid)
    if ach:
        msg += ach
    
    try:
        bot.edit_message_text(msg, g['chat_id'], g['msg_id'])
    except:
        pass
    
    bot.answer_callback_query(call.id)
    del bj_games[uid]

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

# ========== ЗАПУСК ==========

print("=" * 50)
print("ХИТРЫЙ ЕВРЕЙ БОТ ЗАПУЩЕН!")
print("Слоты - работают")
print("Рулетка - работает")
print("Блекджек - работает")
print("Профиль - работает")
print("Топ - работает")
print("Сохранения - железобетонные")
print("=" * 50)

bot.infinity_polling()
