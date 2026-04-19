import telebot
import json
import os
from telebot import types
from requests.exceptions import ReadTimeout

TOKEN = "8683570334:AAFIauRar8CEffsIb6nozFcgyUQsQgFaFh0"

# Increased timeout
bot = telebot.TeleBot(TOKEN, parse_mode="HTML")

QUIZ_FILE = "quiz.json"

user_scores = {}
user_question_index = {}
poll_map = {}

# Load quiz
def load_quiz():
    if os.path.exists(QUIZ_FILE):
        with open(QUIZ_FILE, "r", encoding="utf-8") as f:
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
        "🔥 Welcome!\nSend large JSON file (1000+ questions supported)",
        reply_markup=markup
    )

# START QUIZ
@bot.message_handler(func=lambda m: m.text == "🧠 Start Quiz")
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

    poll_map[msg.poll.id] = chat_id

# HANDLE ANSWER
@bot.poll_answer_handler()
def handle_poll_answer(poll_answer):
    poll_id = poll_answer.poll_id

    if poll_id not in poll_map:
        return

    chat_id = poll_map[poll_id]
    selected = poll_answer.option_ids[0]
    q_index = user_question_index[chat_id]

    if selected == quiz_data[q_index]["correct"]:
        user_scores[chat_id] += 1

    user_question_index[chat_id] += 1
    send_question(chat_id)

# SCORE
@bot.message_handler(func=lambda m: m.text == "📊 My Score")
def score(message):
    bot.send_message(
        message.chat.id,
        f"📊 Score: {user_scores.get(message.chat.id, 0)}"
    )

# FILE UPLOAD (IMPROVED)
@bot.message_handler(content_types=['document'])
def handle_file(message):
    try:
        file_info = bot.get_file(message.document.file_id)

        # Retry logic
        for _ in range(3):
            try:
                downloaded_file = bot.download_file(file_info.file_path)
                break
            except ReadTimeout:
                continue

        with open(QUIZ_FILE, "wb") as f:
            f.write(downloaded_file)

        # Validate JSON
        data = load_quiz()

        bot.send_message(
            message.chat.id,
            f"✅ Uploaded!\n📊 Total Questions: {len(data)}"
        )

    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Error: {e}")

print("Bot running...")
bot.infinity_polling(timeout=60, long_polling_timeout=60)
