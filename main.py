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
    brand TEXT,
    model TEXT,
    year TEXT,
    budget TEXT,
    source_country TEXT,
    delivery_city TEXT,
    phone TEXT,
    comment TEXT,
    status TEXT
)
""")
db.commit()


class LeadForm(StatesGroup):
    brand = State()
    model = State()
    year = State()
    budget = State()
    source_country = State()
    delivery_city = State()
    phone = State()
    comment = State()


def main_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Оставить заявку", callback_data="lead_start")],
        [InlineKeyboardButton(text="Узнать стоимость", callback_data="price")],
        [InlineKeyboardButton(text="Страны поставки", callback_data="countries")],
        [InlineKeyboardButton(text="О компании", callback_data="about")],
        [InlineKeyboardButton(text="Связаться с менеджером", callback_data="manager")]
    ])


def back_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Назад", callback_data="home")]
    ])


def brands_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Toyota", callback_data="brand:Toyota")],
        [InlineKeyboardButton(text="Lexus", callback_data="brand:Lexus")],
        [InlineKeyboardButton(text="BMW", callback_data="brand:BMW")],
        [InlineKeyboardButton(text="Mercedes-Benz", callback_data="brand:Mercedes-Benz")],
        [InlineKeyboardButton(text="KIA", callback_data="brand:KIA")],
        [InlineKeyboardButton(text="Hyundai", callback_data="brand:Hyundai")],
        [InlineKeyboardButton(text="Changan", callback_data="brand:Changan")],
        [InlineKeyboardButton(text="BYD", callback_data="brand:BYD")],
        [InlineKeyboardButton(text="Другая марка", callback_data="brand:Другая марка")],
        [InlineKeyboardButton(text="Назад", callback_data="home")]
    ])


def countries_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Китай", callback_data="country:Китай")],
        [InlineKeyboardButton(text="Корея", callback_data="country:Корея")],
        [InlineKeyboardButton(text="США", callback_data="country:США")],
        [InlineKeyboardButton(text="Дубай", callback_data="country:Дубай")],
        [InlineKeyboardButton(text="Грузия", callback_data="country:Грузия")],
        [InlineKeyboardButton(text="Европа", callback_data="country:Европа")],
        [InlineKeyboardButton(text="Не знаю, нужна консультация", callback_data="country:Нужна консультация")],
        [InlineKeyboardButton(text="Назад", callback_data="home")]
    ])


async def send_to_manager(text):
    if not MANAGER_CHAT_ID:
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
        "Подбор и поставка автомобилей под заказ из Китая, Кореи, США, Дубая, Грузии и Европы.\n\n"
        "Работаем со всеми марками автомобилей.\n\n"
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
    SELECT id, created_at, brand, model, budget, source_country, delivery_city, phone, status
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
            f"Марка: {row[2]}\n"
            f"Модель: {row[3]}\n"
            f"Бюджет: {row[4]}\n"
            f"Поставка: {row[5]}\n"
            f"Город: {row[6]}\n"
            f"Телефон: {row[7]}\n"
            f"Статус: {row[8]}\n\n"
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
        "Автоальянс86KG — сервис по подбору и поставке автомобилей под заказ.\n\n"
        "Мы помогаем клиентам подобрать автомобиль под бюджет, проверить комплектацию, организовать выкуп, доставку и сопровождение сделки.\n\n"
        "Работаем с направлениями:\n"
        "Китай, Корея, США, Дубай, Грузия, Европа.\n\n"
        "Что входит в работу:\n"
        "Подбор автомобиля\n"
        "Проверка автомобиля и комплектации\n"
        "Выкуп\n"
        "Доставка\n"
        "Таможенное сопровождение\n"
        "Консультация на всех этапах",
        reply_markup=back_menu()
    )


@dp.callback_query(F.data == "countries")
async def countries(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_text(
        "Доступные направления поставки:\n\n"
        "Китай\n"
        "Корея\n"
        "США\n"
        "Дубай\n"
        "Грузия\n"
        "Европа\n\n"
        "Если не знаете, откуда лучше заказать автомобиль, оставьте заявку. Менеджер подскажет оптимальный вариант.",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Оставить заявку", callback_data="lead_start")],
            [InlineKeyboardButton(text="Назад", callback_data="home")]
        ])
    )


@dp.callback_query(F.data == "price")
async def price(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_text(
        "Стоимость автомобиля зависит от марки, модели, года, комплектации, страны поставки, курса валют и доставки.\n\n"
        "Для точного расчёта оставьте короткую заявку.",
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
        "Также вы можете оставить заявку через бота, чтобы менеджер получил всю информацию сразу.",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Оставить заявку", callback_data="lead_start")],
            [InlineKeyboardButton(text="Назад", callback_data="home")]
        ])
    )


@dp.callback_query(F.data == "lead_start")
async def lead_start(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(LeadForm.brand)
    await callback.answer()
    await callback.message.edit_text(
        "Оформим заявку на подбор автомобиля.\n\n"
        "Выберите марку:",
        reply_markup=brands_menu()
    )


@dp.callback_query(F.data.startswith("brand:"))
async def choose_brand(callback: CallbackQuery, state: FSMContext):
    brand = callback.data.replace("brand:", "")
    await state.update_data(brand=brand)
    await state.set_state(LeadForm.model)
    await callback.answer()

    await callback.message.edit_text(
        f"Марка: {brand}\n\n"
        "Введите модель автомобиля.\n"
        "Например: Camry, RX 350, X5, E-Class, Sonata"
    )


@dp.message(LeadForm.model)
async def get_model(message: Message, state: FSMContext):
    await state.update_data(model=message.text)
    await state.set_state(LeadForm.year)
    await message.answer("Укажите желаемый год выпуска.\nНапример: 2022 или 2023-2024")


@dp.message(LeadForm.year)
async def get_year(message: Message, state: FSMContext):
    await state.update_data(year=message.text)
    await state.set_state(LeadForm.budget)
    await message.answer("Укажите ваш бюджет.\nНапример: до 25 000 долларов")


@dp.message(LeadForm.budget)
async def get_budget(message: Message, state: FSMContext):
    await state.update_data(budget=message.text)
    await state.set_state(LeadForm.source_country)
    await message.answer(
        "Выберите страну поставки:",
        reply_markup=countries_menu()
    )


@dp.callback_query(F.data.startswith("country:"))
async def choose_country(callback: CallbackQuery, state: FSMContext):
    country = callback.data.replace("country:", "")
    await state.update_data(source_country=country)
    await state.set_state(LeadForm.delivery_city)
    await callback.answer()

    await callback.message.edit_text(
        f"Страна поставки: {country}\n\n"
        "Укажите город доставки.\n"
        "Например: Бишкек, Ош, Алматы"
    )


@dp.message(LeadForm.delivery_city)
async def get_delivery_city(message: Message, state: FSMContext):
    await state.update_data(delivery_city=message.text)
    await state.set_state(LeadForm.phone)
    await message.answer("Укажите номер телефона для связи.\nНапример: +996 555 123 456")


@dp.message(LeadForm.phone)
async def get_phone(message: Message, state: FSMContext):
    await state.update_data(phone=message.text)
    await state.set_state(LeadForm.comment)
    await message.answer(
        "Добавьте комментарий к заказу.\n\n"
        "Например: цвет, комплектация, двигатель, сроки.\n"
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
        brand, model, year, budget, source_country,
        delivery_city, phone, comment, status
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        created_at,
        user.full_name,
        user.username,
        str(user.id),
        data.get("brand"),
        data.get("model"),
        data.get("year"),
        data.get("budget"),
        data.get("source_country"),
        data.get("delivery_city"),
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
        f"Марка: {data.get('brand')}\n"
        f"Модель: {data.get('model')}\n"
        f"Год: {data.get('year')}\n"
        f"Бюджет: {data.get('budget')}\n"
        f"Страна поставки: {data.get('source_country')}\n"
        f"Город доставки: {data.get('delivery_city')}\n"
        f"Телефон: {data.get('phone')}\n"
        f"Комментарий: {data.get('comment')}\n\n"
        f"Статус: новая заявка"
    )

    await send_to_manager(manager_text)

    await message.answer(
        "Спасибо. Ваша заявка принята.\n\n"
        "Менеджер Автоальянс86KG свяжется с вами и подготовит варианты под ваш запрос.",
        reply_markup=main_menu()
    )

    await state.clear()


@dp.message()
async def auto_reply(message: Message):
    text = message.text.lower() if message.text else ""

    await send_to_manager(
        "Новое сообщение от клиента\n\n"
        f"Имя: {message.from_user.full_name}\n"
        f"Username: @{message.from_user.username}\n"
        f"Telegram ID: {message.from_user.id}\n\n"
        f"Сообщение:\n{message.text}"
    )

    if "цена" in text or "стоимость" in text or "сколько" in text:
        await message.answer(
            "Стоимость зависит от марки, модели, года, комплектации, страны поставки и доставки.\n\n"
            "Для точного расчёта нажмите «Оставить заявку».",
            reply_markup=main_menu()
        )
    elif "менеджер" in text or "номер" in text or "телефон" in text:
        await message.answer(
            f"Телефон менеджера:\n{MANAGER_PHONE}\n\n"
            "Также можете оставить заявку через меню.",
            reply_markup=main_menu()
        )
    elif "китай" in text or "корея" in text or "сша" in text or "дубай" in text or "грузия" in text:
        await message.answer(
            "Мы работаем с поставками из Китая, Кореи, США, Дубая, Грузии и Европы.\n\n"
            "Оставьте заявку, и менеджер подскажет оптимальное направление под ваш бюджет.",
            reply_markup=main_menu()
        )
    else:
        await message.answer(
            "Ваше сообщение получено.\n\n"
            "Для быстрого расчёта и подбора автомобиля нажмите «Оставить заявку».",
            reply_markup=main_menu()
        )


async def main():
    print("Бот запущен")
    print("Команда для проверки ID: /id")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())