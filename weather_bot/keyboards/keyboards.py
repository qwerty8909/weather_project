from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

del_kb = ReplyKeyboardRemove()

main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Узнать погоду'), ]
    ],
    resize_keyboard=True)
