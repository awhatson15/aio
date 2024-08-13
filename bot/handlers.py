# bot/handlers.py

from aiogram import Router, types
from aiogram.filters import Command
from aiogram.filters.callback_data import CallbackData  # Обновленный импорт
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from config.config import SETTINGS, EXCHANGES

router = Router()

# CallbackData для обработки нажатий на кнопки
class SettingCallbackFactory(CallbackData, prefix="setting"):
    name: str
    value: str

# Основное меню
def main_menu():
    buttons = [
        [KeyboardButton(text="Настройки пары")],
        [KeyboardButton(text="Настройки стратегии")],
        [KeyboardButton(text="Настройки бирж")]
    ]
    keyboard = ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
    return keyboard

# Команда /start для отображения основного меню
@router.message(Command("start"))
async def start_command(message: types.Message):
    await message.answer("Добро пожаловать! Выберите действие из меню ниже:", reply_markup=main_menu())

# Обработка выбора в основном меню
@router.message(lambda message: message.text == "Настройки пары")
async def pair_settings(message: types.Message):
    await message.answer("Выберите опцию:", reply_markup=pair_menu())

@router.message(lambda message: message.text == "Настройки стратегии")
async def strategy_settings(message: types.Message):
    await message.answer("Выберите опцию:", reply_markup=strategy_menu())

@router.message(lambda message: message.text == "Настройки бирж")
async def exchange_settings(message: types.Message):
    await message.answer("Выберите биржу для настройки:", reply_markup=exchange_menu())

# Подменю для настройки пары
def pair_menu():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Изменить пару", callback_data=SettingCallbackFactory(name="pair", value="set").pack())]
    ])
    return keyboard

# Подменю для настройки стратегии
def strategy_menu():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Изменить порог разницы в цене", callback_data=SettingCallbackFactory(name="diff", value="set").pack())],
        [InlineKeyboardButton(text="Изменить скидку на покупку", callback_data=SettingCallbackFactory(name="discount", value="set").pack())],
        [InlineKeyboardButton(text="Изменить порог для продажи", callback_data=SettingCallbackFactory(name="sell_threshold", value="set").pack())],
        [InlineKeyboardButton(text="Изменить интервал проверки", callback_data=SettingCallbackFactory(name="interval", value="set").pack())]
    ])
    return keyboard

# Подменю для настройки бирж
def exchange_menu():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Изменить первую биржу", callback_data=SettingCallbackFactory(name="exchange1", value="set").pack())],
        [InlineKeyboardButton(text="Изменить вторую биржу", callback_data=SettingCallbackFactory(name="exchange2", value="set").pack())]
    ])
    return keyboard

# Обработка нажатий на Inline-кнопки
@router.callback_query(SettingCallbackFactory.filter())
async def process_setting_callback(callback_query: types.CallbackQuery, callback_data: SettingCallbackFactory):
    name = callback_data.name

    if name == "pair":
        await callback_query.message.answer("Введите новую торговую пару (например, BTC/USDT):")
    elif name == "diff":
        await callback_query.message.answer("Введите новый порог разницы в цене (например, 0.05 для 5%):")
    elif name == "discount":
        await callback_query.message.answer("Введите новую скидку на покупку (например, 0.30 для 30%):")
    elif name in ["exchange1", "exchange2"]:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=exchange, callback_data=SettingCallbackFactory(name=name, value=exchange).pack())]
            for exchange in EXCHANGES
        ])
        await callback_query.message.answer(f"Выберите {'первую' if name == 'exchange1' else 'вторую'} биржу:", reply_markup=keyboard)

    await callback_query.answer()

# Пример изменения значения на основе ответа пользователя
@router.message(lambda message: message.reply_to_message and "Введите" in message.reply_to_message.text)
async def receive_input(message: types.Message):
    if "Введите новую торговую пару" in message.reply_to_message.text:
        SETTINGS["base_currency"] = message.text.upper()
        await message.answer(f"Торговая пара изменена на {SETTINGS['base_currency']}.")
    elif "Введите новый порог разницы в цене" in message.reply_to_message.text:
        try:
            new_threshold = float(message.text)
            if 0 < new_threshold < 1:
                SETTINGS["price_diff_threshold"] = new_threshold
                await message.answer(f"Порог разницы в цене установлен на {new_threshold * 100}%.")
            else:
                await message.answer("Пожалуйста, введите значение между 0 и 1.")
        except ValueError:
            await message.answer("Пожалуйста, введите корректное значение.")
    elif "Введите новую скидку на покупку" in message.reply_to_message.text:
        try:
            new_discount = float(message.text)
            if 0 < new_discount < 1:
                SETTINGS["buy_discount"] = new_discount
                await message.answer(f"Скидка на покупку установлена на {new_discount * 100}%.")
            else:
                await message.answer("Пожалуйста, введите значение между 0 и 1.")
        except ValueError:
            await message.answer("Пожалуйста, введите корректное значение.")
    elif "Введите новый порог для продажи" in message.reply_to_message.text:
        try:
            new_threshold = float(message.text)
            if 0 < new_threshold < 1:
                SETTINGS["sell_threshold"] = new_threshold
                await message.answer(f"Порог для продажи установлен на {new_threshold * 100}%.")
            else:
                await message.answer("Пожалуйста, введите значение между 0 и 1.")
        except ValueError:
            await message.answer("Пожалуйста, введите корректное значение.")
    elif "Введите новый интервал проверки" in message.reply_to_message.text:
        try:
            new_interval = int(message.text)
            if new_interval > 0:
                SETTINGS["check_interval"] = new_interval
                await message.answer(f"Интервал проверки установлен на {new_interval} секунд.")
            else:
                await message.answer("Пожалуйста, введите положительное целое число.")
        except ValueError:
            await message.answer("Пожалуйста, введите корректное значение.")
