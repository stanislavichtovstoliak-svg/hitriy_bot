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
fortune_cooldown = {}

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
    'work_10': {'name': 'Трудоголик', 'desc': 'Выполнить 10 работ', 'target': 10, 'reward': 100},
    'work_50': {'name': 'Стахановец', 'desc': 'Выполнить 50 работ', 'target': 50, 'reward': 500},
    'work_100': {'name': 'Машина', 'desc': 'Выполнить 100 работ', 'target': 100, 'reward': 1000},
    'win_slot': {'name': 'Счастливчик', 'desc': 'Выиграть в слотах', 'target': 1, 'reward': 50},
    'win_bj': {'name': 'Картежник', 'desc': 'Выиграть в блекджек', 'target': 1, 'reward': 50},
    'win_roulette': {'name': 'Фортуна', 'desc': 'Выиграть в рулетку', 'target': 1, 'reward': 50},
    'money_1000': {'name': 'Тысячник', 'desc': 'Накопить 1000 шекелей', 'target': 1000, 'reward': 200},
    'money_5000': {'name': 'Богач', 'desc': 'Накопить 5000 шекелей', 'target': 5000, 'reward': 700},
    'money_10000': {'name': 'Магнат', 'desc': 'Накопить 10000 шекелей', 'target': 10000, 'reward': 1500},
    'level_5': {'name': 'Профи', 'desc': 'Достичь 5 уровня', 'target': 5, 'reward': 300},
    'level_8': {'name': 'Легенда', 'desc': 'Достичь 8 уровня', 'target': 8, 'reward': 1000},
    'daily_streak': {'name': 'Серийный', 'desc': 'Получить бонус 7 дней подряд', 'target': 7, 'reward': 500},
}

FORTUNE_REWARDS = [
    {"name": "50 шекелей", "money": 50, "exp": 0, "prob": 25},
    {"name": "100 шекелей", "money": 100, "exp": 0, "prob": 20},
    {"name": "200 шекелей", "money": 200, "exp": 0, "prob": 15},
    {"name": "500 шекелей", "money": 500, "exp": 0, "prob": 8},
    {"name": "1000 шекелей ДЖЕКПОТ!", "money": 1000, "exp": 0, "prob": 2},
    {"name": "50 опыта", "money": 0, "exp": 50, "prob": 15},
    {"name": "100 опыта", "money": 0, "exp": 100, "prob": 10},
    {"name": "200 опыта", "money": 0, "exp": 200, "prob": 5},
]

PROMOCODES = {
    'шепельпрезидент': {'money': 2000, 'exp': 200},
    'тест': {'money': 2, 'exp': 0},
    'куниза200шекелей': {'money': 199, 'exp': 0},
    'ялюблюгрибы': {'money': 666, 'exp': 0},
}

FAIL_MESSAGES = {
    "Грузчик": ["Уронил ящик! Штраф {} шекелей!", "Разбил вазу! -{} шекелей!"],
    "Курьер": ["Проткнул колесо! Штраф {} шекелей!", "Потерял посылку! -{} шекелей!"],
    "Автомеханик": ["Сорвал резьбу! Штраф {} шекелей!", "Забыл затянуть колесо! -{} шекелей!"],
    "Кладовщик": ["Перепутал товар! Штраф {} шекелей!", "Потерял накладную! -{} шекелей!"],
    "Менеджер": ["Поссорился с клиентом! Штраф {} шекелей!", "Провалил презентацию! -{} шекелей!"],
    "Бухгалтер": ["Ошибся в отчетности! Штраф {} шекелей!", "Потерял чеки! -{} шекелей!"],
    "Директор": ["Неудачная сделка! Штраф {} шекелей!", "Акции упали! -{} шекелей!"],
    "Магнат": ["Крипта провалилась! Штраф {} шекелей!", "Завод встал! -{} шекелей!"]
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
            'last_daily': None, 'daily_streak': 0, 'promos': [],
            'work_count': 0, 'slot_wins': 0, 'bj_wins': 0, 'roulette_wins': 0,
            'achievements': []
        }
        save_data()
    else:
        if username and data[uid].get('username') != username:
            data[uid]['username'] = username
            save_data()
    return data[uid]

