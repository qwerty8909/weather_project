import requests
from requests.exceptions import ConnectionError
from aiogram import Bot
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from weather_bot.keyboards import keyboards
from weather_bot.states.states import WeatherStates


# команда /start
async def start_command(message: Message, bot: Bot):
    await message.answer(
        text=f"Здравствуйте, {message.from_user.first_name}! \n"
             f"Нажми кнопку 'Узнать погоду', чтобы узнать прогноз погоды.",
        reply_markup=keyboards.main_kb
    )


# действие при нажатии кнопки 'Узнать погоду'
async def ask_city(message: Message, bot: Bot, state: FSMContext):
    await state.set_state(WeatherStates.waiting_for_city)
    await message.answer(
        text="Отправь мне название города, чтобы узнать погоду.",
        reply_markup=keyboards.del_kb
    )


async def get_weather(message: Message, bot: Bot, state: FSMContext):
    city_name = message.text.lower()
    api_url = 'http://127.0.0.1:8000/weather/'

    try:
        # Отправляем GET-запрос на ваш сервер с параметром city
        response = requests.get(api_url, params={'city': city_name})

        if response.status_code == 200:
            weather_data = response.json()
            response_text = f"Температура: {weather_data['temperature']}°C\n" \
                            f"Давление: {weather_data['pressure']} мм рт. ст.\n" \
                            f"Ветер: {weather_data['wind_speed']} м/с"
        else:
            response_text = "Ошибка при получении данных о погоде."
    except ConnectionError:
        response_text = "Сервер недоступен."

    await message.answer(
        text=response_text,
        reply_markup=keyboards.main_kb
    )
    await state.clear()


# любой текст кроме соответствующего условиям
async def default_message(message: Message, bot: Bot):
    await message.answer(
        text="Чтобы узнать погоду сперва нажмите кнопку 'Узнать погоду'",
        reply_markup=keyboards.main_kb
    )