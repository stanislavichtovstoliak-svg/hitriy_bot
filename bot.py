import telebot
import random
import json
import os
import shutil
from datetime import datetime, timedelta
import time
import threading

TOKEN = '8672284943:AAEVBa7F9rKGQK76pkLr0vvHyDXKFCJDFos'
bot = telebot.TeleBot(TOKEN)

DATA_FILE = 'users.json'
LOTTO_FILE = 'lotto.json'

# ========== АЛМАЗНЫЕ СОХРАНЕНИЯ ==========
def safe_save(data, filename):
    try:
        temp_file = filename + '.tmp'
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        if os.path.exists(filename):
            shutil.copy2(filename, filename + '.backup')
        os.replace(temp_file, filename)
        return True
    except:
        return False

def safe_load(filename, default={}):
    try:
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
    except:
        backup = filename + '.backup'
        if os.path.exists(backup):
            try:
                with open(backup, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    safe_save(data, filename)
                    return data
            except:
                pass
    return default

data = safe_load(DATA_FILE)
lotto_data = safe_load(LOTTO_FILE, {'tickets': {}, 'last_draw': None, 'winner_today': False})

def save_all():
    safe_save(data, DATA_FILE)
    safe_save(lotto_data, LOTTO_FILE)

# ========== ДАННЫЕ ПОЛЬЗОВАТЕЛЯ ==========
DEFAULT_USER = {
    'money': 500, 'level': 1, 'exp': 0, 'total_exp': 0, 'last_work': None,
    'username': None, 'total_earned': 0, 'last_daily': None, 'daily_streak': 0,
    'promos': [], 'work_count': 0, 'slot_wins': 0, 'roulette_wins': 0,
    'bet_wins': 0, 'achievements': [], 'shop_buffs': {},
    'daily_quests': None, 'last_quest_reset': None, 'lotto_ticket': None,
    'lotto_wins': 0, 'bank_deposit': 0, 'bank_time': None
}

# ========== ПРОФЕССИИ (12 УРОВНЕЙ) ==========
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

# ========== МАГАЗИН ==========
SHOP_ITEMS = {
    1: {'name': '⚡ Ускорение работы', 'price': 500, 'duration': 3600, 'effect': 'work_cooldown', 'value': 300},
    2: {'name': '⭐ Двойной опыт', 'price': 300, 'duration': 3600, 'effect': 'exp_multiplier', 'value': 2},
    3: {'name': '🛡️ Защита от неудач', 'price': 200, 'duration': 3, 'effect': 'no_fail', 'value': 3},
    4: {'name': '📈 +25% к зарплате', 'price': 400, 'duration': 86400, 'effect': 'salary_multiplier', 'value': 1.25},
}

# ========== АЧИВКИ ==========
ACHIEVEMENTS = {
    'work_10': {'name': "📦 Трудоголик", 'reward': 100}, 'work_50': {'name': "🏭 Стахановец", 'reward': 500},
    'work_100': {'name': "💪 Машина", 'reward': 1000}, 'work_500': {'name': "🤖 Терминатор", 'reward': 5000},
    'win_slot': {'name': "🎰 Счастливчик", 'reward': 50}, 'win_roulette': {'name': "🎡 Фортуна", 'reward': 50},
    'win_bet': {'name': "🏇 Лучший каппер", 'reward': 100}, 'money_1000': {'name': "💰 Тысячник", 'reward': 200},
    'money_5000': {'name': "💎 Богач", 'reward': 700}, 'money_10000': {'name': "👑 Магнат", 'reward': 1500},
    'money_50000': {'name': "🏦 Крез", 'reward': 5000}, 'level_5': {'name': "📈 Профи", 'reward': 300},
    'level_8': {'name': "⭐ Эксперт", 'reward': 700}, 'level_10': {'name': "🏆 Мастер", 'reward': 1200},
    'level_12': {'name': "👑 Легенда", 'reward': 2000}, 'daily_streak': {'name': "🔥 Серийный", 'reward': 500},
    'daily_streak_30': {'name': "💪 Железный", 'reward': 3000}, 'lotto_win': {'name': "🍀 Везунчик", 'reward': 500},
    'lotto_win_3': {'name': "👑 Король лотереи", 'reward': 2000}, 'bank_first': {'name': "🏦 Инвестор", 'reward': 200},
}

# ========== ПРОМОКОДЫ ==========
PROMOCODES = {
    'шепельпрезидент': {'money': 2000, 'exp': 200}, 'тест': {'money': 2, 'exp': 0},
    'куниза200шекелей': {'money': 199, 'exp': 0}, 'ялюблюгрибы': {'money': 666, 'exp': 0},
    'яустал': {'money': 228, 'exp': 0}, 'квестыилотерея': {'money': 100, 'exp': 50},
}

# ========== СЛОТЫ ==========
SLOT_SYMBOLS = ['🍒', '🍊', '🍋', '🍉', '🍇', '💰', '💎', '🎰', '7️⃣']
SLOT_LINES = [
    ([0,0], [0,1], [0,2]), ([1,0], [1,1], [1,2]), ([2,0], [2,1], [2,2]),
    ([0,0], [1,1], [2,2]), ([0,2], [1,1], [2,0]), ([0,0], [1,0], [2,0]),
    ([0,1], [1,1], [2,1]), ([0,2], [1,2], [2,2])
]
SLOT_PAYOUTS = {
    ('7️⃣', '7️⃣', '7️⃣'): 50, ('🎰', '🎰', '🎰'): 40, ('💎', '💎', '💎'): 30,
    ('💰', '💰', '💰'): 25, ('🍇', '🍇', '🍇'): 20, ('🍉', '🍉', '🍉'): 15,
    ('🍒', '🍒', '🍒'): 10, ('🍊', '🍊', '🍊'): 10, ('🍋', '🍋', '🍋'): 10,
}

# ========== ЛОШАДИ ==========
HORSES = [
    {"name": "МОЛНИЯ", "emoji": "🐎", "coefficient": 6.0, "chance": 10},
    {"name": "ВЕТЕР", "emoji": "🐎", "coefficient": 4.0, "chance": 15},
    {"name": "ГРОМ", "emoji": "🐎", "coefficient": 3.0, "chance": 20},
    {"name": "МОЛОТ", "emoji": "🐎", "coefficient": 2.5, "chance": 25},
    {"name": "СТРЕЛА", "emoji": "🐎", "coefficient": 2.0, "chance": 30},
    {"name": "ТИХОНЯ", "emoji": "🐎", "coefficient": 10.0, "chance": 5},
]

# ========== ЗАДАНИЯ ==========
QUESTS = [
    {"name": "🎰 Счастливчик", "desc": "Сыграть в слоты 3 раза", "type": "slot", "target": 3, "reward": 200},
    {"name": "🎡 Фортуна", "desc": "Выиграть в рулетку 2 раза", "type": "roulette_win", "target": 2, "reward": 150},
    {"name": "🏇 Каппер", "desc": "Сделать 5 ставок", "type": "bet", "target": 5, "reward": 300},
    {"name": "💰 Труженик", "desc": "Заработать 500💰", "type": "earn", "target": 500, "reward": 200},
    {"name": "🌾 Работяга", "desc": "Поработать 10 раз", "type": "work", "target": 10, "reward": 250},
    {"name": "🏆 Победитель", "desc": "Выиграть в скачках 2 раза", "type": "bet_win", "target": 2, "reward": 350},
]

# ========== СООБЩЕНИЯ НЕУДАЧ ==========
FAIL_MESSAGES = {
    "Грузчик": ["💥 Уронил ящик! -{}💰", "📦 Разбил вазу! -{}💰"],
    "Курьер": ["🛵 Проткнул колесо! -{}💰", "📬 Потерял посылку! -{}💰"],
    "Автомеханик": ["🔧 Сорвал резьбу! -{}💰", "⚡ Забыл затянуть колесо! -{}💰"],
    "Кладовщик": ["📦 Перепутал товар! -{}💰", "🏷 Потерял накладную! -{}💰"],
    "Доставщик": ["🍕 Пролил кофе клиенту! -{}💰", "📦 Перепутал заказ! -{}💰"],
    "Сварщик": ["🔥 Прожег дыру! -{}💰", "💣 Уронил баллон! -{}💰"],
    "Менеджер": ["📞 Поссорился с клиентом! -{}💰", "💼 Провалил презентацию! -{}💰"],
    "Бухгалтер": ["📊 Ошибся в отчетности! -{}💰", "🧾 Потерял чеки! -{}💰"],
    "Прораб": ["🏗 Бригада не вышла! -{}💰", "🔥 Сгорел материал! -{}💰"],
    "Директор": ["🏢 Неудачная сделка! -{}💰", "📉 Акции упали! -{}💰"],
    "Бизнесмен": ["💎 Крипта обвалилась! -{}💰", "🤝 Партнер кинул! -{}💰"],
    "Магнат": ["🏦 Банкротство филиала! -{}💰", "⚔️ Рейдерский захват! -{}💰"],
}

# ========== ПЕРЕМЕННЫЕ ==========
slot_waiting = {}
roulette_waiting = {}
bank_waiting = {}
horse_race_active = False
horse_race_bets = {}
horse_race_events = []
horse_race_thread_running = False

# ========== ФУНКЦИИ ==========
def get_user(user_id, username=None):
    uid = str(user_id)
    if uid not in data:
        data[uid] = DEFAULT_USER.copy()
        data[uid]['username'] = username
        save_all()
    else:
        if username and data[uid].get('username') != username:
            data[uid]['username'] = username
            save_all()
        for key in DEFAULT_USER:
            if key not in data[uid]:
                data[uid][key] = DEFAULT_USER[key]
                save_all()
    return data[uid]

def add_exp(uid, amount):
    user = get_user(uid)
    if user.get('shop_buffs', {}).get('exp_multiplier', {}).get('active_until', 0) > time.time():
        amount = int(amount * 2)
    user['exp'] += amount
    user['total_exp'] += amount
    leveled = False
    for lvl in range(user['level'] + 1, 13):
        if user['total_exp'] >= LEVELS[lvl]['exp_needed']:
            user['level'] = lvl
            leveled = True
    save_all()
    return leveled

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
    if user.get('lotto_wins', 0) >= 1 and 'lotto_win' not in user['achievements']: new.append('lotto_win')
    if user.get('lotto_wins', 0) >= 3 and 'lotto_win_3' not in user['achievements']: new.append('lotto_win_3')
    if user.get('bank_deposit', 0) > 0 and 'bank_first' not in user['achievements']: new.append('bank_first')
    msg = ""
    for ach in new:
        user['achievements'].append(ach)
        user['money'] += ACHIEVEMENTS[ach]['reward']
        user['total_earned'] += ACHIEVEMENTS[ach]['reward']
        msg += f"\n\n🏆 {ACHIEVEMENTS[ach]['name']} +{ACHIEVEMENTS[ach]['reward']}💰"
    if msg:
        save_all()
    return msg

def get_top():
    return sorted([(u.get('username', 'Игрок'), u['money']) for u in data.values()], key=lambda x: x[1], reverse=True)[:10]

def reset_daily_quests(uid):
    user = get_user(uid)
    today = datetime.now().date().isoformat()
    if user.get('last_quest_reset') != today:
        user['daily_quests'] = []
        for q in random.sample(QUESTS, 3):
            user['daily_quests'].append({'name': q['name'], 'desc': q['desc'], 'type': q['type'],
                'target': q['target'], 'reward': q['reward'], 'progress': 0, 'completed': False})
        user['last_quest_reset'] = today
        save_all()

def update_quest(uid, qtype, amount=1):
    user = get_user(uid)
    reset_daily_quests(uid)
    msg = ""
    for q in user.get('daily_quests', []):
        if not q['completed'] and q['type'] == qtype:
            q['progress'] += amount
            if q['progress'] >= q['target']:
                q['completed'] = True
                user['money'] += q['reward']
                user['total_earned'] += q['reward']
                msg += f"\n\n✅ ЗАДАНИЕ: {q['name']} +{q['reward']}💰"
    if msg:
        save_all()
    return msg

# ========== КРАСИВЫЙ ПРОФИЛЬ ==========
@bot.message_handler(commands=['start'])
def start_cmd(message):
    uid = message.from_user.id
    user = get_user(uid, message.from_user.username)
    reset_daily_quests(uid)
    bot.send_message(message.chat.id,
        f"🎮 *ХИТРЫЙ ЕВРЕЙ* 🎮\n\n"
        f"👋 Привет, @{message.from_user.username}!\n"
        f"💰 Баланс: *{user['money']}*\n"
        f"📊 Уровень: *{user['level']}* — {LEVELS[user['level']]['name']}\n\n"
        f"📝 Напиши *команды* для списка!",
        parse_mode='Markdown')

@bot.message_handler(func=lambda m: m.text and m.text.lower() == 'команды')
def show_commands(m):
    msg = f"📋 *СПИСОК КОМАНД* 📋\n\n"
    msg += f"┌─ 🎮 *ИГРЫ*\n│  ├ 🎰 слоты - слоты с анимацией\n│  ├ 🎡 рулетка - рулетка\n│  ├ 🐎 скачки - ставки на лошадей\n│  └ 🎫 лотерея - купить билет (18-19 МСК)\n\n"
    msg += f"├─ 💰 *ЭКОНОМИКА*\n│  ├ 🌾 работа - работа (КД 10 мин)\n│  ├ 🎁 бонус - ежедневный (КД 12 ч)\n│  ├ 🏦 депозит - вложить деньги под 4%\n│  └ 💸 забрать - снять депозит\n\n"
    msg += f"├─ 🛒 *МАГАЗИН*\n│  ├ 🏪 магазин - список товаров\n│  └ 🔢 купить 1-4 - покупка\n\n"
    msg += f"└─ 📊 *ИНФО*\n    ├ 💰 баланс - проверить деньги\n    ├ 📊 профиль - полная статистика\n    ├ 🏆 топ - топ богатых\n    └ 🏅 достижения - список ачивок"
    bot.send_message(m.chat.id, msg, parse_mode='Markdown')

@bot.message_handler(func=lambda m: m.text and m.text.lower() in ['баланс', 'деньги'])
def balance_cmd(m):
    u = get_user(m.from_user.id, m.from_user.username)
    bot.send_message(m.chat.id, f"💰 *БАЛАНС* 💰\n\n💵 {u['money']} шекелей\n⭐ Опыт: {u['exp']}", parse_mode='Markdown')

@bot.message_handler(func=lambda m: m.text and m.text.lower() in ['топ', 'топ10', 'лидеры'])
def top_cmd(m):
    top = get_top()
    if not top:
        bot.send_message(m.chat.id, "🏆 Топ пока пуст!")
        return
    msg = "🏆 *ТОП БОГАТЫХ* 🏆\n\n"
    for i, (name, money) in enumerate(top, 1):
        if i == 1: msg += f"👑 *{i}. @{name}* — {money}💰\n"
        elif i == 2: msg += f"🥈 *{i}. @{name}* — {money}💰\n"
        elif i == 3: msg += f"🥉 *{i}. @{name}* — {money}💰\n"
        else: msg += f"{i}. @{name} — {money}💰\n"
    bot.send_message(m.chat.id, msg, parse_mode='Markdown')

@bot.message_handler(func=lambda m: m.text and m.text.lower() in ['профиль', 'стата'])
def profile_cmd(m):
    uid = m.from_user.id
    u = get_user(uid, m.from_user.username)
    lvl = LEVELS[u['level']]
    now = time.time()
    
    next_lvl = u['level'] + 1
    if next_lvl <= 12:
        need = LEVELS[next_lvl]['exp_needed']
        prog = int((u['total_exp'] / need) * 100) if need > 0 else 100
        bar = '▓' * (prog // 10) + '░' * (10 - (prog // 10))
    else:
        prog, bar = 100, '▓▓▓▓▓▓▓▓▓▓'
    
    buffs = ""
    for key, buff in u.get('shop_buffs', {}).items():
        if key == 'work_cooldown' and buff.get('active_until', 0) > now:
            buffs += f"\n⚡ Ускорение работы ({int((buff['active_until']-now)/60)} мин)"
        elif key == 'exp_multiplier' and buff.get('active_until', 0) > now:
            buffs += f"\n⭐ Двойной опыт ({int((buff['active_until']-now)/60)} мин)"
        elif key == 'salary_multiplier' and buff.get('active_until', 0) > now:
            buffs += f"\n📈 +25% зарплаты ({int((buff['active_until']-now)/3600)} ч)"
        elif key == 'no_fail' and buff.get('uses', 0) > 0:
            buffs += f"\n🛡️ Защита от неудач (осталось {buff['uses']})"
    
    bank_info = ""
    if u.get('bank_deposit', 0) > 0 and u.get('bank_time'):
        end = datetime.fromisoformat(u['bank_time'])
        left = (end - datetime.now()).total_seconds()
        if left > 0:
            h = int(left // 3600)
            mm = int((left % 3600) // 60)
            bank_info = f"\n🏦 Депозит: {u['bank_deposit']}💰 (готов через {h}ч {mm}мин)"
        else:
            bank_info = f"\n🏦 Депозит: {u['bank_deposit']}💰 (готов к забору!)"
    
    msg = f"📊 *ПРОФИЛЬ* 📊\n\n"
    msg += f"👤 @{u.get('username') or 'Игрок'}\n"
    msg += f"🏆 Уровень {u['level']} — {lvl['name']}\n"
    msg += f"💰 Денег: *{u['money']}*\n"
    msg += f"⭐ Опыт: {u['exp']}\n"
    msg += f"📈 Всего заработал: {u['total_earned']}\n"
    msg += f"🎁 Серия бонусов: {u.get('daily_streak', 0)}\n"
    msg += f"📦 Работ: {u.get('work_count', 0)}\n"
    msg += f"🏆 Достижений: {len(u.get('achievements', []))}\n"
    msg += f"🎫 Билет лотереи: {u.get('lotto_ticket', 'Нет')}\n"
    if bank_info: msg += bank_info
    if buffs: msg += f"\n✨ *БАФФЫ*{buffs}"
    msg += f"\n\n📊 *Прогресс* до {next_lvl} уровня:\n`{bar}` *{prog}%*"
    msg += f"\n\n🎲 *ЛОТЕРЕЯ* | ⏰ Розыгрыш в 19:00 МСК"
    bot.send_message(m.chat.id, msg, parse_mode='Markdown')

# ========== РАБОТА ==========
@bot.message_handler(func=lambda m: m.text and m.text.lower() in ['работа', 'фарм'])
def work_cmd(m):
    uid = m.from_user.id
    u = get_user(uid, m.from_user.username)
    lvl = LEVELS[u['level']]
    cd = 300 if u.get('shop_buffs', {}).get('work_cooldown', {}).get('active_until', 0) > time.time() else 600
    
    if u.get('last_work'):
        last = datetime.fromisoformat(u['last_work'])
        diff = (datetime.now() - last).total_seconds()
        if diff < cd:
            rem = int(cd - diff)
            bot.send_message(m.chat.id, f"⏰ Отдыхай {rem//60} мин {rem%60} сек")
            return
    
    base = random.randint(lvl['salary_min'], lvl['salary_max'])
    if u.get('shop_buffs', {}).get('salary_multiplier', {}).get('active_until', 0) > time.time():
        base = int(base * 1.25)
    
    if random.randint(1, 100) <= 5 and not (u.get('shop_buffs', {}).get('no_fail', {}).get('uses', 0) > 0):
        penalty = random.randint(int(base*0.3), int(base*0.7))
        u['money'] -= penalty
        u['total_earned'] -= penalty
        msg = f"😫 *НЕУДАЧА!*\n\n💼 {lvl['name']}\n{random.choice(FAIL_MESSAGES[lvl['name'].split()[-1] if len(lvl['name'].split()) > 1 else lvl['name']]).format(penalty)}\n💵 Баланс: {u['money']}"
    else:
        if u.get('shop_buffs', {}).get('no_fail', {}).get('uses', 0) > 0:
            u['shop_buffs']['no_fail']['uses'] -= 1
            if u['shop_buffs']['no_fail']['uses'] <= 0:
                del u['shop_buffs']['no_fail']
        u['money'] += base
        u['total_earned'] += base
        u['work_count'] += 1
        exp = base//2
        u['exp'] += exp
        u['total_exp'] += exp
        msg = f"🌾 *ТЫ ПОРАБОТАЛ!* 🌾\n\n💼 {lvl['name']}\n💰 +{base}💰\n⭐ +{exp} опыта\n💵 Баланс: {u['money']}"
        leveled = False
        for lvl2 in range(u['level']+1, 13):
            if u['total_exp'] >= LEVELS[lvl2]['exp_needed']:
                u['level'] = lvl2
                leveled = True
        if leveled:
            msg += f"\n\n🎉 *НОВЫЙ УРОВЕНЬ!* {u['level']} — {LEVELS[u['level']]['name']}"
    
    u['last_work'] = datetime.now().isoformat()
    save_all()
    qmsg = update_quest(uid, 'work', 1) + update_quest(uid, 'earn', base)
    if qmsg: msg += qmsg
    ach = check_achievements(uid)
    if ach: msg += ach
    bot.send_message(m.chat.id, msg, parse_mode='Markdown')

# ========== ЕЖЕДНЕВНЫЙ БОНУС ==========
@bot.message_handler(func=lambda m: m.text and m.text.lower() in ['бонус', 'ежедневный'])
def daily_cmd(m):
    uid = m.from_user.id
    u = get_user(uid, m.from_user.username)
    if u.get('last_daily'):
        last = datetime.fromisoformat(u['last_daily'])
        diff = (datetime.now() - last).total_seconds()
        if diff < 43200:
            h = int((43200-diff)//3600)
            mm = int(((43200-diff)%3600)//60)
            bot.send_message(m.chat.id, f"🎁 Бонус через {h}ч {mm}мин\n🔥 Серия: {u.get('daily_streak',0)}")
            return
    bonus = random.randint(50,200)
    u['money'] += bonus
    u['total_earned'] += bonus
    u['last_daily'] = datetime.now().isoformat()
    u['daily_streak'] = u.get('daily_streak',0)+1
    lev = add_exp(uid, bonus//3)
    msg = f"🎁 *ЕЖЕДНЕВНЫЙ БОНУС* 🎁\n\n💰 +{bonus}💰\n⭐ +{bonus//3} опыта\n🔥 Серия: {u['daily_streak']}\n💵 Баланс: {u['money']}"
    if lev: msg += f"\n\n🎉 *НОВЫЙ УРОВЕНЬ!* {u['level']} — {LEVELS[u['level']]['name']}"
    ach = check_achievements(uid)
    if ach: msg += ach
    bot.send_message(m.chat.id, msg, parse_mode='Markdown')

# ========== ПРОМОКОДЫ ==========
@bot.message_handler(func=lambda m: m.text and m.text.lower().startswith('#промо'))
def promo_cmd(m):
    uid = m.from_user.id
    u = get_user(uid, m.from_user.username)
    promo = m.text.lower().replace('#промо', '').strip()
    if promo in u.get('promos', []):
        bot.send_message(m.chat.id, f"❌ Промокод {promo} уже использован!")
        return
    if promo in PROMOCODES:
        p = PROMOCODES[promo]
        u['money'] += p['money']
        u['total_earned'] += p['money']
        u['promos'].append(promo)
        msg = f"🎁 *ПРОМОКОД АКТИВИРОВАН!*\n\n✅ {promo}\n💰 +{p['money']}"
        if p['exp'] > 0:
            lev = add_exp(uid, p['exp'])
            msg += f"\n⭐ +{p['exp']}"
            if lev: msg += f"\n\n🎉 *НОВЫЙ УРОВЕНЬ!* {u['level']} — {LEVELS[u['level']]['name']}"
        msg += f"\n💵 Баланс: {u['money']}"
        bot.send_message(m.chat.id, msg, parse_mode='Markdown')
    else:
        bot.send_message(m.chat.id, f"❌ Промокод не найден!")

# ========== ДОСТИЖЕНИЯ ==========
@bot.message_handler(func=lambda m: m.text and m.text.lower() in ['достижения', 'ачивки'])
def achievements_cmd(m):
    u = get_user(m.from_user.id, m.from_user.username)
    msg = f"🏆 *ДОСТИЖЕНИЯ* 🏆\n\n"
    for aid, ach in ACHIEVEMENTS.items():
        if aid in u.get('achievements', []):
            msg += f"✅ {ach['name']} +{ach['reward']}💰\n"
        else:
            msg += f"❌ {ach['name']} +{ach['reward']}💰\n"
    msg += f"\n📊 Получено: {len(u.get('achievements',[]))}/{len(ACHIEVEMENTS)}"
    bot.send_message(m.chat.id, msg, parse_mode='Markdown')

# ========== СЕКРЕТНАЯ АЧИВКА ==========
@bot.message_handler(func=lambda m: m.text and all(w in m.text.lower() for w in ['шепель', 'лох', 'нищий', 'бомж']))
def secret_achievement(m):
    uid = m.from_user.id
    u = get_user(uid, m.from_user.username)
    if 'secret' in u.get('achievements', []):
        bot.send_message(m.chat.id, "❌ Ты уже получил секретную награду!")
        return
    u['achievements'].append('secret')
    u['money'] += 5555
    u['total_earned'] += 5555
    add_exp(uid, 555)
    save_all()
    bot.send_message(m.chat.id, f"🔓 *СЕКРЕТНАЯ АЧИВКА!*\n\n🏆 ШЕПЕЛЬФЕСТ\n💰 +5555💰\n⭐ +555⭐\n💵 Баланс: {u['money']}", parse_mode='Markdown')

# ========== МАГАЗИН ==========
@bot.message_handler(func=lambda m: m.text and m.text.lower() == 'магазин')
def shop_cmd(m):
    msg = f"🛒 *МАГАЗИН* 🛒\n\n"
    for k, item in SHOP_ITEMS.items():
        msg += f"{k}. {item['name']} — {item['price']}💰\n"
    msg += f"\n💡 Напиши *купить 1-4*"
    bot.send_message(m.chat.id, msg, parse_mode='Markdown')

@bot.message_handler(func=lambda m: m.text and m.text.lower().startswith('купить'))
def buy_cmd(m):
    uid = m.from_user.id
    u = get_user(uid, m.from_user.username)
    parts = m.text.split()
    if len(parts) < 2:
        bot.send_message(m.chat.id, "❌ Укажи номер товара! Пример: купить 1")
        return
    try:
        item_id = int(parts[1])
        if item_id not in SHOP_ITEMS:
            bot.send_message(m.chat.id, "❌ Неверный номер товара!")
            return
    except:
        bot.send_message(m.chat.id, "❌ Введи число 1-4")
        return
    
    item = SHOP_ITEMS[item_id]
    if u['money'] < item['price']:
        bot.send_message(m.chat.id, f"❌ Не хватает {item['price']}💰")
        return
    
    u['money'] -= item['price']
    if 'shop_buffs' not in u: u['shop_buffs'] = {}
    now = time.time()
    if item_id == 3:
        if 'no_fail' in u['shop_buffs']:
            u['shop_buffs']['no_fail']['uses'] += item['value']
        else:
            u['shop_buffs']['no_fail'] = {'uses': item['value'], 'active_until': now + 86400}
    else:
        u['shop_buffs'][item['effect']] = {'active_until': now + item['duration']}
    save_all()
    bot.send_message(m.chat.id, f"✅ {item['name']} куплен!\n💵 Баланс: {u['money']}", parse_mode='Markdown')

# ========== БАНК ==========
@bot.message_handler(func=lambda m: m.text and m.text.lower() in ['депозит', 'вложить'])
def deposit_cmd(m):
    bot.send_message(m.chat.id, "🏦 *ДЕПОЗИТ* 🏦\n\n💰 Процент: *4%* за 5 часов\n📝 Введи сумму (мин 100):", parse_mode='Markdown')
    bank_waiting[m.from_user.id] = 'waiting'

@bot.message_handler(func=lambda m: m.from_user.id in bank_waiting)
def deposit_amount(m):
    uid = m.from_user.id
    del bank_waiting[uid]
    try:
        amount = int(m.text.strip())
        if amount < 100:
            bot.send_message(m.chat.id, "❌ Минимум 100💰")
            return
    except:
        bot.send_message(m.chat.id, "❌ Введи число!")
        return
    
    u = get_user(uid, m.from_user.username)
    if u['money'] < amount:
        bot.send_message(m.chat.id, f"❌ Не хватает {amount}💰")
        return
    
    u['money'] -= amount
    u['bank_deposit'] = amount
    u['bank_time'] = (datetime.now() + timedelta(hours=5)).isoformat()
    save_all()
    check_achievements(uid)
    bot.send_message(m.chat.id, f"✅ *ДЕПОЗИТ ОТКРЫТ!*\n\n💰 Сумма: {amount}💰\n📈 Через 5 часов ты получишь *{int(amount * 1.04)}*💰\n💵 Баланс: {u['money']}", parse_mode='Markdown')

@bot.message_handler(func=lambda m: m.text and m.text.lower() in ['забрать', 'депозит снять'])
def withdraw_cmd(m):
    uid = m.from_user.id
    u = get_user(uid, m.from_user.username)
    if not u.get('bank_deposit', 0):
        bot.send_message(m.chat.id, "❌ У тебя нет активного депозита!")
        return
    if not u.get('bank_time'):
        bot.send_message(m.chat.id, "❌ Ошибка: нет времени депозита")
        return
    
    end = datetime.fromisoformat(u['bank_time'])
    if datetime.now() < end:
        left = (end - datetime.now()).total_seconds()
        h = int(left // 3600)
        mm = int((left % 3600) // 60)
        bot.send_message(m.chat.id, f"⏰ Депозит будет доступен через {h}ч {mm}мин")
        return
    
    amount = u['bank_deposit']
    win = int(amount * 1.04)
    u['money'] += win
    u['total_earned'] += win
    u['bank_deposit'] = 0
    u['bank_time'] = None
    save_all()
    bot.send_message(m.chat.id, f"🏦 *ДЕПОЗИТ ЗАБРАН!*\n\n💰 Ты вложил: {amount}💰\n📈 Получил: *{win}*💰\n💵 Баланс: {u['money']}", parse_mode='Markdown')

# ========== ЛОТЕРЕЯ ==========
def lotto_timer():
    while True:
        now = datetime.now()
        if now.hour == 19 and now.minute == 0 and not lotto_data.get('winner_today', False):
            lotto_data['tickets'] = {}
            lotto_data['winner_today'] = False
            tickets = lotto_data.get('tickets', {})
            if tickets:
                all_tickets = list(tickets.keys())
                random.shuffle(all_tickets)
                winners = all_tickets[:3] if len(all_tickets) >= 3 else all_tickets
                results = f"🎰 *РОЗЫГРЫШ ЛОТЕРЕИ* 🎰\n\n📅 {now.strftime('%d.%m.%Y')}\n🎫 Билетов: {len(all_tickets)}\n\n"
                for i, t in enumerate(winners, 1):
                    uid = tickets[t]
                    u = get_user(uid)
                    win = random.randint(1111, 2002)
                    u['money'] += win
                    u['total_earned'] += win
                    u['lotto_wins'] = u.get('lotto_wins', 0) + 1
                    results += f"{i}-е место: Билет №{t}\n👤 @{u['username']}\n💰 +{win}💰\n\n"
                    check_achievements(uid)
                    try:
                        bot.send_message(int(uid), f"🎉 *ТЫ ВЫИГРАЛ В ЛОТЕРЕЕ!* 🎉\n\n💰 +{win}💰\n💵 Баланс: {u['money']}", parse_mode='Markdown')
                    except: pass
                sent = set()
                for t, uid in tickets.items():
                    if uid not in sent:
                        try:
                            bot.send_message(int(uid), results, parse_mode='Markdown')
                            sent.add(uid)
                        except: pass
                for u in data.values():
                    u['lotto_ticket'] = None
            lotto_data['winner_today'] = True
            save_all()
        time.sleep(60)

threading.Thread(target=lotto_timer, daemon=True).start()

@bot.message_handler(func=lambda m: m.text and m.text.lower() in ['лотерея', 'билет'])
def lotto_buy(m):
    uid = m.from_user.id
    u = get_user(uid, m.from_user.username)
    now = datetime.now()
    if now.hour < 18 or now.hour >= 19:
        bot.send_message(m.chat.id, "🎰 *ЛОТЕРЕЯ* 🎰\n\n❌ Билеты продаются с 18:00 до 19:00 МСК\n🎲 Розыгрыш в 19:00", parse_mode='Markdown')
        return
    if u.get('lotto_ticket'):
        bot.send_message(m.chat.id, f"❌ У тебя уже есть билет №{u['lotto_ticket']}")
        return
    
    ticket = random.randint(8, 100)
    while str(ticket) in lotto_data.get('tickets', {}):
        ticket = random.randint(8, 100)
    u['lotto_ticket'] = ticket
    lotto_data['tickets'][str(ticket)] = uid
    save_all()
    bot.send_message(m.chat.id, f"🎫 *БИЛЕТ КУПЛЕН!*\n\n✅ Твой номер: *{ticket}*\n🎲 Розыгрыш сегодня в 19:00 МСК", parse_mode='Markdown')

# ========== СЛОТЫ С АНИМАЦИЕЙ ==========
@bot.message_handler(func=lambda m: m.text and m.text.lower() in ['слоты', 'слот'])
def slots_start(m):
    slot_waiting[m.from_user.id] = 'bet'
    bot.send_message(m.chat.id, "🎰 *СЛОТЫ* 🎰\n\n💰 Введи сумму ставки (мин 10):", parse_mode='Markdown')

@bot.message_handler(func=lambda m: m.from_user.id in slot_waiting)
def slots_play(m):
    uid = m.from_user.id
    del slot_waiting[uid]
    try:
        bet = int(m.text.strip())
        if bet < 10:
            bot.send_message(m.chat.id, "❌ Минимум 10💰")
            return
    except:
        bot.send_message(m.chat.id, "❌ Введи число!")
        return
    
    u = get_user(uid, m.from_user.username)
    if u['money'] < bet:
        bot.send_message(m.chat.id, f"❌ Не хватает {bet}💰")
        return
    
    u['money'] -= bet
    save_all()
    
    anim_msg = bot.send_message(m.chat.id, "🎰 *СЛОТЫ* 🎰\n\n🌀 | 🌀 | 🌀\n🌀 | 🌀 | 🌀\n🌀 | 🌀 | 🌀\n\n*КРУТИМ...*", parse_mode='Markdown')
    
    # 6 секунд анимации, обновление каждую секунду
    for step in range(6):
        time.sleep(1)
        temp_grid = [[random.choice(SLOT_SYMBOLS) for _ in range(3)] for _ in range(3)]
        display = f"┌───┬───┬───┐\n│ {temp_grid[0][0]} │ {temp_grid[0][1]} │ {temp_grid[0][2]} │\n├───┼───┼───┤\n│ {temp_grid[1][0]} │ {temp_grid[1][1]} │ {temp_grid[1][2]} │\n├───┼───┼───┤\n│ {temp_grid[2][0]} │ {temp_grid[2][1]} │ {temp_grid[2][2]} │\n└───┴───┴───┘"
        bot.edit_message_text(f"🎰 *СЛОТЫ* 🎰\n\n{display}\n\n*КРУТИМ...*", m.chat.id, anim_msg.message_id, parse_mode='Markdown')
    
    # Финальный результат
    grid = [[random.choice(SLOT_SYMBOLS) for _ in range(3)] for _ in range(3)]
    win = 0
    for line in SLOT_LINES:
        combo = (grid[line[0][0]][line[0][1]], grid[line[1][0]][line[1][1]], grid[line[2][0]][line[2][1]])
        for pay, mult in SLOT_PAYOUTS.items():
            if combo == pay:
                win += bet * mult
                break
    
    if win > 0:
        u['money'] += win
        u['total_earned'] += win
        u['slot_wins'] += 1
        add_exp(uid, win//4)
        result = f"✨ *ПОБЕДА!* ✨\n💰 +{win}💰"
    else:
        result = "💔 *ПРОИГРЫШ*"
    
    save_all()
    update_quest(uid, 'slot', 1)
    ach = check_achievements(uid)
    
    final_display = f"┌───┬───┬───┐\n│ {grid[0][0]} │ {grid[0][1]} │ {grid[0][2]} │\n├───┼───┼───┤\n│ {grid[1][0]} │ {grid[1][1]} │ {grid[1][2]} │\n├───┼───┼───┤\n│ {grid[2][0]} │ {grid[2][1]} │ {grid[2][2]} │\n└───┴───┴───┘"
    msg = f"🎰 *СЛОТЫ* 🎰\n\n{final_display}\n\n{result}\n💵 Баланс: {u['money']}"
    if ach: msg += ach
    bot.edit_message_text(msg, m.chat.id, anim_msg.message_id, parse_mode='Markdown')

# ========== РУЛЕТКА ==========
@bot.message_handler(func=lambda m: m.text and m.text.lower() in ['рулетка', 'рулетку'])
def roulette_menu(m):
    kb = telebot.types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        telebot.types.InlineKeyboardButton("🔴 КРАСНОЕ", callback_data='roul_red'),
        telebot.types.InlineKeyboardButton("⚫ ЧЕРНОЕ", callback_data='roul_black'),
        telebot.types.InlineKeyboardButton("🟢 ЗЕЛЕНЫЙ", callback_data='roul_green'),
        telebot.types.InlineKeyboardButton("📊 ЧЕТ", callback_data='roul_even'),
        telebot.types.InlineKeyboardButton("📊 НЕЧЕТ", callback_data='roul_odd'))
    bot.send_message(m.chat.id, "🎡 *РУЛЕТКА* 🎡\nВыбери тип ставки:", parse_mode='Markdown', reply_markup=kb)

@bot.callback_query_handler(func=lambda c: c.data.startswith('roul_'))
def roulette_bet(c):
    uid = c.from_user.id
    bet_type = c.data.split('_')[1]
    roulette_waiting[uid] = bet_type
    bot.edit_message_text("🎡 *РУЛЕТКА* 🎡\n\n💰 Введи сумму (мин 10):", c.message.chat.id, c.message.message_id, parse_mode='Markdown')
    bot.answer_callback_query(c.id)

@bot.message_handler(func=lambda m: m.from_user.id in roulette_waiting)
def roulette_amount(m):
    uid = m.from_user.id
    bet_type = roulette_waiting[uid]
    del roulette_waiting[uid]
    try:
        bet = int(m.text.strip())
        if bet < 10:
            bot.send_message(m.chat.id, "❌ Минимум 10💰")
            return
    except:
        bot.send_message(m.chat.id, "❌ Введи число!")
        return
    
    u = get_user(uid, m.from_user.username)
    if u['money'] < bet:
        bot.send_message(m.chat.id, f"❌ Не хватает {bet}💰")
        return
    
    u['money'] -= bet
    save_all()
    
    num = random.randint(0, 36)
    if num == 0: color, emoji = 'green', '🟢'
    elif num in [1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36]: color, emoji = 'red', '🔴'
    else: color, emoji = 'black', '⚫'
    
    win = 0
    if bet_type == 'red' and color == 'red': win = bet*2
    elif bet_type == 'black' and color == 'black': win = bet*2
    elif bet_type == 'green' and num == 0: win = bet*35
    elif bet_type == 'even' and num > 0 and num % 2 == 0: win = bet*2
    elif bet_type == 'odd' and num > 0 and num % 2 == 1: win = bet*2
    
    names = {'red':'КРАСНОЕ', 'black':'ЧЕРНОЕ', 'green':'ЗЕЛЕНЫЙ', 'even':'ЧЕТ', 'odd':'НЕЧЕТ'}
    
    if win > 0:
        u['money'] += win
        u['total_earned'] += win
        u['roulette_wins'] += 1
        add_exp(uid, win//4)
        msg = f"🎡 *РУЛЕТКА* 🎡\n\n🎲 {emoji} *{num}*\n🎯 {names[bet_type]} {bet}💰\n💰 *ВЫИГРЫШ: +{win}*💰\n💵 Баланс: {u['money']}"
        update_quest(uid, 'roulette_win', 1)
    else:
        msg = f"🎡 *РУЛЕТКА* 🎡\n\n🎲 {emoji} *{num}*\n🎯 {names[bet_type]} {bet}💰\n💔 *ПРОИГРЫШ*\n💵 Баланс: {u['money']}"
    
    save_all()
    ach = check_achievements(uid)
    if ach: msg += ach
    bot.send_message(m.chat.id, msg, parse_mode='Markdown')

# ========== СКАЧКИ ==========
def horse_race_event_loop(chat_id):
    global horse_race_events, horse_race_active, horse_race_thread_running
    horse_race_thread_running = True
    last = time.time()
    while horse_race_active:
        if time.time() - last >= 15 and random.randint(1,100) <= 40:
            horse = random.choice(HORSES)
            ev = random.choice([f"💥 {horse['name']} споткнулась!", f"🏇 {horse['name']} ускорилась!", f"🐎 {horse['name']} обошла соперника!", f"⚡ {horse['name']} набрала скорость!"])
            horse_race_events.append(ev)
            try: bot.send_message(chat_id, f"🏁 {ev}")
            except: pass
            last = time.time()
        time.sleep(1)
    horse_race_thread_running = False

def start_horse_race(chat_id):
    time.sleep(60)
    global horse_race_active, horse_race_bets, horse_race_events
    if not horse_race_active: return
    winner = random.choices([h['name'] for h in HORSES], weights=[h['chance'] for h in HORSES])[0]
    w_horse = next(h for h in HORSES if h['name'] == winner)
    res = f"🏁 *СКАЧКИ ЗАВЕРШЕНЫ!* 🏁\n\n🥇 ПОБЕДИТЕЛЬ: {w_horse['emoji']} {winner} (x{w_horse['coefficient']})\n\n"
    if horse_race_events:
        res += "📋 *СОБЫТИЯ:*\n" + "\n".join(horse_race_events[-5:]) + "\n\n"
    wins = []
    for hname, bd in horse_race_bets.items():
        if hname == winner:
            for bet in bd['bets']:
                u = get_user(bet['uid'])
                win_amt = int(bet['amount'] * w_horse['coefficient'])
                u['money'] += win_amt
                u['total_earned'] += win_amt
                u['bet_wins'] += 1
                add_exp(bet['uid'], win_amt//4)
                wins.append(f"✅ @{u['username']} +{win_amt}💰")
                update_quest(bet['uid'], 'bet_win', 1)
                update_quest(bet['uid'], 'bet', 1)
    if wins: res += "💰 *ВЫИГРЫШИ:*\n" + "\n".join(wins)
    else: res += "💔 НЕТ ВЫИГРЫШЕЙ"
    for hname, bd in horse_race_bets.items():
        try: bot.send_message(bd['chat_id'], res, parse_mode='Markdown')
        except: pass
    horse_race_active = False
    horse_race_bets = {}
    horse_race_events = []
    save_all()

@bot.message_handler(func=lambda m: m.text and m.text.lower() in ['скачки', 'ставка'])
def horse_menu(m):
    global horse_race_active, horse_race_bets, horse_race_events
    if horse_race_active:
        kb = telebot.types.InlineKeyboardMarkup(row_width=2)
        for h in HORSES:
            kb.add(telebot.types.InlineKeyboardButton(f"{h['emoji']} {h['name']} x{h['coefficient']}", callback_data=f'hrace_{h["name"]}'))
        bot.send_message(m.chat.id, "🏁 *СТАВКИ НА СКАЧКИ* 🏁\nВыбери лошадь:", parse_mode='Markdown', reply_markup=kb)
        return
    
    horse_race_active = True
    horse_race_bets = {}
    horse_race_events = []
    threading.Thread(target=start_horse_race, args=(m.chat.id,), daemon=True).start()
    threading.Thread(target=horse_race_event_loop, args=(m.chat.id,), daemon=True).start()
    msg = "🏁 *НОВЫЕ СКАЧКИ!* 🏁\n\n⏰ 1 минута на ставки!\n\n🐎 *УЧАСТНИКИ:*\n" + "\n".join([f"{h['emoji']} {h['name']} — x{h['coefficient']} (шанс {h['chance']}%)" for h in HORSES]) + "\n\n⏳ Скачки через 60 сек!\n📝 Делай ставку командой 'скачки'"
    bot.send_message(m.chat.id, msg, parse_mode='Markdown')

@bot.callback_query_handler(func=lambda c: c.data.startswith('hrace_'))
def horse_choose(c):
    uid = c.from_user.id
    hname = c.data.split('_')[1]
    bot.edit_message_text(f"🏁 СТАВКА НА {hname} 🏁\n\n💰 Введи сумму (мин 10):", c.message.chat.id, c.message.message_id)
    bot.answer_callback_query(c.id)
    slot_waiting[uid] = f'hr_{hname}'

@bot.message_handler(func=lambda m: m.from_user.id in slot_waiting and slot_waiting[m.from_user.id].startswith('hr_'))
def horse_bet(m):
    uid = m.from_user.id
    hname = slot_waiting[uid].replace('hr_', '')
    del slot_waiting[uid]
    try:
        amt = int(m.text.strip())
        if amt < 10:
            bot.send_message(m.chat.id, "❌ Минимум 10💰")
            return
    except:
        bot.send_message(m.chat.id, "❌ Введи число!")
        return
    u = get_user(uid, m.from_user.username)
    if u['money'] < amt:
        bot.send_message(m.chat.id, f"❌ Не хватает {amt}💰")
        return
    if not horse_race_active:
        bot.send_message(m.chat.id, "❌ Скачки уже начались!")
        return
    u['money'] -= amt
    if hname not in horse_race_bets:
        horse_race_bets[hname] = {'bets': [], 'chat_id': m.chat.id}
    horse_race_bets[hname]['bets'].append({'uid': uid, 'amount': amt})
    save_all()
    update_quest(uid, 'bet', 1)
    horse = next(h for h in HORSES if h['name'] == hname)
    bot.send_message(m.chat.id, f"✅ *СТАВКА ПРИНЯТА!*\n\n🐎 {horse['emoji']} {hname}\n💰 Сумма: {amt}💰\n📊 Коэф: x{horse['coefficient']}\n💵 Баланс: {u['money']}", parse_mode='Markdown')

# ========== ЗАПУСК ==========
print("=" * 50)
print("🔥 ХИТРЫЙ ЕВРЕЙ — ФИНАЛЬНАЯ ВЕРСИЯ 🔥")
print("🎰 СЛОТЫ — АНИМАЦИЯ 6 СЕКУНД")
print("💰 БАНК — 4% за 5 часов")
print("🛒 МАГАЗИН — КУПИТЬ 1-4")
print("🎡 РУЛЕТКА — КРАСНОЕ/ЧЕРНОЕ/ЗЕЛЕНЫЙ/ЧЕТ/НЕЧЕТ")
print("🐎 СКАЧКИ — 6 ЛОШАДЕЙ, СОБЫТИЯ")
print("🎫 ЛОТЕРЕЯ — 18:00-19:00 МСК")
print("🏆 АЧИВКИ — 20+ ШТУК")
print("=" * 50)

bot.infinity_polling()

