import telebot

TOKEN = "8683570334:AAFIauRar8CEffsIb6nozFcgyUQsQgFaFh0"

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "🔥 Welcome to Quiz Bot!\nType /quiz to start.")

@bot.message_handler(commands=['quiz'])
def quiz(message):
    bot.send_poll(
        message.chat.id,
        "India ki capital kya hai?",
        ["Delhi", "Mumbai", "Kolkata", "Chennai"],
        type="quiz",
        correct_option_id=0,
        is_anonymous=False
    )

print("Bot running...")
bot.infinity_polling()
