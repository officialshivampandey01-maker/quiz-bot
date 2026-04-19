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

# -------- LOAD QUIZ --------
def load_quiz():
    if os.path.exists(QUIZ_FILE):
        with open(QUIZ_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

quiz_data = load_quiz()

# -------- AUTO QUIZ FROM TEXT --------
def generate_quiz_from_text(text):
    questions = []
    lines = text.split("\n")

    for i, line in enumerate(lines):
        if len(line.strip()) > 20:
            q = {
                "question": f"{line.strip()} ka correct answer kya hai?",
                "options": ["Option A", "Option B", "Option C", "Option D"],
                "correct": 0
            }
            questions.append(q)

    return questions[:10]  # limit

# -------- START --------
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🧠 Start Quiz", "📊 My Score", "🎯 Create Quiz")

    bot.send_message(
        message.chat.id,
        "🔥 Welcome!\nSend JSON / text / file to create quiz",
        reply_markup=markup
    )

# -------- START QUIZ --------
@bot.message_handler(func=lambda m: m.text == "🧠 Start Quiz")
def start_quiz(message):
    global quiz_data
    quiz_data = load_quiz()

    if not quiz_data:
        bot.send_message(message.chat.id, "⚠️ No quiz available!")
        return

    chat_id = message.chat.id
    user_scores[chat_id] = 0
    user_question_index[chat_id] = 0

    send_question(chat_id)

# -------- SEND QUESTION --------
def send_question(chat_id):
    q_index = user_question_index.get(chat_id, 0)

    if q_index >= len(quiz_data):
        bot.send_message(chat_id, f"🎉 Finished!\nScore: {user_scores[chat_id]}/{len(quiz_data)}")
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

# -------- ANSWER --------
@bot.poll_answer_handler()
def handle_answer(poll_answer):
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

# -------- SCORE --------
@bot.message_handler(func=lambda m: m.text == "📊 My Score")
def score(message):
    bot.send_message(message.chat.id, f"Score: {user_scores.get(message.chat.id, 0)}")

# -------- CREATE QUIZ FROM TEXT --------
@bot.message_handler(func=lambda m: m.text == "🎯 Create Quiz")
def ask_text(message):
    bot.send_message(message.chat.id, "Send text to generate quiz")

@bot.message_handler(content_types=['text'])
def handle_text(message):
    if message.text.startswith("/"):
        return

    questions = generate_quiz_from_text(message.text)

    if not questions:
        return

    with open(QUIZ_FILE, "w", encoding="utf-8") as f:
        json.dump(questions, f, ensure_ascii=False, indent=2)

    bot.send_message(message.chat.id, f"✅ Quiz Created!\nQuestions: {len(questions)}")

# -------- FILE UPLOAD --------
@bot.message_handler(content_types=['document'])
def handle_file(message):
    try:
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        with open(QUIZ_FILE, "wb") as f:
            f.write(downloaded_file)

        data = load_quiz()

        bot.send_message(message.chat.id, f"✅ Uploaded!\nQuestions: {len(data)}")

    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Error: {e}")

print("Bot running...")
bot.infinity_polling()
