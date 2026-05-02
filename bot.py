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
slot_games = {}
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
    "Грузчик": [
        "💥 Уронил ящик с помидорами! Штраф {} шекелей!",
        "📦 Споткнулся и разбил дорогую вазу! -{} шекелей!",
        "🔨 Неправильно закрепил груз - штраф {} шекелей!"
    ],
    "Курьер": [
        "🛵 Проткнул колесо о гвоздь! Штраф {} шекелей!",
        "📬 Потерял посылку по пути! -{} шекелей!",
        "💨 Опоздал к клиенту на 5 минут! Штраф {} шекелей!"
    ],
    "Автомеханик": [
        "🔧 Перетянул болт и сорвал резьбу! Штраф {} шекелей!",
        "⚡ Забыл затянуть колесо - вылетело на дороге! -{} шекелей!",
        "🛢 Залил не то масло в двигатель! Штраф {} шекелей!"
    ],
    "Кладовщик": [
        "📦 Перепутал товар при отгрузке! Штраф {} шекелей!",
        "🏷 Потерял накладную на товар! -{} шекелей!",
        "💻 Неправильно внес данные в систему! Штраф {} шекелей!"
    ],
    "Менеджер": [
        "📞 Поссорился с важным клиентом! Штраф {} шекелей!",
        "💼 Провалил презентацию проекта! -{} шекелей!",
        "📉 Неправильно рассчитал бюджет! Штраф {} шекелей!"
    ],
    "Бухгалтер": [
        "📊 Ошибся в годовой отчетности! Штраф {} шекелей!",
        "🧾 Потерял важные чеки для налоговой! -{} шекелей!",
        "💰 Неправильно начислил зарплаты сотрудникам! Штраф {} шекелей!"
    ],
    "Директор": [
        "🏢 Неудачная сделка с партнерами! Штраф {} шекелей!",
        "📉 Акции компании упали в цене! -{} шекелей!",
        "🤝 Подписал невыгодный контракт! Штраф {} шекелей!"
    ],
    "Магнат": [
        "💎 Инвестиция в криптовалюту провалилась! Штраф {} шекелей!",
        "🏭 Завод встал на простой из-за поломки! -{} шекелей!",
        "📈 Фондовый рынок обвалился! Штраф {} шекелей!"
    ]
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
            'money': 500,
            'level': 1,
            'exp': 0,
            'total_exp': 0,
            'last_work': None,
            'username': username,
            'total_earned': 0,
            'last_daily': None,
            'daily_streak': 0,
            'promos': []
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
    top_list = []
    for uid, u in data.items():
        name = u.get('username', 'Игрок')
        top_list.append((name, u['money']))
    top_list.sort(key=lambda x: x[1], reverse=True)
    return top_list[:10]

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
        f"📝 Напиши 'команды' чтобы увидеть все команды!\n\n"
        f"🎲 Удачи!")

