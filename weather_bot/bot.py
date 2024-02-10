import asyncio
import logging
import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.fsm.storage.memory import MemoryStorage
from keyboards import commands
from handlers import basic
from states.states import WeatherStates

# Загрузка переменных из файла .env
load_dotenv()
# Initialize logger
logger = logging.getLogger(__name__)


async def start_bot(bot: Bot):
    logger.info('Starting bot')
    await commands.set_commands(bot)
    await bot.send_message(os.getenv('TG_ADMIN_ID'), text='Bot started successfully')


async def stop_bot(bot: Bot):
    logger.info('Ending bot')
    await bot.send_message(os.getenv('TG_ADMIN_ID'), text='Bot STOPPED')


async def start():
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - [%(levelname)s] - %(name)s - '
                               '(%(filename)s).%(funcName)s(%(lineno)d) - %(message)s')

    # Initialize bot and dispatcher
    storage = MemoryStorage()
    bot = Bot(token=os.getenv('TELEGRAM_BOT_TOKEN'), parse_mode="HTML")
    dp = Dispatcher(storage=storage)

    # Register startup and shutdown handlers
    dp.startup.register(start_bot)
    dp.shutdown.register(stop_bot)

    # Register in the dispatcher
    dp.message.register(basic.start_command, CommandStart())
    dp.message.register(basic.ask_city, F.text == "Узнать погоду")
    dp.message.register(basic.get_weather, WeatherStates.waiting_for_city)
    dp.message.register(basic.default_message)

    # Delete webhook and start polling
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(start())