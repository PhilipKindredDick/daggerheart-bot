import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import WebAppInfo, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.client.session.aiohttp import AiohttpSession
from config.settings import settings

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Создание бота и диспетчера
bot = Bot(token=settings.BOT_TOKEN)
dp = Dispatcher()


@dp.message(Command("start"))
async def start_handler(message: types.Message):
    """Обработчик команды /start"""
    user_name = message.from_user.first_name or "Искатель приключений"

    # Создаем клавиатуру с кнопкой для запуска Mini App
    webapp_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🎲 Начать игру в Daggerheart",
                    web_app=WebAppInfo(url=f"{settings.WEBAPP_URL}")
                )
            ]
        ]
    )

    welcome_text = f"""
🗡️ Добро пожаловать в мир Daggerheart, {user_name}!

Этот бот поможет тебе окунуться в захватывающие приключения в мире, где магия переплетается с опасностями, а твои решения определяют судьбу персонажа.

✨ **Что тебя ждет:**
• Создание уникального персонажа
• Интерактивные приключения с ИИ Мастером
• Система двойных костей и Hope/Fear
• Увлекательные квесты и сражения

Нажми кнопку ниже, чтобы начать свое приключение!
    """

    await message.answer(
        text=welcome_text,
        reply_markup=webapp_keyboard
    )


@dp.message(Command("help"))
async def help_handler(message: types.Message):
    """Обработчик команды /help"""
    help_text = """
🎯 **Команды бота:**

/start - Начать игру
/help - Показать это сообщение
/profile - Посмотреть профиль персонажа
/new_game - Начать новую игру

🎲 **Как играть:**
1. Нажми кнопку "Начать игру в Daggerheart"
2. Создай своего персонажа
3. Следуй указаниям ИИ Мастера
4. Принимай решения и кидай кости!

Удачи в приключениях! ⚔️
    """
    await message.answer(help_text)


@dp.message(Command("profile"))
async def profile_handler(message: types.Message):
    """Показать профиль персонажа"""
    # TODO: Получить данные персонажа из API
    await message.answer("🔮 Профиль персонажа пока в разработке...")


@dp.message(Command("new_game"))
async def new_game_handler(message: types.Message):
    """Начать новую игру"""
    webapp_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🎲 Создать нового персонажа",
                    web_app=WebAppInfo(url=f"{settings.WEBAPP_URL}/new_character")
                )
            ]
        ]
    )

    await message.answer(
        "🆕 Начинаем новую игру! Создай своего персонажа:",
        reply_markup=webapp_keyboard
    )


@dp.message()
async def echo_handler(message: types.Message):
    """Обработчик всех остальных сообщений"""
    await message.answer(
        "🎲 Используй команды бота или нажми на кнопку Mini App для игры!\n\n"
        "Доступные команды: /start, /help, /profile, /new_game"
    )


async def main():
    """Основная функция запуска бота"""
    logger.info("Запуск Daggerheart бота...")

    # Удаляем все обновления, которые поступили, пока бот был оффлайн
    await bot.delete_webhook(drop_pending_updates=True)

    # Запускаем бота
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())