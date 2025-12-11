import telebot
from telebot import types
import threading

from scan import ObrabotkaPhoto
from calc import Output, BMI

API_TOKEN = "8269265780:AAGQpz-v7iTcBwcfJRgGN0p8Ijp-axm4I4o"
bot = telebot.TeleBot(API_TOKEN)

# -------------------- Команды --------------------
@bot.message_handler(commands=['start'])
def cmd_start(message):
    bot.send_message(message.chat.id,
                    "👋 <b>Привет! Я бот для работы с товарами и расчета КБЖУ.</b>\n\n"
                    "📌 <b>Доступные команды:</b>\n"
                    "/help - помощь\n"
                    "/kbju - расчет КБЖУ\n\n"
                    "📷 А также ты можешь присылать <b>фото штрихкода товара,</b> и я дам <b>информацию о его бжу.</b>\n",
                    parse_mode='HTML'
                    )

@bot.message_handler(commands=['help'])
def cmd_help(message):
    bot.send_message(message.chat.id,
                    "📖 <b>Инструкция по использованию:</b>\n\n"
                    "1️⃣ 📷 Присылайте фото штрихкода товара — я верну информацию о нём.\n"
                    "2️⃣ 🥗 Используйте <b>/kbju</b> для расчета калорий, белков, жиров и углеводов.\n"
                    "<b>А также чтобы узнать свой индекс массы тела!</b>",
                    parse_mode='HTML'
                    )
    
# -------------------- Обработка фото --------------------
@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    bot.send_message(message.chat.id, "⏳ Фото получено, обрабатываю...")

    threading.Thread(target=Image, args=(message,)).start()

def Image(message):
    try:
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_image = bot.download_file(file_info.file_path)

        result_text = ObrabotkaPhoto(downloaded_image)

        bot.send_message(message.chat.id, f"<b>Результат</b> ✅\n{result_text}", parse_mode='HTML')

    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка обработки фото: {e}")



# ---------- KБЖУ FSM ----------
user_state = {}
user_data = {}

@bot.message_handler(commands=['kbju'])
def kbju_start(message):
    chat_id = message.chat.id
    user_state[chat_id] = "gender"

    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("🟦 Мужчина", "🩷 Женщина")
    bot.send_message(chat_id, "Выберите пол:", reply_markup=kb)


@bot.message_handler(func=lambda m: m.chat.id in user_state)
def kbju_steps(message):
    chat_id = message.chat.id
    state = user_state[chat_id]
    text = message.text

    # 2 — пол
    if state == "gender":
        if text not in ["🟦 Мужчина", "🩷 Женщина"]:
            return bot.send_message(chat_id, "👇🏻 Нажми кнопку")
        user_data[chat_id] = {"gender": text}
        user_state[chat_id] = "height"
        return bot.send_message(chat_id, "📏 Введите рост в см:", reply_markup=types.ReplyKeyboardRemove())

    # 2 — рост
    if state == "height":
        if not text.isdigit():
            return bot.send_message(chat_id, "✏️ Введите число")
        user_data[chat_id]["height"] = int(text)
        user_state[chat_id] = "weight"
        return bot.send_message(chat_id, "⚖️ Введите вес:")

    # 3 — вес
    if state == "weight":
        if not text.isdigit():
            return bot.send_message(chat_id, "✏️ Введите число")
        user_data[chat_id]["weight"] = int(text)
        user_state[chat_id] = "age"
        return bot.send_message(chat_id, "📆 Введите возраст:")

    # 4 — возраст
    if state == "age":
        if not text.isdigit():
            return bot.send_message(chat_id, "✏️ Введите число")
        user_data[chat_id]["age"] = int(text)

        kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
        kb.add("🪑 1", "🚶‍♂️ 2", "🏃‍♂️ 3", "🏋️‍♂️ 4", "🔥 5")

        user_state[chat_id] = "activity"
        return bot.send_message(chat_id, "Выберите уровень активности\n"
                                "1 - минимальная, 5 - максимальная", reply_markup=kb)
    
    # 5 — активность
    if state == "activity":
        allowed = ["🪑 1", "🚶‍♂️ 2", "🏃‍♂️ 3", "🏋️‍♂️ 4", "🔥 5"]

        if text not in allowed:
            return bot.send_message(chat_id, "Нажмите одну из кнопок 1–5!")

        activity_num = ''.join(c for c in text if c.isdigit())
        user_data[chat_id]["activity"] = int(activity_num)

        kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
        kb.add("Похудеть", "Держать вес", "Набрать вес")

        user_state[chat_id] = "goal"
        return bot.send_message(chat_id, "Выберите цель:", reply_markup=kb)

    # 6 — цель
    if state == "goal":
        goals = {"Похудеть": "lose", "Держать вес": "keep", "Набрать вес": "gain"}
        if text not in goals:
            return bot.send_message(chat_id, "Нажми кнопку")
        user_data[chat_id]["goal"] = goals[text]

        d = user_data[chat_id]
        result = Output(
            gender=d["gender"],
            age=d["age"],
            weight=d["weight"],
            height=d["height"],
            goal=d["goal"],
            activity=d["activity"]
        )

        bmi, bmi_category = BMI(
            weight=d["weight"],
            height=d["height"]
        )

        user_state.pop(chat_id)
        user_data.pop(chat_id)

        return bot.send_message(
            chat_id,
            f"<b>Ваши результаты</b> ✅\n"
            "\n"
            f"Ваш индекс массы тела - <b>{bmi}</b>\n"
            f"Это - {bmi_category}\n"
            "\n"
            f"<b>Ваши необходимые каллории</b> на день состовляют: <b>{result['kcal']} калл.</b>\n"
            f"<b>Белки:</b> {int(result['proteins'][0])}-{int(result['proteins'][1])} г.\n"
            f"<b>Жиры:</b> {int(result['fats'][0])}-{int(result['fats'][1])} г.\n"
            f"<b>Углеводы - это все остальное.</b>\n"
            f"Но выходит примерно от {int(result['carbs'][1])} г. до {int(result['carbs'][0])} г.",
            reply_markup=types.ReplyKeyboardRemove(),
            parse_mode='HTML'
        )

bot.polling(none_stop=True)