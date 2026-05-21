import asyncio
import os
import csv

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv

from texts import WELCOME_TEXT, ABOUT_TEXT, PRICE_TEXT, COUNTRIES_TEXT
from keyboards import main_menu, back_menu, lead_or_back_menu, brands_menu, countries_menu
from database import (
    create_lead,
    get_last_leads,
    get_new_leads,
    get_stats,
    update_lead_status,
    get_lead_by_id,
    get_all_leads,
)

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
MANAGER_CHAT_ID = os.getenv("MANAGER_CHAT_ID")
MANAGER_PHONE = os.getenv("MANAGER_PHONE", "+996 XXX XX XX XX")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не найден в .env")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())


class LeadForm(StatesGroup):
    brand = State()
    model = State()
    year = State()
    budget = State()
    source_country = State()
    delivery_city = State()
    phone = State()
    comment = State()


async def send_to_manager(text: str):
    if not MANAGER_CHAT_ID:
        print("MANAGER_CHAT_ID не указан")
        print(text)
        return

    try:
        await bot.send_message(int(MANAGER_CHAT_ID), text)
    except Exception as e:
        print("Ошибка отправки менеджеру:", e)
        print(text)


def is_manager(message: Message) -> bool:
    return str(message.from_user.id) == str(MANAGER_CHAT_ID)


async def send_new_message(callback: CallbackQuery, text: str, reply_markup=None):
    await callback.answer()

    try:
        await callback.message.delete()
    except Exception:
        pass

    await callback.message.answer(text, reply_markup=reply_markup)


async def show_home(target):
    photo = FSInputFile("welcome.jpg")

    if isinstance(target, Message):
        await target.answer_photo(
            photo=photo,
            caption=WELCOME_TEXT,
            reply_markup=main_menu()
        )
    else:
        await target.answer()

        try:
            await target.message.delete()
        except Exception:
            pass

        await target.message.answer_photo(
            photo=photo,
            caption=WELCOME_TEXT,
            reply_markup=main_menu()
        )


@dp.message(CommandStart())
async def start(message: Message, state: FSMContext):
    await state.clear()
    await show_home(message)


@dp.message(Command("id"))
async def get_id(message: Message):
    await message.answer(f"Ваш Telegram ID:\n{message.from_user.id}")


@dp.message(Command("leads"))
async def show_leads(message: Message):
    if not is_manager(message):
        await message.answer("У вас нет доступа к заявкам.")
        return

    rows = get_last_leads()

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


@dp.message(Command("new"))
async def show_new_leads(message: Message):
    if not is_manager(message):
        await message.answer("У вас нет доступа.")
        return

    rows = get_new_leads()

    if not rows:
        await message.answer("Новых заявок нет.")
        return

    text = "Новые заявки:\n\n"

    for row in rows:
        text += (
            f"Заявка #{row[0]}\n"
            f"Дата: {row[1]}\n"
            f"Клиент: {row[2]}\n"
            f"Марка: {row[3]}\n"
            f"Модель: {row[4]}\n"
            f"Бюджет: {row[5]}\n"
            f"Поставка: {row[6]}\n"
            f"Город: {row[7]}\n"
            f"Телефон: {row[8]}\n"
            f"Статус: {row[9]}\n\n"
        )

    await message.answer(text)


@dp.message(Command("stats"))
async def stats(message: Message):
    if not is_manager(message):
        await message.answer("У вас нет доступа.")
        return

    data = get_stats()

    await message.answer(
        "Статистика заявок:\n\n"
        f"Всего заявок: {data['total']}\n"
        f"Новые заявки: {data['new']}"
    )


@dp.message(Command("lead"))
async def show_lead(message: Message):
    if not is_manager(message):
        await message.answer("У вас нет доступа.")
        return

    parts = message.text.split()

    if len(parts) != 2 or not parts[1].isdigit():
        await message.answer("Укажите номер заявки. Например: /lead 1")
        return

    lead_id = int(parts[1])
    lead = get_lead_by_id(lead_id)

    if not lead:
        await message.answer(f"Заявка #{lead_id} не найдена.")
        return

    text = (
        f"Заявка #{lead[0]}\n\n"
        f"Дата: {lead[1]}\n"
        f"Клиент: {lead[2]}\n"
        f"Username: @{lead[3]}\n"
        f"Telegram ID: {lead[4]}\n\n"
        f"Марка: {lead[5]}\n"
        f"Модель: {lead[6]}\n"
        f"Год: {lead[7]}\n"
        f"Бюджет: {lead[8]}\n"
        f"Страна поставки: {lead[9]}\n"
        f"Город доставки: {lead[10]}\n"
        f"Телефон: {lead[11]}\n"
        f"Комментарий: {lead[12]}\n\n"
        f"Статус: {lead[13]}"
    )

    await message.answer(text)


