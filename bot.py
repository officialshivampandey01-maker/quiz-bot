import telebot
import json
import os
from telebot import types

TOKEN = "8683570334:AAFIauRar8CEffsIb6nozFcgyUQsQgFaFh0"

bot = telebot.TeleBot(TOKEN)

QUIZ_FILE = "quiz.json"

# User data
user_scores = {}
user_question_index = {}

# Load quiz file
def load_quiz():
    if os.path.exists(QUIZ_FILE):
        with open(QUIZ_FILE, "r") as f:
            return json.load(f)
    return []

quiz_data = load_quiz()

# START MENU
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    btn1 = types.KeyboardButton("🧠 Start Quiz")
    btn2 = types.KeyboardButton("📊 My Score")

    markup.add(btn1, btn2)

    bot.send_message(
        message.chat.id,
        "🔥 Welcome to Shivam Quiz Bot!\nSend JSON file to upload quiz.",
        reply_markup=markup
    )

# START QUIZ
@bot.message_handler(func=lambda message: message.text == "🧠 Start Quiz")
def start_quiz(message):
    global quiz_data
    quiz_data = load_quiz()

    if not quiz_data:
        bot.send_message(message.chat.id, "⚠️ No quiz uploaded!")
        return

    user_scores[message.chat.id] = 0
    user_question_index[message.chat.id] = 0

    send_question(message.chat.id)

# SEND QUESTION
def send_question(chat_id):
    q_index = user_question_index.get(chat_id, 0)

    if q_index >= len(quiz_data):
        bot.send_message(
            chat_id,
            f"🎉 Quiz Finished!\nScore: {user_scores[chat_id]}/{len(quiz_data)}"
        )
        return

    q = quiz_data[q_index]

    bot.send_poll(
        chat_id,
        q["question"],
        q["options"],
        type="quiz",
        correct_option_id=q["correct"],
        is_anonymous=False
    )

# HANDLE ANSWERS
@bot.poll_answer_handler()
def handle_poll_answer(poll_answer):
    user_id = poll_answer.user.id
    selected = poll_answer.option_ids[0]

    if user_id not in user_question_index:
        return

    q_index = user_question_index[user_id]

    if selected == quiz_data[q_index]["correct"]:
        user_scores[user_id] += 1

    user_question_index[user_id] += 1

    send_question(user_id)

# SHOW SCORE
@bot.message_handler(func=lambda message: message.text == "📊 My Score")
def show_score(message):
    score = user_scores.get(message.chat.id, 0)
    bot.send_message(message.chat.id, f"📊 Your Score: {score}")

# JSON FILE UPLOAD
@bot.message_handler(content_types=['document'])
def handle_file(message):
    try:
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        with open(QUIZ_FILE, "wb") as f:
            f.write(downloaded_file)

        bot.send_message(message.chat.id, "✅ Quiz file uploaded successfully!")

    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Error: {e}")

print("Bot running...")
bot.infinity_polling()
