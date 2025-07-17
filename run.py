#!/usr/bin/env python3
"""
Скрипт запуска Daggerheart Telegram Bot
"""

import asyncio
import logging
import multiprocessing
import signal
import sys
from pathlib import Path

# Добавляем корневую папку в PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent))

from config.settings import settings

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('daggerheart_bot.log')
    ]
)

logger = logging.getLogger(__name__)


def run_bot():
    """Запуск телеграм бота"""
    try:
        from bot.main import main
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Телеграм бот остановлен пользователем")
    except Exception as e:
        logger.error(f"Ошибка запуска телеграм бота: {e}")


def run_api():
    """Запуск FastAPI сервера"""
    try:
        import uvicorn
        uvicorn.run(
            "api.main:app",
            host=settings.API_HOST,
            port=settings.API_PORT,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        logger.info("API сервер остановлен пользователем")
    except Exception as e:
        logger.error(f"Ошибка запуска API сервера: {e}")


def signal_handler(signum, frame):
    """Обработчик сигналов завершения"""
    logger.info("Получен сигнал завершения, останавливаем все процессы...")
    sys.exit(0)


def main():
    """Главная функция запуска"""
    logger.info("🎲 Запуск Daggerheart Telegram Bot...")

    # Проверяем наличие необходимых переменных окружения
    if not settings.BOT_TOKEN:
        logger.error("❌ BOT_TOKEN не найден в переменных окружения!")
        sys.exit(1)

    if not settings.DEEPSEEK_API_KEY:
        logger.error("❌ DEEPSEEK_API_KEY не найден в переменных окружения!")
        sys.exit(1)

    # Настраиваем обработчики сигналов
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        # Создаем процессы для бота и API
        bot_process = multiprocessing.Process(target=run_bot, name="TelegramBot")
        api_process = multiprocessing.Process(target=run_api, name="FastAPI")

        # Запускаем процессы
        logger.info("🚀 Запуск API сервера...")
        api_process.start()

        logger.info("🤖 Запуск Telegram бота...")
        bot_process.start()

        logger.info("✅ Все сервисы запущены успешно!")
        logger.info(f"📡 API доступно по адресу: http://{settings.API_HOST}:{settings.API_PORT}")
        logger.info(f"🌐 Web App доступно по адресу: http://{settings.API_HOST}:{settings.API_PORT}/webapp")
        logger.info("📚 API документация: http://localhost:8000/docs")
        logger.info("🛑 Для остановки нажмите Ctrl+C")

        # Ожидаем завершения процессов
        bot_process.join()
        api_process.join()

    except KeyboardInterrupt:
        logger.info("🛑 Получен сигнал остановки...")

        # Завершаем процессы
        if 'bot_process' in locals() and bot_process.is_alive():
            logger.info("🤖 Остановка Telegram бота...")
            bot_process.terminate()
            bot_process.join(timeout=5)

        if 'api_process' in locals() and api_process.is_alive():
            logger.info("📡 Остановка API сервера...")
            api_process.terminate()
            api_process.join(timeout=5)

        logger.info("✅ Все сервисы остановлены")

    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # Проверяем версию Python
    if sys.version_info < (3, 8):
        print("❌ Требуется Python 3.8 или выше")
        sys.exit(1)

    main()