@bot.message_handler(func=lambda m: m.text and m.text.lower() == 'команды')
def show_commands(message):
    msg = f"📋 СПИСОК КОМАНД 📋\n\n"
    msg += f"--- ИГРЫ ---\n"
    msg += f"• рулетка - игра в рулетку\n"
    msg += f"• слоты - игра в слоты 3x3\n"
    msg += f"• блекджек - игра в 21\n"
    msg += f"• дуэль @username сумма - вызвать на дуэль\n\n"
    msg += f"--- ЗАРАБОТОК ---\n"
    msg += f"• работа / фарм - заработать (КД 10 мин)\n"
    msg += f"  (5% шанс на провал со штрафом)\n"
    msg += f"• бонус / ежедневный - бонус (КД 12 ч)\n\n"
    msg += f"--- ИНФОРМАЦИЯ ---\n"
    msg += f"• баланс / деньги - проверить баланс\n"
    msg += f"• профиль / стата - твоя статистика\n"
    msg += f"• топ / лидеры - топ богатых игроков\n\n"
    msg += f"--- ПРОМОКОДЫ ---\n"
    msg += f"• #промо код - активировать промокод\n"
    msg += f"Доступные промокоды:\n"
    msg += f"  - шепельпрезидент (2000 шекелей)\n"
    msg += f"  - тест (2 шекеля)\n"
    msg += f"  - куниза200шекелей (199 шекелей)\n"
    msg += f"  - ялюблюгрибы (666 шекелей)\n\n"
    msg += f"--- ДУЭЛИ ---\n"
    msg += f"Пример: дуэль @vovan 100\n"
    msg += f"Победитель забирает ставку x2"
    
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
    
    base_earned = random.randint(level_info['salary_min'], level_info['salary_max'])
    fail_chance = random.randint(1, 100)
    failed = fail_chance <= 5
    
    if failed:
        penalty_percent = random.randint(30, 70)
        penalty = int(base_earned * penalty_percent / 100)
        earned = -penalty
        user['money'] += earned
        user['total_earned'] += earned
        
        messages = FAIL_MESSAGES.get(level_info['name'], ["Работа не заладилась! Штраф {} шекелей!"])
        fail_text = random.choice(messages)
        
        msg = f"😫 НЕУДАЧА НА РАБОТЕ!\n\n"
        msg += f"💼 {level_info['name']}\n"
        msg += f"{fail_text.format(penalty)}\n"
    else:
        earned = base_earned
        user['money'] += earned
        user['total_earned'] += earned
        msg = f"🌾 ТЫ ПОРАБОТАЛ! 🌾\n\n"
        msg += f"💼 {level_info['name']}\n"
        msg += f"💰 +{earned} шекелей\n"
    
    user['last_work'] = datetime.now().isoformat()
    exp_earned = abs(earned) // 2 if earned > 0 else abs(earned) // 4
    
    if earned > 0:
        leveled = add_exp(uid, exp_earned)
        msg += f"\n⭐ +{exp_earned} опыта"
    else:
        leveled = add_exp(uid, -exp_earned)
        msg += f"\n😭 -{exp_earned} опыта (штраф)"
    
    msg += f"\n💵 Баланс: {user['money']} шекелей"
    
    if leveled and earned > 0:
        new_level = get_level_info(user['level'])
        msg += f"\n\n🎉 НОВЫЙ УРОВЕНЬ! 🎉\nТеперь ты {user['level']} - {new_level['name']}"
    
    save_data()
    bot.send_message(message.chat.id, msg)

@bot.message_handler(func=lambda m: m.text and m.text.lower() in ['баланс', 'деньги'])
def balance_cmd(message):
    uid = message.from_user.id
    user = get_user(uid, message.from_user.username)
    level_info = get_level_info(user['level'])
    bot.send_message(message.chat.id,
        f"💰 ТВОЙ БАЛАНС 💰\n\n"
        f"💵 Денег: {user['money']} шекелей\n"
        f"📊 Уровень: {user['level']} - {level_info['name']}\n"
        f"⭐ Опыт: {user['exp']}\n"
        f"📈 Всего заработал: {user['total_earned']}")

