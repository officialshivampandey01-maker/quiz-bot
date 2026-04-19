import telebot
import json
import os
from telebot import types

TOKEN = "8683570334:AAFIauRar8CEffsIb6nozFcgyUQsQgFaFh0"
bot = telebot.TeleBot(TOKEN)

QUIZ_FILE = "quiz.json"

user_scores = {}
user_question_index = {}
poll_map = {}

# LOAD QUIZ
def load_quiz():
    if os.path.exists(QUIZ_FILE):
        with open(QUIZ_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

quiz_data = load_quiz()

# START MENU
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🧠 Start Quiz", "📊 My Score")

    bot.send_message(
        message.chat.id,
        "🔥 Welcome!\nUpload JSON file then press Start Quiz",
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

    bot.send_message(chat_id, "✅ Quiz Started!")
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

    # CLEAN QUESTION
    question = str(q.get("question", "")).strip()

    # CLEAN OPTIONS
    options = q.get("options", [])
    options = [str(opt).strip() for opt in options if str(opt).strip() != ""]

    # SAFETY FIX
    if len(options) < 2:
        options = ["Option A", "Option B", "Option C", "Option D"]

    msg = bot.send_poll(
        chat_id,
        question,
        options,
        type="quiz",
        correct_option_id=int(q.get("correct", 0)),
        is_anonymous=False
    )

    poll_map[msg.poll.id] = chat_id

# HANDLE ANSWER
@bot.poll_answer_handler()
def handle_answer(poll_answer):
    poll_id = poll_answer.poll_id

    if poll_id not in poll_map:
        return

    chat_id = poll_map[poll_id]
    selected = poll_answer.option_ids[0]

    q_index = user_question_index.get(chat_id, 0)

    if selected == int(quiz_data[q_index].get("correct", 0)):
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

# FILE UPLOAD
@bot.message_handler(content_types=['document'])
def handle_file(message):
    try:
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        with open(QUIZ_FILE, "wb") as f:
            f.write(downloaded_file)

        data = load_quiz()

        bot.send_message(
            message.chat.id,
            f"✅ Uploaded!\n📊 Questions: {len(data)}"
        )

    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Error: {e}")

print("Bot running...")
bot.infinity_polling()
