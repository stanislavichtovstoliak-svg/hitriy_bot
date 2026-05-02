import telebot

TOKEN = '8672284943:AAEVBa7F9rKGQK76pkLr0vvHyDXKFCJDFos'
bot = telebot.TeleBot(TOKEN)

# Список команд, на которые будет ответ
COMMANDS = [
    'start', 'команды', 'работа', 'фарм', 'баланс', 'деньги',
    'профиль', 'стата', 'топ', 'топ10', 'лидеры', 'бонус',
    'ежедневный', 'daily', 'слоты', 'слот', 'рулетка', 'рулетку',
    'скачки', 'ставка', 'лотерея', 'билет', 'банк',
    'положить', 'снять', 'депозит', 'забрать', 'магазин',
    'купить', 'дать', 'достижения', 'ачивки', 'команды'
]

# Обработчик только команд
@bot.message_handler(func=lambda m: m.text and (
    m.text.startswith('/') or 
    m.text.lower() in COMMANDS or
    m.text.lower().startswith('#промо') or
    m.text.lower().startswith('положить') or
    m.text.lower().startswith('снять') or
    m.text.lower().startswith('депозит') or
    m.text.lower().startswith('дать') or
    m.text.lower().startswith('купить')
))
def command_handler(m):
    bot.send_message(m.chat.id, "🔧 Бот закрыт, на доработку 🔧\n\nСкоро вернёмся!")

print("Бот запущен в режиме 'на доработку' (только команды)")
bot.infinity_polling()
