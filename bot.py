import telebot
import json
import os
from telebot import types

TOKEN = "8683570334:AAFIauRar8CEffsIb6nozFcgyUQsQgFaFh0"
bot = telebot.TeleBot(TOKEN)

QUIZ_FILE = "quiz.json"

# Data
user_scores = {}
user_question_index = {}
poll_map = {}  # poll_id -> chat_id

# Load quiz
def load_quiz():
    if os.path.exists(QUIZ_FILE):
        with open(QUIZ_FILE, "r") as f:
            return json.load(f)
    return []

quiz_data = load_quiz()

# START
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🧠 Start Quiz", "📊 My Score")

    bot.send_message(
        message.chat.id,
        "🔥 Welcome!\nSend JSON file to upload quiz.",
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

    chat_id = message.chat.id
    user_scores[chat_id] = 0
    user_question_index[chat_id] = 0

    send_question(chat_id)

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

    msg = bot.send_poll(
        chat_id,
        q["question"],
        q["options"],
        type="quiz",
        correct_option_id=q["correct"],
        is_anonymous=False
    )

    # Save poll_id mapping
    poll_map[msg.poll.id] = chat_id

# HANDLE ANSWER
@bot.poll_answer_handler()
def handle_poll_answer(poll_answer):
    poll_id = poll_answer.poll_id
    selected = poll_answer.option_ids[0]

    if poll_id not in poll_map:
        return

    chat_id = poll_map[poll_id]

    q_index = user_question_index[chat_id]

    if selected == quiz_data[q_index]["correct"]:
        user_scores[chat_id] += 1

    user_question_index[chat_id] += 1

    send_question(chat_id)

# SCORE
@bot.message_handler(func=lambda message: message.text == "📊 My Score")
def score(message):
    score = user_scores.get(message.chat.id, 0)
    bot.send_message(message.chat.id, f"📊 Your Score: {score}")

# FILE UPLOAD
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
