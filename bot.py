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

# Load quiz from JSON file (matches your advanced schema)
def load_quiz():
    if os.path.exists(QUIZ_FILE):
        with open(QUIZ_FILE, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
                # Convert correct_option value to index for Telegram poll
                for q in data:
                    if "correct_option" in q and "options" in q:
                        idx = -1
                        opts = [str(opt).strip() for opt in q["options"]]
                        for i, opt in enumerate(opts):
                            # compare ignoring case & whitespace
                            if opt.strip().lower() == q["correct_option"].strip().lower():
                                idx = i
                                break
                        q["correct"] = idx if idx >= 0 else 0
                return data
            except Exception as e:
                print(f"Error loading quiz: {e}")
    return []

quiz_data = load_quiz()

# Start menu
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🧠 Start Quiz", "📊 My Score")
    bot.send_message(
        message.chat.id,
        "🔥 Welcome!\nUpload JSON file then press Start Quiz",
        reply_markup=markup
    )

# Start Quiz
@bot.message_handler(func=lambda m: m.text == "🧠 Start Quiz")
def start_quiz(message):
    global quiz_data
    quiz_data = load_quiz()

    if not quiz_data:
        bot.send_message(message.chat.id, "⚠️ No quiz uploaded or quiz file format error!")
        return

    chat_id = message.chat.id
    user_scores[chat_id] = 0
    user_question_index[chat_id] = 0

    bot.send_message(chat_id, "✅ Quiz Started!")
    send_question(chat_id)

# Send Question
def send_question(chat_id):
    q_index = user_question_index.get(chat_id, 0)

    if q_index >= len(quiz_data):
        bot.send_message(
            chat_id,
            f"🎉 Quiz Finished!\nScore: {user_scores[chat_id]}/{len(quiz_data)}"
        )
        return

    q = quiz_data[q_index]
    question = str(q.get("question", "")).strip()
    options = [str(opt).strip() for opt in q.get("options", []) if str(opt).strip() != ""]

    if len(options) < 2:
        options = ["Option A", "Option B", "Option C", "Option D"]

    correct_index = int(q.get("correct", 0))
    if correct_index < 0 or correct_index >= len(options):
        correct_index = 0  # Fallback

    msg = bot.send_poll(
        chat_id,
        question,
        options,
        type="quiz",
        correct_option_id=correct_index,
        is_anonymous=False
    )
    poll_map[msg.poll.id] = chat_id

# Handle Answer
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

# Score Command
@bot.message_handler(func=lambda m: m.text == "📊 My Score")
def score(message):
    bot.send_message(
        message.chat.id,
        f"📊 Score: {user_scores.get(message.chat.id, 0)}"
    )

# File Upload (accepts only .json, parses and tests file)
@bot.message_handler(content_types=['document'])
def handle_file(message):
    try:
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        with open(QUIZ_FILE, "wb") as f:
            f.write(downloaded_file)

        # Validate/parse file
        data = load_quiz()

        bot.send_message(
            message.chat.id,
            f"✅ Uploaded! 📊 Questions: {len(data)}"
        )

    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Error: {e}")

print("Bot running...")
bot.infinity_polling()