from aiogram import types
import emoji
from aiogram.types import ReplyKeyboardMarkup
from emoji import demojize


def show_big_menu() -> ReplyKeyboardMarkup:
    big_menu = types.ReplyKeyboardMarkup(resize_keyboard=True)
    big_menu.row(types.InlineKeyboardButton(text="Личные"),
                 types.InlineKeyboardButton(text="Входящие"),
                 types.InlineKeyboardButton(text="Участвую"),
                 types.InlineKeyboardButton(text="ВхВыполненные"))
    big_menu.row(types.InlineKeyboardButton(text="Исходящие"),
                 types.InlineKeyboardButton(text="Выполненные"),
                 types.InlineKeyboardButton(text=f"{emoji.emojize(':gear:')}"))
    return big_menu

