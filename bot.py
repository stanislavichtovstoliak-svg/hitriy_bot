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
BACKUP_FILE = 'users.json.backup'
LOTTO_FILE = 'lotto.json'

# ========== АЛМАЗНЫЕ СОХРАНЕНИЯ ==========
def safe_save(data, filename=DATA_FILE):
    try:
        temp_file = filename + '.tmp'
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        if os.path.exists(filename):
            shutil.copy2(filename, filename + '.backup')
        os.replace(temp_file, filename)
        return True
    except Exception as e:
        print(f"Ошибка сохранения: {e}")
        return False

def safe_load(filename=DATA_FILE, default={}):
    try:
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
    except:
        print(f"Файл {filename} поврежден, пробуем восстановить...")
        backup = filename + '.backup'
        if os.path.exists(backup):
            try:
                with open(backup, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    safe_save(data, filename)
                    print("Восстановление из бэкапа успешно!")
                    return data
            except:
                pass
    return default

data = safe_load()
save_data = lambda d: safe_save(d)

# ========== ДАННЫЕ ЛОТЕРЕИ ==========
def load_lotto():
    return safe_load(LOTTO_FILE, {'tickets': {}, 'last_draw': None, 'winner_today': False})

def save_lotto(lotto):
    safe_save(lotto, LOTTO_FILE)

lotto_data = load_lotto()

DEFAULT_USER = {
    'money': 500, 'level': 1, 'exp': 0, 'total_exp': 0,
    'last_work': None, 'username': None, 'total_earned': 0,
    'last_daily': None, 'daily_streak': 0, 'promos': [],
    'work_count': 0, 'slot_wins': 0, 'roulette_wins': 0,
    'bet_wins': 0, 'achievements': [], 'shop_buffs': {},
    'daily_quests': None, 'last_quest_reset': None,
    'lotto_ticket': None, 'lotto_wins': 0
}

# ========== ПРОФЕССИИ ==========
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

SHOP_ITEMS = {
    'speed': {'name': 'Ускорение работы', 'price': 500, 'duration': 3600, 'effect': 'work_cooldown', 'value': 300},
    'double_exp': {'name': 'Двойной опыт', 'price': 300, 'duration': 3600, 'effect': 'exp_multiplier', 'value': 2},
    'protection': {'name': 'Защита от неудач', 'price': 200, 'duration': 3, 'effect': 'no_fail', 'value': 3},
    'salary_boost': {'name': '+25% к зарплате', 'price': 400, 'duration': 86400, 'effect': 'salary_multiplier', 'value': 1.25},
}

ACHIEVEMENTS = {
    'work_10': {'name': "Трудоголик", 'reward': 100},
    'work_50': {'name': "Стахановец", 'reward': 500},
    'work_100': {'name': "Машина", 'reward': 1000},
    'work_500': {'name': "Терминатор", 'reward': 5000},
    'win_slot': {'name': "Счастливчик", 'reward': 50},
    'win_roulette': {'name': "Фортуна", 'reward': 50},
    'win_bet': {'name': "Лучший каппер", 'reward': 100},
    'quest_5': {'name': "Завсегдатай", 'reward': 200},
    'quest_25': {'name': "Мастер заданий", 'reward': 1000},
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
    'lotto_win': {'name': "Везунчик", 'reward': 500},
    'lotto_win_3': {'name': "Король лотереи", 'reward': 2000},
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

HORSES = [
    {"name": "МОЛНИЯ", "emoji": "🐎", "coefficient": 6.0, "chance": 10},
    {"name": "ВЕТЕР", "emoji": "🐎", "coefficient": 4.0, "chance": 15},
    {"name": "ГРОМ", "emoji": "🐎", "coefficient": 3.0, "chance": 20},
    {"name": "МОЛОТ", "emoji": "🐎", "coefficient": 2.5, "chance": 25},
    {"name": "СТРЕЛА", "emoji": "🐎", "coefficient": 2.0, "chance": 30},
    {"name": "ТИХОНЯ", "emoji": "🐎", "coefficient": 10.0, "chance": 5},
]

QUESTS = [
    {"name": "Счастливчик", "desc": "Сыграть в слоты 3 раза", "type": "slot", "target": 3, "reward": 200},
    {"name": "Фортуна", "desc": "Выиграть в рулетку 2 раза", "type": "roulette_win", "target": 2, "reward": 150},
    {"name": "Каппер", "desc": "Сделать 5 ставок на скачки", "type": "bet", "target": 5, "reward": 300},
    {"name": "Труженик", "desc": "Заработать 500 шекелей", "type": "earn", "target": 500, "reward": 200},
    {"name": "Работяга", "desc": "Поработать 10 раз", "type": "work", "target": 10, "reward": 250},
    {"name": "Победитель", "desc": "Выиграть в скачках 2 раза", "type": "bet_win", "target": 2, "reward": 350},
]

# ========== ПЕРЕМЕННЫЕ ==========
slot_waiting = {}
roulette_waiting = {}
horse_race_active = False
horse_race_bets = {}
horse_race_events = []

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

def reset_daily_quests(user_id):
    user = get_user(user_id)
    today = datetime.now().date().isoformat()
    
    if user.get('last_quest_reset') != today:
        selected = random.sample(QUESTS, 3)
        user['daily_quests'] = []
        for q in selected:
            user['daily_quests'].append({
                'name': q['name'], 'desc': q['desc'], 'type': q['type'],
                'target': q['target'], 'reward': q['reward'], 'progress': 0, 'completed': False
            })
        user['last_quest_reset'] = today
        save_data(data)

def update_quest_progress(user_id, quest_type, amount=1):
    user = get_user(user_id)
    reset_daily_quests(user_id)
    
    msg = ""
    for quest in user.get('daily_quests', []):
        if not quest['completed'] and quest['type'] == quest_type:
            quest['progress'] += amount
            if quest['progress'] >= quest['target']:
                quest['completed'] = True
                user['money'] += quest['reward']
                user['total_earned'] += quest['reward']
                msg += f"\n\n✅ ЗАДАНИЕ ВЫПОЛНЕНО: {quest['name']}\n💰 +{quest['reward']} шекелей!"
    
    if msg:
        save_data(data)
    return msg

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
    
    quest_count = sum(1 for q in user.get('daily_quests', []) if q.get('completed'))
    if quest_count >= 5 and 'quest_5' not in user['achievements']: new.append('quest_5')
    if quest_count >= 25 and 'quest_25' not in user['achievements']: new.append('quest_25')
    
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
    buff = user.get('shop_buffs', {}).get('double_exp')
    if buff and buff.get('active_until', 0) > time.time():
        amount = int(amount * 2)
    
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

def has_buff(uid, buff_type):
    user = get_user(uid)
    buff = user.get('shop_buffs', {}).get(buff_type)
    return buff and buff.get('active_until', 0) > time.time()

def use_buff(uid, buff_type):
    user = get_user(uid)
    if buff_type == 'no_fail':
        user['shop_buffs'][buff_type]['uses'] -= 1
        if user['shop_buffs'][buff_type]['uses'] <= 0:
            del user['shop_buffs'][buff_type]
    save_data(data)

def buy_buff(uid, item_key):
    user = get_user(uid)
    item = SHOP_ITEMS[item_key]
    
    if user['money'] < item['price']:
        return False, f"❌ Не хватает {item['price']} шекелей!"
    
    user['money'] -= item['price']
    
    if 'shop_buffs' not in user:
        user['shop_buffs'] = {}
    
    now = time.time()
    if item_key == 'protection':
        if item_key in user['shop_buffs']:
            user['shop_buffs'][item_key]['uses'] += item['value']
        else:
            user['shop_buffs'][item_key] = {'uses': item['value'], 'active_until': now + 86400}
    else:
        user['shop_buffs'][item_key] = {'active_until': now + item['duration']}
    
    save_data(data)
    return True, f"✅ {item['name']} куплен!"

# ========== ЛОТЕРЕЯ ==========
def generate_ticket_number():
    return random.randint(8, 100)

def check_lotto_status():
    now = datetime.now()
    current_time = now.time()
    
    # Прием билетов с 18:00 до 19:00
    ticket_start = datetime.strptime("18:00", "%H:%M").time()
    ticket_end = datetime.strptime("19:00", "%H:%M").time()
    
    is_ticket_time = ticket_start <= current_time < ticket_end
    can_buy = is_ticket_time and not lotto_data.get('winner_today', False)
    
    return can_buy, is_ticket_time, lotto_data.get('winner_today', False)

def reset_lotto_if_needed():
    today = datetime.now().date().isoformat()
    if lotto_data.get('last_draw') != today:
        lotto_data['tickets'] = {}
        lotto_data['last_draw'] = today
        lotto_data['winner_today'] = False
        save_lotto(lotto_data)

def draw_lotto():
    global lotto_data
    now = datetime.now()
    current_time = now.time()
    draw_time = datetime.strptime("19:00", "%H:%M").time()
    
    # Проверяем время розыгрыша (19:00)
    if current_time >= draw_time and not lotto_data.get('winner_today', False):
        tickets = lotto_data.get('tickets', {})
        
        if not tickets:
            lotto_data['winner_today'] = True
            save_lotto(lotto_data)
            return
        
        # Выбираем 3 случайных билета
        all_tickets = list(tickets.keys())
        random.shuffle(all_tickets)
        winners = all_tickets[:3] if len(all_tickets) >= 3 else all_tickets
        
        # Подсчитываем результаты
        results = f"🎰 РОЗЫГРЫШ ЛОТЕРЕИ 🎰\n\n"
        results += f"📅 Дата: {now.strftime('%d.%m.%Y')}\n"
        results += f"🎫 Всего билетов: {len(all_tickets)}\n\n"
        
        # Рассылаем выигрыши
        for i, ticket_num in enumerate(winners, 1):
            user_id = tickets[ticket_num]
            user = get_user(user_id)
            win_amount = random.randint(1111, 2002)
            user['money'] += win_amount
            user['total_earned'] += win_amount
            user['lotto_wins'] = user.get('lotto_wins', 0) + 1
            save_data(data)
            
            results += f"🥇 {i}-е МЕСТО: Билет №{ticket_num}\n"
            results += f"👤 Победитель: @{user['username']}\n"
            results += f"💰 Выигрыш: {win_amount} шекелей!\n\n"
            
            # Отправляем личное сообщение победителю
            try:
                bot.send_message(int(user_id), 
                    f"🎉 ПОЗДРАВЛЯЮ! 🎉\n\n"
                    f"Твой билет №{ticket_num} выиграл в лотерее!\n"
                    f"💰 Выигрыш: {win_amount} шекелей!\n"
                    f"💵 Новый баланс: {user['money']}")
            except:
                pass
            
            check_achievements(user_id)
        
        if len(winners) < 3:
            results += f"❌ Недостаточно участников для 3 победителей\n"
        
        results += f"\n🎲 Следующий розыгрыш завтра в 19:00 МСК!\n"
        results += f"🎫 Билеты можно купить с 18:00 до 19:00 МСК"
        
        # Рассылаем результаты всем, у кого были билеты
        sent_users = set()
        for ticket_num, user_id in tickets.items():
            if user_id not in sent_users:
                try:
                    bot.send_message(int(user_id), results)
                    sent_users.add(user_id)
                except:
                    pass
        
        lotto_data['winner_today'] = True
        save_lotto(lotto_data)
        
        # Очищаем билеты
        for uid in data:
            if data[uid].get('lotto_ticket'):
                data[uid]['lotto_ticket'] = None
        save_data(data)

@bot.message_handler(func=lambda m: m.text and m.text.lower() in ['лотерея', 'билет', 'купить билет'])
def lotto_cmd(message):
    uid = message.from_user.id
    user = get_user(uid, message.from_user.username)
    
    reset_lotto_if_needed()
    can_buy, is_ticket_time, winner_today = check_lotto_status()
    
    if winner_today:
        bot.send_message(message.chat.id, 
            "🎰 ЛОТЕРЕЯ 🎰\n\n"
            "❌ Розыгрыш сегодня уже прошел!\n"
            "🎫 Следующий розыгрыш завтра в 19:00 МСК\n"
            "⏰ Билеты можно купить с 18:00 до 19:00 МСК")
        return
    
    if not is_ticket_time:
        bot.send_message(message.chat.id, 
            "🎰 ЛОТЕРЕЯ 🎰\n\n"
            "❌ Сейчас нельзя купить билет!\n"
            "⏰ Время приема билетов: с 18:00 до 19:00 МСК\n"
            "🎲 Розыгрыш в 19:00 МСК")
        return
    
    if user.get('lotto_ticket'):
        bot.send_message(message.chat.id, 
            f"🎰 ЛОТЕРЕЯ 🎰\n\n"
            f"❌ У тебя уже есть билет №{user['lotto_ticket']}!\n"
            f"🎲 Жди розыгрыша в 19:00 МСК!")
        return
    
    ticket = generate_ticket_number()
    while str(ticket) in lotto_data.get('tickets', {}):
        ticket = generate_ticket_number()
    
    user['lotto_ticket'] = ticket
    lotto_data['tickets'][str(ticket)] = uid
    save_lotto(lotto_data)
    save_data(data)
    
    bot.send_message(message.chat.id, 
        f"🎰 ЛОТЕРЕЯ 🎰\n\n"
        f"✅ Твой билет №{ticket}!\n"
        f"🎲 Розыгрыш сегодня в 19:00 МСК\n"
        f"🏆 3 победителя получат призы от 1111 до 2002 шекелей!\n\n"
        f"💫 Удачи!")

# ========== ФОН ТАЙМЕР ДЛЯ ЛОТЕРЕИ ==========
def lotto_timer():
    while True:
        try:
            now = datetime.now()
            # Проверяем розыгрыш каждую минуту в 19:00
            if now.hour == 19 and now.minute == 0:
                reset_lotto_if_needed()
                draw_lotto()
            time.sleep(60)
        except:
            time.sleep(60)

# Запускаем поток лотереи
lotto_thread = threading.Thread(target=lotto_timer, daemon=True)
lotto_thread.start()

# ========== КОМАНДЫ ==========

@bot.message_handler(commands=['start'])
def start_cmd(message):
    uid = message.from_user.id
    user = get_user(uid, message.from_user.username)
    level_info = get_level_info(user['level'])
    reset_daily_quests(uid)
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
    msg += f"• скачки - сделать ставку на скачки\n"
    msg += f"• лотерея / билет - купить билет (с 18:00 до 19:00 МСК)\n\n"
    msg += f"--- ЗАРАБОТОК ---\n"
    msg += f"• работа - работа (КД 10 мин)\n"
    msg += f"• бонус - ежедневный (КД 12 ч)\n\n"
    msg += f"--- МАГАЗИН ---\n"
    msg += f"• магазин - посмотреть товары\n"
    msg += f"• купить [товар] - купить улучшение\n\n"
    msg += f"--- ЗАДАНИЯ ---\n"
    msg += f"• задания - посмотреть ежедневные задания\n\n"
    msg += f"--- ИНФО ---\n"
    msg += f"• баланс - проверить деньги\n"
    msg += f"• профиль - статистика\n"
    msg += f"• топ - топ богатых\n"
    msg += f"• достижения - список ачивок"
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
    uid = message.from_user.id
    user = get_user(uid, message.from_user.username)
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
    
    buffs = ""
    now = time.time()
    for key, buff in user.get('shop_buffs', {}).items():
        if key == 'speed' and buff.get('active_until', 0) > now:
            buffs += f"\n⚡ Ускорение работы (ещё {int((buff['active_until']-now)/60)} мин)"
        elif key == 'double_exp' and buff.get('active_until', 0) > now:
            buffs += f"\n⭐ Двойной опыт (ещё {int((buff['active_until']-now)/60)} мин)"
        elif key == 'salary_boost' and buff.get('active_until', 0) > now:
            buffs += f"\n📈 +25% зарплаты (ещё {int((buff['active_until']-now)/3600)} ч)"
        elif key == 'protection' and buff.get('uses', 0) > 0:
            buffs += f"\n🛡️ Защита от неудач (осталось {buff['uses']} раз)"
    
    msg = f"📊 ПРОФИЛЬ 📊\n\n"
    msg += f"👤 @{user.get('username') or 'Нет имени'}\n"
    msg += f"🏆 Уровень {user['level']} - {level_info['name']}\n"
    msg += f"💰 Денег: {user['money']}\n"
    msg += f"⭐ Опыт: {user['exp']}\n"
    msg += f"📈 Всего заработал: {user['total_earned']}\n"
    msg += f"🎁 Серия бонусов: {user.get('daily_streak', 0)}\n"
    msg += f"📦 Работ выполнено: {user.get('work_count', 0)}\n"
    msg += f"🏆 Достижений: {len(user.get('achievements', []))}\n"
    msg += f"🎫 Билет лотереи: {user.get('lotto_ticket', 'Нет')}"
    if buffs:
        msg += f"\n✨ АКТИВНЫЕ БАФФЫ:{buffs}"
    msg += f"\n\n🎲 *ЛОТЕРЕЯ*\n⏰ Розыгрыш каждый день в 19:00 МСК!\n🎫 Билеты можно купить с 18:00 до 19:00 МСК"
    
    if left > 0:
        msg += f"\n\n📊 До {next_lvl} уровня:\n{bar} {prog}%\nОсталось: {left} опыта"
    bot.send_message(message.chat.id, msg, parse_mode='Markdown')

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
    
    cooldown = 300 if has_buff(uid, 'speed') else 600
    
    if user['last_work']:
        last = datetime.fromisoformat(user['last_work'])
        diff = (datetime.now() - last).total_seconds()
        if diff < cooldown:
            rem = int(cooldown - diff)
            m, s = rem // 60, rem % 60
            bot.send_message(message.chat.id, f"⏰ Отдыхай {m} мин {s} сек")
            return
    
    base = random.randint(level_info['salary_min'], level_info['salary_max'])
    
    if has_buff(uid, 'salary_boost'):
        base = int(base * 1.25)
    
    fail = random.randint(1, 100) <= 5
    
    if has_buff(uid, 'no_fail') and fail:
        fail = False
        use_buff(uid, 'no_fail')
        bot.send_message(message.chat.id, "🛡️ Защита от неудач сработала!")
    
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
    
    quest_msg = update_quest_progress(uid, 'work', 1)
    quest_msg += update_quest_progress(uid, 'earn', base)
    if quest_msg:
        msg += quest_msg
    
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

@bot.message_handler(func=lambda m: m.text and m.text.lower() in ['магазин', 'shop'])
def shop_cmd(message):
    msg = f"🛒 МАГАЗИН 🛒\n\n"
    for key, item in SHOP_ITEMS.items():
        msg += f"• {item['name']} - {item['price']}💰\n"
    msg += f"\n💡 Напиши 'купить [название]'"
    bot.send_message(message.chat.id, msg)

@bot.message_handler(func=lambda m: m.text and m.text.lower().startswith('купить'))
def buy_cmd(message):
    uid = message.from_user.id
    item_name = message.text.lower().replace('купить', '').strip()
    
    item_key = None
    for key, item in SHOP_ITEMS.items():
        if item['name'].lower() in item_name:
            item_key = key
            break
    
    if not item_key:
        bot.send_message(message.chat.id, f"❌ Товар '{item_name}' не найден!\nНапиши 'магазин' для списка")
        return
    
    success, msg = buy_buff(uid, item_key)
    bot.send_message(message.chat.id, msg)

@bot.message_handler(func=lambda m: m.text and m.text.lower() in ['задания', 'ежедневные', 'quest', 'квесты'])
def quests_cmd(message):
    uid = message.from_user.id
    reset_daily_quests(uid)
    user = get_user(uid)
    
    msg = f"📋 ЕЖЕДНЕВНЫЕ ЗАДАНИЯ 📋\n\n"
    for quest in user.get('daily_quests', []):
        if quest['completed']:
            msg += f"✅ {quest['name']} - {quest['desc']} (ВЫПОЛНЕНО)\n"
        else:
            msg += f"❌ {quest['name']} - {quest['desc']} ({quest['progress']}/{quest['target']}) +{quest['reward']}💰\n"
    
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
            bot.send_message(message.chat.id, "❌ Минимальная ставка 10 шекелей!")
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
        update_quest_progress(uid, 'slot', 1)
    
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
        update_quest_progress(uid, 'roulette_win', 1)
        msg = f"🎡 РУЛЕТКА 🎡\n\n🎲 {emoji} {num}\n🎯 {names[bet_type]} {bet}\n💰 ВЫИГРЫШ: +{win}\n💵 Баланс: {user['money']}"
    else:
        msg = f"🎡 РУЛЕТКА 🎡\n\n🎲 {emoji} {num}\n🎯 {names[bet_type]} {bet}\n💔 ПРОИГРЫШ\n💵 Баланс: {user['money']}"
    
    save_data(data)
    ach = check_achievements(uid)
    if ach:
        msg += ach
    bot.send_message(message.chat.id, msg)
    del roulette_waiting[uid]

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
                update_quest_progress(uid, 'bet_win', 1)
                update_quest_progress(uid, 'bet', 1)
    
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
                    f"💥 {horse['name']} споткнулась!",
                    f"🏇 {horse['name']} ускорилась!",
                    f"🐎 {horse['name']} обошла соперника!",
                    f"⚡ {horse['name']} набрала скорость!",
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
    
    horse = next((h for h in HORSES if h['name'] == horse_name), None)
    
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
    
    update_quest_progress(uid, 'bet', 1)
    
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
print("АЛМАЗНЫЕ СОХРАНЕНИЯ - активны!")
print("МАГАЗИН - работает!")
print("ЕЖЕДНЕВНЫЕ ЗАДАНИЯ - работают!")
print("ЛОТЕРЕЯ - каждый день в 18:00-19:00 МСК!")
print("12 УРОВНЕЙ ПРОФЕССИЙ!")
print("СЛОТЫ - работают")
print("РУЛЕТКА - работает")
print("СКАЧКИ - работают")
print("=" * 50)

bot.infinity_polling()


