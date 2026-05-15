import asyncio
import os
import sqlite3
from datetime import datetime

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
MANAGER_CHAT_ID = os.getenv("MANAGER_CHAT_ID")
MANAGER_PHONE = os.getenv("MANAGER_PHONE", "+996 XXX XX XX XX")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не найден в .env")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

db = sqlite3.connect("database.db")
cursor = db.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS leads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TEXT,
    client_name TEXT,
    username TEXT,
    telegram_id TEXT,
    model TEXT,
    budget TEXT,
    city TEXT,
    phone TEXT,
    comment TEXT,
    status TEXT
)
""")
db.commit()


class LeadForm(StatesGroup):
    model = State()
    budget = State()
    city = State()
    phone = State()
    comment = State()


def main_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Оставить заявку", callback_data="lead_start")],
        [InlineKeyboardButton(text="Модели Changan", callback_data="models")],
        [InlineKeyboardButton(text="Узнать стоимость", callback_data="price")],
        [InlineKeyboardButton(text="Связаться с менеджером", callback_data="manager")],
        [InlineKeyboardButton(text="О компании", callback_data="about")]
    ])


def back_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Назад", callback_data="home")]
    ])


def models_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Changan UNI-Z", callback_data="model:Changan UNI-Z")],
        [InlineKeyboardButton(text="Changan UNI-K", callback_data="model:Changan UNI-K")],
        [InlineKeyboardButton(text="Changan UNI-V", callback_data="model:Changan UNI-V")],
        [InlineKeyboardButton(text="Changan CS75 Plus", callback_data="model:Changan CS75 Plus")],
        [InlineKeyboardButton(text="Другая модель", callback_data="model:Другая модель")],
        [InlineKeyboardButton(text="Назад", callback_data="home")]
    ])


async def send_to_manager(text):
    if not MANAGER_CHAT_ID:
        print("MANAGER_CHAT_ID не указан")
        print(text)
        return

    try:
        await bot.send_message(int(MANAGER_CHAT_ID), text)
        print("Заявка отправлена менеджеру")
    except Exception as e:
        print("Ошибка отправки менеджеру:", e)
        print(text)


async def show_home(target):
    text = (
        "Здравствуйте.\n"
        "Вас приветствует Автоальянс86KG.\n\n"
        "Мы специализируемся на подборе и поставке автомобилей Changan под заказ.\n\n"
        "Выберите нужный раздел:"
    )

    if isinstance(target, Message):
        await target.answer(text, reply_markup=main_menu())
    else:
        await target.message.edit_text(text, reply_markup=main_menu())


@dp.message(CommandStart())
async def start(message: Message, state: FSMContext):
    await state.clear()
    await show_home(message)


@dp.message(Command("id"))
async def get_id(message: Message):
    await message.answer(f"Ваш Telegram ID:\n{message.from_user.id}")


@dp.message(Command("leads"))
async def show_leads(message: Message):
    if str(message.from_user.id) != str(MANAGER_CHAT_ID):
        await message.answer("У вас нет доступа к заявкам.")
        return

    cursor.execute("""
    SELECT id, created_at, model, budget, city, phone, status
    FROM leads
    ORDER BY id DESC
    LIMIT 10
    """)
    rows = cursor.fetchall()

    if not rows:
        await message.answer("Заявок пока нет.")
        return

    text = "Последние заявки:\n\n"

    for row in rows:
        text += (
            f"Заявка #{row[0]}\n"
            f"Дата: {row[1]}\n"
            f"Модель: {row[2]}\n"
            f"Бюджет: {row[3]}\n"
            f"Город: {row[4]}\n"
            f"Телефон: {row[5]}\n"
            f"Статус: {row[6]}\n\n"
        )

    await message.answer(text)


@dp.callback_query(F.data == "home")
async def home(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.answer()
    await show_home(callback)


@dp.callback_query(F.data == "about")
async def about(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_text(
        "Автоальянс86KG — сервис по подбору и поставке автомобилей Changan под заказ.\n\n"
        "Мы помогаем клиентам подобрать автомобиль, проверить комплектацию, организовать выкуп, доставку и сопровождение сделки.\n\n"
        "Основное направление:\n"
        "Changan под заказ.\n\n"
        "Что входит в работу:\n"
        "Подбор автомобиля\n"
        "Проверка комплектации\n"
        "Выкуп\n"
        "Доставка\n"
        "Таможенное сопровождение\n"
        "Консультация на всех этапах",
        reply_markup=back_menu()
    )


@dp.callback_query(F.data == "models")
async def models(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_text(
        "Выберите интересующую модель Changan:",
        reply_markup=models_menu()
    )


@dp.callback_query(F.data == "price")
async def price(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_text(
        "Стоимость автомобиля Changan зависит от модели, комплектации, года выпуска, курса валют и доставки.\n\n"
        "Чтобы подготовить точный расчёт, оставьте заявку. Менеджер свяжется с вами и подготовит актуальное предложение.",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Оставить заявку", callback_data="lead_start")],
            [InlineKeyboardButton(text="Назад", callback_data="home")]
        ])
    )


@dp.callback_query(F.data == "manager")
async def manager(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_text(
        f"Менеджер Автоальянс86KG:\n{MANAGER_PHONE}\n\n"
        "Также вы можете оставить заявку через бота, чтобы мы не потеряли ваш запрос.",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Оставить заявку", callback_data="lead_start")],
            [InlineKeyboardButton(text="Назад", callback_data="home")]
        ])
    )


@dp.callback_query(F.data == "lead_start")
async def lead_start(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(LeadForm.model)
    await callback.answer()
    await callback.message.edit_text(
        "Оформим заявку на подбор Changan.\n\n"
        "Выберите модель:",
        reply_markup=models_menu()
    )


@dp.callback_query(F.data.startswith("model:"))
async def choose_model(callback: CallbackQuery, state: FSMContext):
    model = callback.data.replace("model:", "")
    await state.update_data(model=model)
    await state.set_state(LeadForm.budget)
    await callback.answer()
    await callback.message.edit_text(
        f"Модель: {model}\n\n"
        "Укажите ваш бюджет.\n"
        "Например: до 25 000 долларов"
    )


@dp.message(LeadForm.budget)
async def get_budget(message: Message, state: FSMContext):
    await state.update_data(budget=message.text)
    await state.set_state(LeadForm.city)
    await message.answer("Укажите город доставки.\nНапример: Бишкек")


@dp.message(LeadForm.city)
async def get_city(message: Message, state: FSMContext):
    await state.update_data(city=message.text)
    await state.set_state(LeadForm.phone)
    await message.answer("Укажите номер телефона для связи.\nНапример: +996 555 123 456")


@dp.message(LeadForm.phone)
async def get_phone(message: Message, state: FSMContext):
    await state.update_data(phone=message.text)
    await state.set_state(LeadForm.comment)
    await message.answer(
        "Добавьте комментарий к заказу.\n\n"
        "Например: цвет, комплектация, сроки.\n"
        "Если комментария нет, напишите: нет"
    )


@dp.message(LeadForm.comment)
async def get_comment(message: Message, state: FSMContext):
    await state.update_data(comment=message.text)
    data = await state.get_data()
    user = message.from_user
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
    INSERT INTO leads (
        created_at, client_name, username, telegram_id,
        model, budget, city, phone, comment, status
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        created_at,
        user.full_name,
        user.username,
        str(user.id),
        data.get("model"),
        data.get("budget"),
        data.get("city"),
        data.get("phone"),
        data.get("comment"),
        "new"
    ))
    db.commit()

    lead_id = cursor.lastrowid

    manager_text = (
        f"Новая заявка #{lead_id}\n\n"
        f"Дата: {created_at}\n"
        f"Имя: {user.full_name}\n"
        f"Username: @{user.username}\n"
        f"Telegram ID: {user.id}\n\n"
        f"Модель: {data.get('model')}\n"
        f"Бюджет: {data.get('budget')}\n"
        f"Город: {data.get('city')}\n"
        f"Телефон: {data.get('phone')}\n"
        f"Комментарий: {data.get('comment')}\n\n"
        f"Статус: новая заявка"
    )

    await send_to_manager(manager_text)

    await message.answer(
        "Спасибо. Ваша заявка принята.\n\n"
        "Менеджер Автоальянс86KG свяжется с вами и подготовит варианты Changan под ваш запрос.",
        reply_markup=main_menu()
    )

    await state.clear()


@dp.message()
async def auto_reply(message: Message):
    text = message.text.lower() if message.text else ""

    if "цена" in text or "стоимость" in text or "сколько" in text:
        await message.answer(
            "Стоимость зависит от модели, комплектации и доставки.\n\n"
            "Для точного расчёта нажмите «Оставить заявку».",
            reply_markup=main_menu()
        )
    elif "номер" in text or "телефон" in text or "менеджер" in text:
        await message.answer(
            f"Телефон менеджера:\n{MANAGER_PHONE}\n\n"
            "Также можете оставить заявку через меню.",
            reply_markup=main_menu()
        )
    elif "uni" in text or "чанган" in text or "changan" in text:
        await message.answer(
            "Мы работаем с автомобилями Changan под заказ.\n\n"
            "Оставьте заявку, и менеджер подготовит варианты под ваш бюджет.",
            reply_markup=main_menu()
        )
    else:
        await message.answer(
            "Ваше сообщение получено.\n\n"
            "Для быстрого подбора автомобиля нажмите «Оставить заявку».",
            reply_markup=main_menu()
        )


async def main():
    print("Бот запущен")
    print("Команда для проверки ID: /id")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())