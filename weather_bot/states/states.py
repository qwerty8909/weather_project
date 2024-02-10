from aiogram.fsm.state import StatesGroup, State


class WeatherStates(StatesGroup):
    waiting_for_city = State()
