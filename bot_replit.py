#!/usr/bin/env python3
"""
Запуск Telegram бота для Replit
"""

import asyncio
import logging
import os
import sys
from pathlib import Path

# Добавляем корневую папку в PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent))

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import WebAppInfo, InlineKeyboardMarkup, InlineKeyboardButton

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Получаем токен из переменных окружения
BOT_TOKEN = os.getenv('BOT_TOKEN')
if not BOT_TOKEN:
    logger.error("BOT_TOKEN не найден в переменных окружения!")
    sys.exit(1)

# Создание бота и диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# URL Replit приложения (автоматически определяется)
REPL_SLUG = os.getenv('REPL_SLUG', 'daggerheart-bot')
REPL_OWNER = os.getenv('REPL_OWNER', 'username')
REPLIT_URL = f"https://{REPL_SLUG}.{REPL_OWNER}.repl.co"
WEBAPP_URL = f"{REPLIT_URL}/webapp"


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
                    web_app=WebAppInfo(url=WEBAPP_URL)
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
/info - Информация о проекте

🎲 **Как играть:**
1. Нажми кнопку "Начать игру в Daggerheart"
2. Создай своего персонажа в веб-приложении
3. Следуй указаниям ИИ Мастера
4. Принимай решения и кидай кости!

Удачи в приключениях! ⚔️
    """
    await message.answer(help_text)


@dp.message(Command("info"))
async def info_handler(message: types.Message):
    """Информация о проекте"""
    bot_info = await bot.get_me()
    info_text = f"""
ℹ️ **Информация о проекте:**

🤖 **Бот:** @{bot_info.username}
🌐 **API:** {REPLIT_URL}
📱 **WebApp:** {WEBAPP_URL}
🔗 **GitHub:** https://github.com/PhilipKindredDick/daggerheart-bot

🛠️ **Технологии:**
• Python + aiogram
• FastAPI
• Telegram Mini Apps
• Replit hosting

Версия: 1.0.0 (Replit)
Хост: {REPL_SLUG}.{REPL_OWNER}.repl.co
    """
    await message.answer(info_text)


@dp.message()
async def echo_handler(message: types.Message):
    """Обработчик всех остальных сообщений"""
    await message.answer(
        "🎲 Используй команды бота или нажми на кнопку Mini App для игры!\n\n"
        "Доступные команды: /start, /help, /info"
    )


async def main():
    """Основная функция запуска бота"""
    logger.info("🚀 Запуск Daggerheart бота (Replit)...")
    logger.info(f"📱 WebApp URL: {WEBAPP_URL}")
    logger.info(f"🌐 Replit URL: {REPLIT_URL}")

    # Удаляем все обновления, которые поступили, пока бот был оффлайн
    await bot.delete_webhook(drop_pending_updates=True)

    # Запускаем бота
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())