import telebot

TOKEN = '8672284943:AAEVBa7F9rKGQK76pkLr0vvHyDXKFCJDFos'
bot = telebot.TeleBot(TOKEN)

# Обработчик всех текстовых сообщений
@bot.message_handler(func=lambda m: True)
def all_messages(m):
    bot.send_message(m.chat.id, "🔧 Бот закрыт, на доработку 🔧\n\nСкоро вернёмся!")

print("Бот запущен в режиме 'на доработку'")
bot.infinity_polling()