@bot.message_handler(func=lambda m: m.text and m.text.lower() in ['профиль', 'стата'])
def profile_cmd(message):
    uid = message.from_user.id
    user = get_user(uid, message.from_user.username)
    level_info = get_level_info(user['level'])
    
    next_level = user['level'] + 1
    if next_level <= 8:
        need = LEVELS[next_level]['exp_needed']
        have = user['total_exp']
        left = need - have
        prog = int((have / need) * 100) if need > 0 else 100
        prog_bar = '▓' * (prog // 10) + '░' * (10 - (prog // 10))
    else:
        left = 0
        prog = 100
        prog_bar = '▓▓▓▓▓▓▓▓▓▓'
    
    msg = f"📊 ТВОЙ ПРОФИЛЬ 📊\n\n"
    msg += f"👤 Игрок: @{user.get('username') or 'Нет имени'}\n"
    msg += f"🏆 Уровень: {user['level']} - {level_info['name']}\n"
    msg += f"💰 Денег: {user['money']} шекелей\n"
    msg += f"⭐ Опыт: {user['exp']}\n"
    msg += f"📈 Всего заработал: {user['total_earned']}\n"
    msg += f"🎁 Серия бонусов: {user.get('daily_streak', 0)} дней"
    
    if left > 0:
        msg += f"\n\n📊 До {next_level} уровня:\n{prog_bar} {prog}%\nОсталось: {left} опыта"
    
    bot.send_message(message.chat.id, msg)

@bot.message_handler(func=lambda m: m.text and m.text.lower() in ['топ', 'топ10', 'лидеры'])
def top_cmd(message):
    top = get_top()
    if not top:
        bot.send_message(message.chat.id, "🏆 Топ пока пуст!")
        return
    msg = "🏆 ТОП БОГАТЫХ ИГРОКОВ 🏆\n\n"
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

@bot.message_handler(func=lambda m: m.text and m.text.lower() in ['бонус', 'ежедневный', 'daily'])
def daily_cmd(message):
    uid = message.from_user.id
    user = get_user(uid, message.from_user.username)
    
    if user.get('last_daily'):
        last = datetime.fromisoformat(user['last_daily'])
        diff = (datetime.now() - last).total_seconds()
        if diff < 43200:
            hours = int((43200 - diff) // 3600)
            minutes = int(((43200 - diff) % 3600) // 60)
            bot.send_message(message.chat.id, f"🎁 Бонус через {hours} ч {minutes} мин\n🔥 Серия: {user.get('daily_streak', 0)}")
            return
    
    bonus = random.randint(50, 200)
    user['money'] += bonus
    user['total_earned'] += bonus
    user['last_daily'] = datetime.now().isoformat()
    user['daily_streak'] = user.get('daily_streak', 0) + 1
    exp_gained = bonus // 3
    leveled = add_exp(uid, exp_gained)
    
    msg = f"🎁 ЕЖЕДНЕВНЫЙ БОНУС 🎁\n\n💰 +{bonus} шекелей\n⭐ +{exp_gained} опыта\n🔥 Серия: {user['daily_streak']} дней\n💵 Баланс: {user['money']}"
    if leveled:
        new_level = get_level_info(user['level'])
        msg += f"\n\n🎉 НОВЫЙ УРОВЕНЬ! 🎉\nТеперь ты {user['level']} - {new_level['name']}"
    
    save_data()
    bot.send_message(message.chat.id, msg)

@bot.message_handler(func=lambda m: m.text and m.text.lower().startswith('#промо'))
def promo_cmd(message):
    uid = message.from_user.id
    user = get_user(uid, message.from_user.username)
    promo_text = message.text.lower().replace('#промо', '').strip()
    
    if promo_text in user.get('promos', []):
        bot.send_message(message.chat.id, f"❌ Ты уже использовал промокод {promo_text}!")
        return
    
    if promo_text in PROMOCODES:
        promo = PROMOCODES[promo_text]
        user['money'] += promo['money']
        user['total_earned'] += promo['money']
        user['promos'].append(promo_text)
        leveled = add_exp(uid, promo['exp'])
        
        msg = f"🎁 ПРОМОКОД АКТИВИРОВАН! 🎁\n\n✅ {promo_text}\n💰 +{promo['money']} шекелей\n⭐ +{promo['exp']} опыта\n💵 Баланс: {user['money']}"
        if leveled:
            new_level = get_level_info(user['level'])
            msg += f"\n\n🎉 НОВЫЙ УРОВЕНЬ! 🎉\nТеперь ты {user['level']} - {new_level['name']}"
        
        save_data()
        bot.send_message(message.chat.id, msg)
    else:
        bot.send_message(message.chat.id, f"❌ Промокод {promo_text} не найден!")

# ========== ДУЭЛИ ==========

@bot.message_handler(func=lambda m: m.text and m.text.lower().startswith('дуэль'))
def duel_command(message):
    uid = message.from_user.id
    user = get_user(uid, message.from_user.username)
    
    parts = message.text.split()
    if len(parts) < 3:
        bot.send_message(message.chat.id, "❌ Используй: дуэль @username сумма\nПример: дуэль @vanya 100")
        return
    
    target = parts[1]
    if not target.startswith('@'):
        target = '@' + target
    
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
    
    target_name = target.replace('@', '')
    target_uid = None
    for uid_check, u in data.items():
        if u.get('username') == target_name:
            target_uid = uid_check
            break
    
    if not target_uid:
        bot.send_message(message.chat.id, f"❌ Игрок {target} не найден!")
        return
    
    if str(target_uid) == str(uid):
        bot.send_message(message.chat.id, "❌ Нельзя дуэлиться с самим собой!")
        return
    
    target_user = get_user(target_uid)
    
    if target_user['money'] < bet:
        bot.send_message(message.chat.id, f"❌ У {target} не хватает {bet} шекелей!")
        return
    
    duel_id = str(int(time.time()))
    duels[duel_id] = {
        'player1': uid,
        'player2': target_uid,
        'bet': bet,
        'status': 'waiting',
        'chat_id': message.chat.id
    }
    
    user['money'] -= bet
    target_user['money'] -= bet
    save_data()
    
    kb = telebot.types.InlineKeyboardMarkup()
    kb.add(
        telebot.types.InlineKeyboardButton("✅ ПРИНЯТЬ", callback_data=f'duel_accept_{duel_id}'),
        telebot.types.InlineKeyboardButton("❌ ОТКАЗАТЬ", callback_data=f'duel_decline_{duel_id}')
    )
    
    bot.send_message(message.chat.id, 
        f"🥊 ДУЭЛЬ 🥊\n\n"
        f"👤 @{message.from_user.username} вызывает @{target_name}!\n"
        f"💰 Ставка: {bet} шекелей\n\n"
        f"У обоих списано {bet} шекелей.\n"
        f"Победитель забирает {bet * 2}!",
        reply_markup=kb)
    
    try:
        bot.send_message(int(target_uid), 
            f"🥊 ВЫЗОВ НА ДУЭЛЬ! 🥊\n\n"
            f"@{message.from_user.username} вызвал тебя!\n"
            f"💰 Ставка: {bet} шекелей\n\n"
            f"Нажми кнопку в группе!")
    except:
        pass

@bot.callback_query_handler(func=lambda call: call.data.startswith('duel_'))
def duel_callback(call):
    action, duel_id = call.data.split('_')[1], call.data.split('_')[2]
    uid = call.from_user.id
    duel = duels.get(duel_id)
    
    if not duel:
        bot.answer_callback_query(call.id, "❌ Дуэль не найдена!", show_alert=True)
        return
    
    if action == 'accept':
        if uid != duel['player2']:
            bot.answer_callback_query(call.id, "❌ Это не твоя дуэль!", show_alert=True)
            return
        
        if duel['status'] != 'waiting':
            bot.answer_callback_query(call.id, "❌ Дуэль уже завершена!", show_alert=True)
            return
        
        duel['status'] = 'active'
        duels[duel_id] = duel
        
        player1 = get_user(duel['player1'])
        player2 = get_user(duel['player2'])
        
        roll1 = random.randint(1, 6)
        roll2 = random.randint(1, 6)
        
        msg = f"🎲 РЕЗУЛЬТАТ ДУЭЛИ 🎲\n\n"
        msg += f"🥊 @{player1['username']} vs @{player2['username']}\n"
        msg += f"💰 Ставка: {duel['bet']} шекелей\n\n"
        msg += f"🎲 @{player1['username']} выбросил: {roll1}\n"
        msg += f"🎲 @{player2['username']} выбросил: {roll2}\n\n"
        
        if roll1 > roll2:
            player1['money'] += duel['bet'] * 2
            msg += f"🏆 ПОБЕДИТЕЛЬ: @{player1['username']} 🏆\n"
            msg += f"💰 Выигрыш: +{duel['bet'] * 2} шекелей!"
        elif roll2 > roll1:
            player2['money'] += duel['bet'] * 2
            msg += f"🏆 ПОБЕДИТЕЛЬ: @{player2['username']} 🏆\n"
            msg += f"💰 Выигрыш: +{duel['bet'] * 2} шекелей!"
        else:
            player1['money'] += duel['bet']
            player2['money'] += duel['bet']
            msg += f"🤝 НИЧЬЯ! 🤝\n"
            msg += f"💰 Деньги возвращены обоим!"
        
        save_data()
        bot.edit_message_text(msg, duel['chat_id'], call.message.message_id)
        bot.answer_callback_query(call.id, "✅ Дуэль принята!", show_alert=True)
        del duels[duel_id]
        
    elif action == 'decline':
        if uid != duel['player2']:
            bot.answer_callback_query(call.id, "❌ Это не твоя дуэль!", show_alert=True)
            return
        
        if duel['status'] != 'waiting':
            bot.answer_callback_query(call.id, "❌ Дуэль уже завершена!", show_alert=True)
            return
        
        player1 = get_user(duel['player1'])
        player2 = get_user(duel['player2'])
        player1['money'] += duel['bet']
        player2['money'] += duel['bet']
        save_data()
        
        bot.edit_message_text(f"❌ @{player2['username']} отказался от дуэли!\n💰 Деньги возвращены.", 
                              duel['chat_id'], call.message.message_id)
        bot.answer_callback_query(call.id, "❌ Ты отказался!", show_alert=True)
        del duels[duel_id]

# ========== СЛОТЫ 3x3 ==========

@bot.message_handler(func=lambda m: m.text and m.text.lower() in ['слоты', 'слот', 'казик'])
def slots_menu_cmd(message):
    uid = message.from_user.id
    slot_games[uid] = True
    kb = telebot.types.InlineKeyboardMarkup(row_width=3)
    kb.add(
        telebot.types.InlineKeyboardButton("10", callback_data='slot_10'),
        telebot.types.InlineKeyboardButton("50", callback_data='slot_50'),
        telebot.types.InlineKeyboardButton("100", callback_data='slot_100')
    )
    bot.send_message(message.chat.id, "🎰 ВЫБЕРИ СТАВКУ:", reply_markup=kb)

@bot.callback_query_handler(func=lambda call: call.data.startswith('slot_'))
def slots_play_callback(call):
    uid = call.from_user.id
    if uid not in slot_games:
        bot.answer_callback_query(call.id, "❌ Нажми 'Слоты' сначала!", show_alert=True)
        return
    bet = int(call.data.split('_')[1])
    user = get_user(uid, call.from_user.username)
    if user['money'] < bet:
        bot.answer_callback_query(call.id, f"❌ Не хватает {bet}!", show_alert=True)
        del slot_games[uid]
        return
    user['money'] -= bet
    icons = ['🍒', '🍊', '🍋', '🍉', '🍇', '💰', '💎', '🎰', '7']
    grid = [[random.choice(icons) for _ in range(3)] for _ in range(3)]
    win = 0
    if grid[0][0] == grid[1][1] == grid[2][2]:
        win = bet * 3
    if grid[0][2] == grid[1][1] == grid[2][0]:
        win = bet * 3
    for row in grid:
        if row[0] == row[1] == row[2]:
            if row[0] in ['7', '🎰']:
                win = max(win, bet * 10)
            elif row[0] in ['💰', '💎']:
                win = max(win, bet * 5)
            else:
                win = max(win, bet * 2)
    for col in range(3):
        if grid[0][col] == grid[1][col] == grid[2][col]:
            if grid[0][col] in ['7', '🎰']:
                win = max(win, bet * 10)
            elif grid[0][col] in ['💰', '💎']:
                win = max(win, bet * 5)
            else:
                win = max(win, bet * 2)
    display = ""
    for row in grid:
        display += f"│ {row[0]} │ {row[1]} │ {row[2]} │\n"
    if win > 0:
        user['money'] += win
        user['total_earned'] += win
        add_exp(uid, win // 4)
        result = f"✨ ПОБЕДА! ✨\n💰 +{win} шекелей!"
    else:
        result = f"💔 ПРОИГРЫШ"
    save_data()
    msg = f"🎰 СЛОТЫ 3x3 🎰\n\n{display}\n{result}\n💵 Баланс: {user['money']}"
    try:
        bot.edit_message_text(msg, call.message.chat.id, call.message.message_id)
    except:
        bot.send_message(call.message.chat.id, msg)
    bot.answer_callback_query(call.id)
    del slot_games[uid]

# ========== РУЛЕТКА ==========

@bot.message_handler(func=lambda m: m.text and m.text.lower() in ['рулетка', 'рулетку'])
def roulette_menu_cmd(message):
    uid = message.from_user.id
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
    bot.send_message(message.chat.id, "🎡 РУЛЕТКА 🎡\n\nВыбери тип ставки:", reply_markup=kb)

@bot.callback_query_handler(func=lambda call: call.data.startswith('roulette_'))
def roulette_bet_callback(call):
    uid = call.from_user.id
    bet_type = call.data.split('_')[1]
    roulette_waiting[uid] = bet_type
    bot.edit_message_text("🎡 РУЛЕТКА 🎡\n\n💰 Введи сумму (мин 10):", call.message.chat.id, call.message.message_id)
    bot.answer_callback_query(call.id)

@bot.message_handler(func=lambda m: m.from_user.id in roulette_waiting)
def roulette_bet_amount(message):
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
        color = 'green'
        color_emoji = '🟢'
    elif num in [1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36]:
        color = 'red'
        color_emoji = '🔴'
    else:
        color = 'black'
        color_emoji = '⚫'
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
    bet_names = {'red': '🔴 КРАСНОЕ', 'black': '⚫ ЧЕРНОЕ', 'green': '🟢 ЗЕЛЕНЫЙ', 'even': '📊 ЧЕТ', 'odd': '📊 НЕЧЕТ'}
    if win > 0:
        user['money'] += win
        user['total_earned'] += win
        add_exp(uid, win // 4)
        save_data()
        msg = f"🎡 РУЛЕТКА 🎡\n\n🎲 Выпало: {color_emoji} {num}\n🎯 Ставка: {bet_names[bet_type]} {bet}\n💰 ВЫИГРЫШ: +{win} 💰\n💵 Баланс: {user['money']}"
    else:
        save_data()
        msg = f"🎡 РУЛЕТКА 🎡\n\n🎲 Выпало: {color_emoji} {num}\n🎯 Ставка: {bet_names[bet_type]} {bet}\n💔 ПРОИГРЫШ 💔\n💵 Баланс: {user['money']}"
    bot.send_message(message.chat.id, msg)
    del roulette_waiting[uid]

# ========== БЛЕКДЖЕК С ЭМОДЗИ ==========

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
    deck = []
    for _ in range(4):
        for c in ['2️⃣','3️⃣','4️⃣','5️⃣','6️⃣','7️⃣','8️⃣','9️⃣','🔟','👑','👸','🤴','🅰️']:
            deck.append(c)
    random.shuffle(deck)
    return deck

@bot.message_handler(func=lambda m: m.text and m.text.lower() in ['блекджек', 'блек джек', 'blackjack', '21'])
def bj_start_cmd(message):
    uid = message.from_user.id
    kb = telebot.types.InlineKeyboardMarkup()
    kb.add(
        telebot.types.InlineKeyboardButton("🔟", callback_data='bj_10'),
        telebot.types.InlineKeyboardButton("5️⃣0️⃣", callback_data='bj_50'),
        telebot.types.InlineKeyboardButton("1️⃣0️⃣0️⃣", callback_data='bj_100')
    )
    bot.send_message(message.chat.id, "🃏 ВЫБЕРИ СТАВКУ 🃏", reply_markup=kb)

@bot.callback_query_handler(func=lambda call: call.data.startswith('bj_') and len(call.data) < 7)
def bj_new_game(call):
    uid = call.from_user.id
    bet = int(call.data.split('_')[1])
    user = get_user(uid, call.from_user.username)
    if user['money'] < bet:
        bot.answer_callback_query(call.id, f"❌ Не хватает {bet}!", show_alert=True)
        return
    user['money'] -= bet
    save_data()
    deck = new_deck()
    player_hand = [deck.pop(), deck.pop()]
    dealer_hand = [deck.pop(), deck.pop()]
    bj_games[uid] = {
        'bet': bet,
        'player': player_hand,
        'dealer': dealer_hand,
        'deck': deck,
        'chat_id': call.message.chat.id,
        'msg_id': call.message.message_id
    }
    bj_show_game(call.message.chat.id, uid, call.message.message_id)
    bot.answer_callback_query(call.id)

def bj_show_game(chat_id, uid, msg_id):
    game = bj_games.get(uid)
    if not game:
        return
    ps = hand_score(game['player'])
    ds = hand_score([game['dealer'][0]])
    msg = f"🃏 *БЛЕК ДЖЕК* 🃏\n\n"
    msg += f"💰 СТАВКА: *{game['bet']}* 💰\n\n"
    msg += f"👨‍💼 ДИЛЕР: {game['dealer'][0]} | ❓\n"
    msg += f"⭐ ОЧКИ: *{ds}* + ? ⭐\n\n"
    msg += f"🎲 ТЫ: {' '.join(game['player'])} 🎲\n"
    msg += f"⭐ ОЧКИ: *{ps}* ⭐\n"
    kb = telebot.types.InlineKeyboardMarkup()
    kb.add(
        telebot.types.InlineKeyboardButton("🎴 ЕЩЕ 🎴", callback_data='bj_hit'),
        telebot.types.InlineKeyboardButton("✋ ХВАТИТ ✋", callback_data='bj_stand')
    )
    try:
        bot.edit_message_text(msg, chat_id, msg_id, parse_mode='Markdown', reply_markup=kb)
    except:
        pass

@bot.callback_query_handler(func=lambda call: call.data == 'bj_hit')
def bj_hit_callback(call):
    uid = call.from_user.id
    game = bj_games.get(uid)
    if not game:
        bot.answer_callback_query(call.id, "❌ Игра не найдена!", show_alert=True)
        return
    card = game['deck'].pop()
    game['player'].append(card)
    ps = hand_score(game['player'])
    if ps > 21:
        msg = f"🃏 *БЛЕК ДЖЕК* 🃏\n\n"
        msg += f"💰 СТАВКА: *{game['bet']}* 💰\n\n"
        msg += f"🎲 ТВОИ КАРТЫ: {' '.join(game['player'])} 🎲\n"
        msg += f"⭐ ОЧКИ: *{ps}* ❌ *ПЕРЕБОР!* ❌\n\n"
        msg += f"💔 *ТЫ ПРОИГРАЛ* {game['bet']}! 💔"
        try:
            bot.edit_message_text(msg, game['chat_id'], game['msg_id'], parse_mode='Markdown')
        except:
            pass
        bot.answer_callback_query(call.id, "ПЕРЕБОР!", show_alert=True)
        del bj_games[uid]
        return
    bj_games[uid] = game
    msg = f"🃏 *БЛЕК ДЖЕК* 🃏\n\n"
    msg += f"💰 СТАВКА: *{game['bet']}* 💰\n\n"
    msg += f"👨‍💼 ДИЛЕР: {game['dealer'][0]} | ❓\n"
    msg += f"🎲 ТЫ: {' '.join(game['player'])} 🎲\n"
    msg += f"⭐ ОЧКИ: *{ps}* ⭐\n"
    kb = telebot.types.InlineKeyboardMarkup()
    kb.add(
        telebot.types.InlineKeyboardButton("🎴 ЕЩЕ 🎴", callback_data='bj_hit'),
        telebot.types.InlineKeyboardButton("✋ ХВАТИТ ✋", callback_data='bj_stand')
    )
    try:
        bot.edit_message_text(msg, game['chat_id'], game['msg_id'], parse_mode='Markdown', reply_markup=kb)
    except:
        pass
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data == 'bj_stand')
def bj_stand_callback(call):
    uid = call.from_user.id
    game = bj_games.get(uid)
    if not game:
        bot.answer_callback_query(call.id, "❌ Игра не найдена!", show_alert=True)
        return
    ps = hand_score(game['player'])
    ds = hand_score(game['dealer'])
    while ds < 17:
        card = game['deck'].pop()
        game['dealer'].append(card)
        ds = hand_score(game['dealer'])
    user = get_user(uid, call.from_user.username)
    if ds > 21:
        win = game['bet'] * 2
        user['money'] += win
        user['total_earned'] += win
        add_exp(uid, win // 4)
        res = f"🎉 ПОБЕДА! 🎉\n💰 +{win} шекелей! 💰"
    elif ps > ds:
        win = game['bet'] * 2
        user['money'] += win
        user['total_earned'] += win
        add_exp(uid, win // 4)
        res = f"🎉 ПОБЕДА! 🎉\n💰 +{win} шекелей! 💰"
    elif ps < ds:
        res = f"💔 ПРОИГРЫШ! 💔\n😭 -{game['bet']} шекелей! 😭"
    else:
        user['money'] += game['bet']
        res = f"🤝 НИЧЬЯ! 🤝\n💰 +{game['bet']} шекелей! 💰"
    save_data()
    msg = f"🃏 *БЛЕК ДЖЕК* 🃏\n\n"
    msg += f"💰 СТАВКА: *{game['bet']}* 💰\n\n"
    msg += f"👨‍💼 ДИЛЕР: {' '.join(game['dealer'])} 👨‍💼\n"
    msg += f"⭐ ОЧКИ: *{ds}* ⭐\n\n"
    msg += f"🎲 ТЫ: {' '.join(game['player'])} 🎲\n"
    msg += f"⭐ ОЧКИ: *{ps}* ⭐\n\n"
    msg += f"{res}\n"
    msg += f"💰 БАЛАНС: *{user['money']}* 💰"
    try:
        bot.edit_message_text(msg, game['chat_id'], game['msg_id'], parse_mode='Markdown')
    except:
        pass
    bot.answer_callback_query(call.id)
    del bj_games[uid]

# ========== ЗАПУСК ==========

load_data()
print("=" * 50)
print("ХИТРЫЙ ЕВРЕЙ БОТ ЗАПУЩЕН!")
print("Слоты 3x3 - работают")
print("Рулетка - работает")
print("Блекджек - работает")
print("Дуэли - работают")
print("Провалы на работе - включены (5%)")
print("=" * 50)

bot.infinity_polling()
