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

def guess_correct_field(q):
    # Accept any of these common keys
    for field in ['correct_option', 'answer', 'correct', 'ans']:
        if field in q:
            return q[field]
    # Fuzzy: find key containing ans/correct
    for k in q:
        if any(x in k.lower() for x in ['ans', 'correct']):
            return q[k]
    return None

def load_quiz():
    if os.path.exists(QUIZ_FILE):
        with open(QUIZ_FILE, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
                for q in data:
                    options = q.get("options", [])
                    correct_txt = guess_correct_field(q)
                    idx = 0
                    opts = [str(opt).strip() for opt in options]
                    for i, opt in enumerate(opts):
                        if correct_txt and opt.replace('"','').strip().lower() == str(correct_txt).replace('"','').strip().lower():
                            idx = i
                            break
                    q["correct"] = idx
                return data
            except Exception as e:
                print(f"Error loading quiz: {e}")
    return []

quiz_data = load_quiz()

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🧠 Start Quiz", "📊 My Score")
    bot.send_message(
        message.chat.id,
        "🔥 Welcome!\nUpload JSON file or PASTE your MCQ JSON/text below (any fieldnames: answer, correct_option, correct, ans, etc). Then press Start Quiz.",
        reply_markup=markup
    )

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
        correct_index = 0  # fallback

    msg = bot.send_poll(
        chat_id,
        question,
        options,
        type="quiz",
        correct_option_id=correct_index,
        is_anonymous=False
    )
    poll_map[msg.poll.id] = chat_id

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

@bot.message_handler(func=lambda m: m.text == "📊 My Score")
def score(message):
    bot.send_message(
        message.chat.id,
        f"📊 Score: {user_scores.get(message.chat.id, 0)}"
    )

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
            f"✅ Uploaded! 📊 Questions: {len(data)}"
        )
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Error: {e}")

@bot.message_handler(content_types=['text'])
def handle_json_text(message):
    text = message.text.strip()
    try:
        try_json = text
        # Add [] wrap for single objects
        if try_json.startswith("{") and try_json.endswith("}"):
            try_json = "[" + try_json + "]"
        # Replace single quotes with double quotes if needed
        if "'" in try_json and '"' not in try_json:
            try_json = try_json.replace("'", '"')
        # Remove trailing commas before closing list (common copy-paste)
        try_json = try_json.replace(",\n]", "\n]")
        quizz = json.loads(try_json)
        if isinstance(quizz, dict):
            quizz = [quizz]
        for q in quizz:
            if "question" in q and "options" in q:
                correct_txt = guess_correct_field(q)
                idx = 0
                opts = [str(opt).strip() for opt in q["options"]]
                for i, opt in enumerate(opts):
                    if correct_txt and opt.replace('"','').strip().lower() == str(correct_txt).replace('"','').strip().lower():
                        idx = i
                        break
                q["correct"] = idx
        with open(QUIZ_FILE, "w", encoding="utf-8") as f:
            json.dump(quizz, f, ensure_ascii=False, indent=2)
        bot.send_message(message.chat.id, f"✅ Quiz loaded from pasted text! Questions: {len(quizz)}")
    except Exception as e:
        bot.send_message(message.chat.id,
            "❌ Error: MCQ parsing failed!\n\n"
            "• Paste must be a valid JSON array or object(s).\n"
            "• Supported answer fields: correct_option, answer, correct, ans (auto).\n"
            "• Strings/field names ideally double quotes.\n"
            f"_Details:_ {e}"
        )

print("Bot running...")
bot.infinity_polling()