def check_achievements(uid):
    user = get_user(uid)
    new_achievements = []
    
    if user['work_count'] >= 10 and 'work_10' not in user['achievements']:
        new_achievements.append('work_10')
    if user['work_count'] >= 50 and 'work_50' not in user['achievements']:
        new_achievements.append('work_50')
    if user['work_count'] >= 100 and 'work_100' not in user['achievements']:
        new_achievements.append('work_100')
    
    if user['slot_wins'] >= 1 and 'win_slot' not in user['achievements']:
        new_achievements.append('win_slot')
    if user['bj_wins'] >= 1 and 'win_bj' not in user['achievements']:
        new_achievements.append('win_bj')
    if user['roulette_wins'] >= 1 and 'win_roulette' not in user['achievements']:
        new_achievements.append('win_roulette')
    
    if user['money'] >= 1000 and 'money_1000' not in user['achievements']:
        new_achievements.append('money_1000')
    if user['money'] >= 5000 and 'money_5000' not in user['achievements']:
        new_achievements.append('money_5000')
    if user['money'] >= 10000 and 'money_10000' not in user['achievements']:
        new_achievements.append('money_10000')
    
    if user['level'] >= 5 and 'level_5' not in user['achievements']:
        new_achievements.append('level_5')
    if user['level'] >= 8 and 'level_8' not in user['achievements']:
        new_achievements.append('level_8')
    
    if user.get('daily_streak', 0) >= 7 and 'daily_streak' not in user['achievements']:
        new_achievements.append('daily_streak')
    
    msg = ""
    for ach_id in new_achievements:
        ach = ACHIEVEMENTS[ach_id]
        user['achievements'].append(ach_id)
        user['money'] += ach['reward']
        user['total_earned'] += ach['reward']
        msg += f"\n\n🏆 ДОСТИЖЕНИЕ ПОЛУЧЕНО: {ach['name']}\n💰 +{ach['reward']} шекелей!"
    
    if msg:
        save_data()
        return msg
    return None

def add_exp(uid, amount):
    user = get_user(uid)
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

def get_bot_stats():
    total_users = len(data)
    total_money = sum(u['money'] for u in data.values())
    total_earned = sum(u.get('total_earned', 0) for u in data.values())
    top_level = max((u.get('level', 1) for u in data.values()), default=1)
    return total_users, total_money, total_earned, top_level

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
    msg += f"• слоты - слоты с анимацией\n"
    msg += f"• блекджек - игра в 21\n"
    msg += f"• дуэль - в разработке 🚧\n"
    msg += f"• колесо / фортуна - Колесо Фортуны (раз в час)\n\n"
    msg += f"--- ЗАРАБОТОК ---\n"
    msg += f"• работа / фарм - работа (КД 10 мин)\n"
    msg += f"• бонус - ежедневный (КД 12 ч)\n\n"
    msg += f"--- ИНФО ---\n"
    msg += f"• баланс - проверить деньги\n"
    msg += f"• профиль - статистика\n"
    msg += f"• топ - топ богатых\n"
    msg += f"• достижения - список достижений\n"
    msg += f"• стата - статистика бота\n\n"
    msg += f"--- ПРОМОКОДЫ ---\n"
    msg += f"#промо название - активировать промокод"
    bot.send_message(message.chat.id, msg)

@bot.message_handler(func=lambda m: m.text and m.text.lower() == 'дуэль')
def duel_placeholder(message):
    bot.send_message(message.chat.id, "🚧 ДУЭЛИ В РАЗРАБОТКЕ! 🚧\n\nСкоро появятся, следи за обновлениями!")

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
    else:
        earned = base
        user['money'] += earned
        user['total_earned'] += earned
        user['work_count'] += 1
        exp_gain = earned // 2
        user['exp'] += exp_gain
        user['total_exp'] += exp_gain
        msg = f"🌾 ТЫ ПОРАБОТАЛ! 🌾\n\n💼 {level_info['name']}\n💰 +{earned} шекелей\n⭐ +{exp_gain} опыта\n💵 Баланс: {user['money']}"
    
    user['last_work'] = datetime.now().isoformat()
    
    leveled = False
    if not fail:
        for lvl in range(user['level'] + 1, 9):
            if user['total_exp'] >= LEVELS[lvl]['exp_needed']:
                user['level'] = lvl
                leveled = True
            else:
                break
        if leveled:
            new_level = get_level_info(user['level'])
            msg += f"\n\n🎉 НОВЫЙ УРОВЕНЬ! {user['level']} - {new_level['name']}"
    
    save_data()
    
    # Проверка ачивок
    ach_msg = check_achievements(uid)
    if ach_msg:
        msg += ach_msg
    
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
    msg += f"🎁 Серия бонусов: {user.get('daily_streak', 0)}\n"
    msg += f"📦 Работ выполнено: {user.get('work_count', 0)}\n"
    msg += f"🏆 Достижений получено: {len(user.get('achievements', []))}"
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
    
    ach_msg = check_achievements(uid)
    if ach_msg:
        msg += ach_msg
    
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

@bot.message_handler(func=lambda m: m.text and m.text.lower() in ['достижения', 'ачивки'])
def achievements_cmd(message):
    uid = message.from_user.id
    user = get_user(uid, message.from_user.username)
    completed = user.get('achievements', [])
    
    msg = f"🏆 ДОСТИЖЕНИЯ 🏆\n\n"
    
    for ach_id, ach in ACHIEVEMENTS.items():
        if ach_id in completed:
            msg += f"✅ {ach['name']} - {ach['desc']}\n"
        else:
            msg += f"❌ {ach['name']} - {ach['desc']} (награда: {ach['reward']}💰)\n"
    
    msg += f"\n📊 Получено: {len(completed)}/{len(ACHIEVEMENTS)}"
    bot.send_message(message.chat.id, msg)

