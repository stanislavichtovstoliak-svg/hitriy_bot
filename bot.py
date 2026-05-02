import telebot
import random
import json
import os
from datetime import datetime
import time

# Токен из переменных окружения Railway
TOKEN = os.environ.get('8672284943:AAGr068cDybidNBehyS0Dcst5wj0BcGjLAU')

if not TOKEN:
    print("ОШИБКА: Токен не найден!")
    exit(1)

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
    user['last_work'] = datetime.now().isoformat()
    save_users(users)
    
    bot.send_message(message.chat.id, f"🌾 +{earned} шекелей!\n💰 Баланс: {user['money']}")

@bot.message_handler(func=lambda m: m.text == '🎰 Слоты')
def slots_menu(message):
    kb = telebot.types.InlineKeyboardMarkup()
    kb.add(telebot.types.InlineKeyboardButton("10", callback_data='slot_10'))
    kb.add(telebot.types.InlineKeyboardButton("50", callback_data='slot_50'))
    kb.add(telebot.types.InlineKeyboardButton("100", callback_data='slot_100'))
    bot.send_message(message.chat.id, "🎰 Ставка:", reply_markup=kb)

@bot.callback_query_handler(func=lambda call: call.data.startswith('slot_'))
def slots_play(call):
    bet = int(call.data.split('_')[1])
    user = get_user(call.from_user.id)
    
    if user['money'] < bet:
        bot.answer_callback_query(call.id, "❌ Не хватает!", show_alert=True)
        return
    
    user['money'] -= bet
    icons = ['🍒', '🍊', '🍋', '💰', '💎']
    res = [random.choice(icons) for _ in range(3)]
    
    win = 0
    if res[0] == res[1] == res[2]:
        if res[0] == '🍒': win = bet * 2
        elif res[0] == '💰': win = bet * 5
        elif res[0] == '💎': win = bet * 10
        else: win = bet * 2
    
    if win > 0:
        user['money'] += win
        msg = f"✨ ПОБЕДА! +{win}\n💰 {user['money']}"
    else:
        msg = f"💔 ПРОИГРЫШ\n💰 {user['money']}"
    
    save_users(users)
    bot.edit_message_text(f"🎰 {res[0]} | {res[1]} | {res[2]}\n\n{msg}", 
                          call.message.chat.id, call.message.message_id)
    bot.answer_callback_query(call.id)

print("🤖 ХИТРЫЙ ЕВРЕЙ БОТ ЗАПУЩЕН!")
print(f"Бот: @{bot.get_me().username}")

bot.infinity_polling()
