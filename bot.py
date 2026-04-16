import asyncio
import json
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, types, F

TOKEN = "8787664171:AAGSRE85kVMf-UuaRecz7Sx95Frr8a5Rs0E"
ADMIN_ID = 8095231634

bot = Bot(token=TOKEN)
dp = Dispatcher()

user_states = {}
user_data = {}
submitted_users = set()

# ===== БАЗА =====
def load_users():
    try:
        with open("users.json", "r") as f:
            return json.load(f)
    except:
        return {}

def save_users(data):
    with open("users.json", "w") as f:
        json.dump(data, f)

def register_user(user_id):
    users = load_users()
    if str(user_id) not in users:
        users[str(user_id)] = {
            "joined": str(datetime.now()),
            "submitted": False
        }
        save_users(users)

def mark_submitted(user_id):
    users = load_users()
    if str(user_id) in users:
        users[str(user_id)]["submitted"] = True
        save_users(users)

# ===== КНОПКИ =====
def start_menu():
    return types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="🚀 Подобрать вакансию")],
            [types.KeyboardButton(text="📩 Консультация")]
        ],
        resize_keyboard=True
    )

def main_menu():
    return types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="💼 Вакансии")],
            [types.KeyboardButton(text="📩 Оставить заявку")],
            [types.KeyboardButton(text="📊 Кейсы"), types.KeyboardButton(text="📢 О компании")]
        ],
        resize_keyboard=True
    )

# ===== УМНЫЙ ПРОГРЕВ =====
async def funnel(user_id):
    await asyncio.sleep(180)

    if user_id in submitted_users:
        return

    await bot.send_message(
        user_id,
        "Вы рассматриваете возможность работы за границей?\n\n"
        "Обычно решение откладывают — и теряют шанс"
    )

    await asyncio.sleep(300)

    if user_id in submitted_users:
        return

    await bot.send_message(
        user_id,
        "📊 Практика показывает:\n\n"
        "Клиенты, которые принимают решение сразу — получают результат быстрее"
    )

    await asyncio.sleep(600)

    if user_id in submitted_users:
        return

    await bot.send_message(
        user_id,
        "⚠️ Сейчас есть ограниченное количество мест\n\n"
        "Если вопрос актуален — лучше зафиксировать заявку"
    )

# ===== FOLLOW-UP (на следующий день) =====
async def next_day_followup(user_id):
    await asyncio.sleep(86400)  # 24 часа

    users = load_users()
    if str(user_id) in users and not users[str(user_id)]["submitted"]:
        await bot.send_message(
            user_id,
            "Добрый день\n\n"
            "Вы вчера интересовались работой за границей\n\n"
            "Если вопрос ещё актуален — можем продолжить оформление"
        )

# ===== СТАРТ =====
@dp.message(F.text == "/start")
async def start(message: types.Message):
    user_id = message.from_user.id
    register_user(user_id)

    await message.answer(
        "Blackwood Immigration Law Group\n\n"
        "Официальное сопровождение клиентов\n"
        "в вопросах трудоустройства и иммиграции\n\n"
        "📍 UK / Europe\n"
        "📑 Легальные программы\n"
        "📊 Подтверждённые кейсы\n\n"
        "👇 Укажите цель обращения:",
        reply_markup=start_menu()
    )

    await asyncio.sleep(2)

    await message.answer(
        "📊 За последние 7 дней:\n"
        "— 17 клиентов начали оформление\n"
        "— 8 уже трудоустроены"
    )

    asyncio.create_task(funnel(user_id))
    asyncio.create_task(next_day_followup(user_id))

# ===== СЕГМЕНТАЦИЯ =====
@dp.message(F.text == "🚀 Подобрать вакансию")
async def job(message: types.Message):
    user_data[message.from_user.id] = {"goal": "job"}

    await message.answer(
        "Подберём вакансию под ваш профиль\n\n"
        "👇 Продолжите:",
        reply_markup=main_menu()
    )

@dp.message(F.text == "📩 Консультация")
async def consult(message: types.Message):
    user_data[message.from_user.id] = {"goal": "consult"}

    await message.answer(
        "Проведём консультацию по вашей ситуации\n\n"
        "👇 Оставьте заявку:",
        reply_markup=main_menu()
    )

# ===== КНОПКИ =====
@dp.message(F.text == "💼 Вакансии")
async def jobs(message: types.Message):
    await message.answer(
        "💼 Доступные направления:\n\n"
        "— Склад / логистика\n"
        "— Производство\n"
        "— Строительство\n\n"
        "👉 https://t.me/visaworkuk"
    )

@dp.message(F.text == "📊 Кейсы")
async def reviews(message: types.Message):
    await message.answer(
        "📊 Кейсы клиентов:\n"
        "https://t.me/Blackwood_Immigration_Law_Group"
    )

@dp.message(F.text == "📢 О компании")
async def about(message: types.Message):
    await message.answer(
        "Blackwood Immigration Law Group\n\n"
        "Работаем с трудоустройством и визовыми вопросами\n\n"
        "📢 https://t.me/BlackwoodImmigration_Law_Group"
    )

# ===== ЗАЯВКА =====
@dp.message(F.text == "📩 Оставить заявку")
async def form_start(message: types.Message):
    submitted_users.add(message.from_user.id)
    mark_submitted(message.from_user.id)

    user_states[message.from_user.id] = "name"
    await message.answer("Введите ваше имя:")

@dp.message()
async def form_process(message: types.Message):
    state = user_states.get(message.from_user.id)

    if state == "name":
        user_states[message.from_user.id] = {"name": message.text}
        await message.answer("Контакт (Telegram или телефон):")

    elif isinstance(state, dict):
        data = state
        data["contact"] = message.text

        goal = user_data.get(message.from_user.id, {}).get("goal", "не указано")

        await bot.send_message(
            ADMIN_ID,
            f"📩 Новая заявка\n\n"
            f"Имя: {data['name']}\n"
            f"Контакт: {data['contact']}\n"
            f"Цель: {goal}"
        )

        await message.answer(
            "✅ Заявка принята\n\n"
            "Специалист свяжется с вами\n\n"
            "📊 Кейсы:\nhttps://t.me/Blackwood_Immigration_Law_Group"
        )

        user_states.pop(message.from_user.id)

# ===== РАССЫЛКА =====
@dp.message(F.text.startswith("/send"))
async def broadcast(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return

    text = message.text.replace("/send ", "")
    users = load_users()

    sent = 0

    for user_id in users:
        try:
            await bot.send_message(int(user_id), text)
            sent += 1
        except:
            pass

    await message.answer(f"Отправлено: {sent}")

# ===== ЗАПУСК =====
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())