@bot.message_handler(func=lambda m: m.text and m.text.lower() in ['стата', 'статистика', 'статистика бота'])
def stats_cmd(message):
    total_users, total_money, total_earned, top_level = get_bot_stats()
    
    msg = f"📊 СТАТИСТИКА БОТА 📊\n\n"
    msg += f"👥 Всего игроков: {total_users}\n"
    msg += f"💰 Всего денег у игроков: {total_money}\n"
    msg += f"💵 Всего заработано: {total_earned}\n"
    msg += f"🏆 Максимальный уровень: {top_level}\n"
    msg += f"🎰 Активных игр: рулетка, слоты, блекджек\n"
    bot.send_message(message.chat.id, msg)

@bot.message_handler(func=lambda m: m.text and m.text.lower() in ['колесо', 'фортуна', 'колесо фортуны'])
def fortune_cmd(message):
    uid = message.from_user.id
    user = get_user(uid, message.from_user.username)
    now = time.time()
    
    if uid in fortune_cooldown:
        last = fortune_cooldown[uid]
        if now - last < 3600:
            left = int(3600 - (now - last))
            h = left // 3600
            m = (left % 3600) // 60
            bot.send_message(message.chat.id, f"🎡 Колесо Фортуны доступно через {h}ч {m}мин!")
            return
    
    # Выбор награды
    total_prob = sum(r['prob'] for r in FORTUNE_REWARDS)
    roll = random.randint(1, total_prob)
    cum = 0
    reward = None
    for r in FORTUNE_REWARDS:
        cum += r['prob']
        if roll <= cum:
            reward = r
            break
    
    msg = ""
    if reward['money'] > 0:
        user['money'] += reward['money']
        user['total_earned'] += reward['money']
        msg = f"🎡 КОЛЕСО ФОРТУНЫ 🎡\n\n💰 Выпало: {reward['name']}!\n💵 Баланс: {user['money']}"
    elif reward['exp'] > 0:
        leveled = add_exp(uid, reward['exp'])
        msg = f"🎡 КОЛЕСО ФОРТУНЫ 🎡\n\n⭐ Выпало: {reward['name']}!\n"
        if leveled:
            new_level = get_level_info(user['level'])
            msg += f"\n🎉 НОВЫЙ УРОВЕНЬ! {user['level']} - {new_level['name']}"
    else:
        msg = f"🎡 КОЛЕСО ФОРТУНЫ 🎡\n\n{reward['name']}!"
    
    fortune_cooldown[uid] = now
    save_data()
    bot.send_message(message.chat.id, msg)

# ========== СЛОТЫ ==========

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
    
    msg = bot.send_message(message.chat.id, "🎰 КРУТИМ... 🎰\n\n🌀 | 🌀 | 🌀")
    time.sleep(0.5)
    
    for step in range(3):
        spin1 = random.choice(SLOT_SYMBOLS)
        spin2 = random.choice(SLOT_SYMBOLS)
        spin3 = random.choice(SLOT_SYMBOLS)
        bot.edit_message_text(f"🎰 КРУТИМ... 🎰\n\n{spin1} | {spin2} | {spin3}", message.chat.id, msg.message_id)
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
        save_data()
    
    msg_text = f"🎰 РЕЗУЛЬТАТ 🎰\n\n"
    msg_text += f"┌───┬───┬───┐\n"
    msg_text += f"│ {result[0]} │ {result[1]} │ {result[2]} │\n"
    msg_text += f"└───┴───┴───┘\n\n"
    msg_text += f"{win_type}\n"
    if win > 0:
        msg_text += f"💰 +{win} шекелей!\n"
    msg_text += f"💵 Баланс: {user['money']}"
    
    ach_msg = check_achievements(uid)
    if ach_msg:
        msg_text += ach_msg
    
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
        user['roulette_wins'] += 1
        add_exp(uid, win // 4)
        msg = f"🎡 РУЛЕТКА 🎡\n\n🎲 {emoji} {num}\n🎯 {names[bet_type]} {bet}\n💰 ВЫИГРЫШ: +{win}\n💵 Баланс: {user['money']}"
    else:
        msg = f"🎡 РУЛЕТКА 🎡\n\n🎲 {emoji} {num}\n🎯 {names[bet_type]} {bet}\n💔 ПРОИГРЫШ\n💵 Баланс: {user['money']}"
    
    save_data()
    
    ach_msg = check_achievements(uid)
    if ach_msg:
        msg += ach_msg
    
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
        card = g['deck'].pop()
        g['dealer'].append(card)
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
    save_data()
    msg = f"🃏 БЛЕК ДЖЕК 🃏\n\n💰 СТАВКА: {g['bet']}\n\n"
    msg += f"👨‍💼 ДИЛЕР: {' '.join(g['dealer'])}\n⭐ {ds}\n\n"
    msg += f"🎲 ТЫ: {' '.join(g['player'])}\n⭐ {ps}\n\n{res}\n💰 БАЛАНС: {user['money']}"
    
    ach_msg = check_achievements(uid)
    if ach_msg:
        msg += ach_msg
    
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
print("Колесо Фортуны - работает")
print("Достижения - работают")
print("=" * 50)

bot.infinity_polling()
