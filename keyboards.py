from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


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


def lead_or_back_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Оставить заявку", callback_data="lead_start")],
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
        [InlineKeyboardButton(text="Нужна консультация", callback_data="country:Нужна консультация")],
        [InlineKeyboardButton(text="Назад", callback_data="home")]
    ])