@dp.message(Command("export"))
async def export_leads(message: Message):
    if not is_manager(message):
        await message.answer("У вас нет доступа.")
        return

    rows = get_all_leads()

    if not rows:
        await message.answer("Заявок пока нет.")
        return

    file_path = "leads_export.csv"

    with open(file_path, "w", newline="", encoding="utf-8-sig") as file:
        writer = csv.writer(file)

        writer.writerow([
            "ID", "Дата", "Клиент", "Username", "Telegram ID",
            "Марка", "Модель", "Год", "Бюджет",
            "Страна поставки", "Город доставки",
            "Телефон", "Комментарий", "Статус"
        ])

        writer.writerows(rows)

    await message.answer_document(
        FSInputFile(file_path),
        caption="Экспорт заявок"
    )


async def change_status(message: Message, status: str, status_name: str):
    if not is_manager(message):
        await message.answer("У вас нет доступа.")
        return

    parts = message.text.split()

    if len(parts) != 2 or not parts[1].isdigit():
        await message.answer("Укажите номер заявки. Например: /work 1")
        return

    lead_id = int(parts[1])
    result = update_lead_status(lead_id, status)

    if result:
        await message.answer(f"Заявка #{lead_id} переведена в статус: {status_name}")
    else:
        await message.answer(f"Заявка #{lead_id} не найдена.")


@dp.message(Command("work"))
async def work_lead(message: Message):
    await change_status(message, "in_progress", "в работе")


@dp.message(Command("done"))
async def done_lead(message: Message):
    await change_status(message, "completed", "завершена")


@dp.message(Command("cancel"))
async def cancel_lead(message: Message):
    await change_status(message, "canceled", "отменена")


@dp.callback_query(F.data == "home")
async def home(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await show_home(callback)


@dp.callback_query(F.data == "about")
async def about(callback: CallbackQuery):
    await send_new_message(callback, ABOUT_TEXT, back_menu())


@dp.callback_query(F.data == "countries")
async def countries(callback: CallbackQuery):
    await send_new_message(callback, COUNTRIES_TEXT, lead_or_back_menu())


@dp.callback_query(F.data == "price")
async def price(callback: CallbackQuery):
    await send_new_message(callback, PRICE_TEXT, lead_or_back_menu())


@dp.callback_query(F.data == "manager")
async def manager(callback: CallbackQuery):
    text = (
        f"Менеджер Автоальянс86KG:\n{MANAGER_PHONE}\n\n"
        "Также вы можете оставить заявку через бота, чтобы менеджер получил всю информацию сразу."
    )

    await send_new_message(callback, text, lead_or_back_menu())


@dp.callback_query(F.data == "lead_start")
async def lead_start(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(LeadForm.brand)

    await send_new_message(
        callback,
        "Оформим заявку на подбор автомобиля.\n\nВыберите марку:",
        brands_menu()
    )


@dp.callback_query(F.data.startswith("brand:"))
async def choose_brand(callback: CallbackQuery, state: FSMContext):
    brand = callback.data.replace("brand:", "")

    await state.update_data(brand=brand)
    await state.set_state(LeadForm.model)

    await send_new_message(
        callback,
        f"Марка: {brand}\n\n"
        "Введите модель автомобиля.\n"
        "Например: Camry, RX 350, X5, E-Class, Sonata"
    )


@dp.message(LeadForm.model)
async def get_model(message: Message, state: FSMContext):
    await state.update_data(model=message.text)
    await state.set_state(LeadForm.year)

    await message.answer(
        "Укажите желаемый год выпуска.\n"
        "Например: 2022 или 2023-2024"
    )


@dp.message(LeadForm.year)
async def get_year(message: Message, state: FSMContext):
    await state.update_data(year=message.text)
    await state.set_state(LeadForm.budget)

    await message.answer(
        "Укажите ваш бюджет.\n"
        "Например: до 25 000 долларов"
    )


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

    await send_new_message(
        callback,
        f"Страна поставки: {country}\n\n"
        "Укажите город доставки.\n"
        "Например: Бишкек, Ош, Алматы"
    )


@dp.message(LeadForm.delivery_city)
async def get_delivery_city(message: Message, state: FSMContext):
    await state.update_data(delivery_city=message.text)
    await state.set_state(LeadForm.phone)

    await message.answer(
        "Укажите номер телефона для связи.\n"
        "Например: +996 555 123 456"
    )


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

    lead_id = create_lead(
        client_name=user.full_name,
        username=user.username,
        telegram_id=str(user.id),
        brand=data.get("brand"),
        model=data.get("model"),
        year=data.get("year"),
        budget=data.get("budget"),
        source_country=data.get("source_country"),
        delivery_city=data.get("delivery_city"),
        phone=data.get("phone"),
        comment=data.get("comment"),
    )

    manager_text = (
        f"Новая заявка #{lead_id}\n\n"
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