import telebot
import json

TOKEN = "8683570334:AAFIauRar8CEffsIb6nozFcgyUQsQgFaFh0"

bot = telebot.TeleBot(TOKEN)

# Load quiz data
with open("quiz.json", "r") as f:
    quiz_data = json.load(f)

user_scores = {}

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "🔥 Welcome to Quiz Bot!\nType /quiz to start.")

@bot.message_handler(commands=['quiz'])
def start_quiz(message):
    user_scores[message.chat.id] = 0
    send_question(message.chat.id, 0)

def send_question(chat_id, q_index):
    if q_index >= len(quiz_data):
        bot.send_message(chat_id, f"🎉 Quiz Finished!\nScore: {user_scores[chat_id]}/{len(quiz_data)}")
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

@bot.poll_answer_handler()
def handle_poll_answer(poll_answer):
    user_id = poll_answer.user.id
    selected = poll_answer.option_ids[0]

    # Track question index
    if user_id not in user_scores:
        user_scores[user_id] = 0

    # Increase score if correct
    # (simple logic - assumes same order)
    current_q = user_scores[user_id]

    if selected == quiz_data[current_q]["correct"]:
        user_scores[user_id] += 1

    send_question(user_id, current_q + 1)

print("Bot running...")
bot.infinity_polling()
