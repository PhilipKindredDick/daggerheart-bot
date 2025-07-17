#!/usr/bin/env python3
"""
Главный файл для запуска на Replit
"""

import os
import subprocess
import sys


def install_dependencies():
    """Установка зависимостей если их нет"""
    try:
        import uvicorn
        import fastapi
        print("✅ Зависимости уже установлены")
    except ImportError:
        print("📦 Устанавливаем зависимости...")
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "fastapi", "uvicorn", "httpx", "python-dotenv", "pydantic"])
        print("✅ Зависимости установлены!")


# Устанавливаем зависимости
install_dependencies()

# Импортируем FastAPI приложение из api_simple.py
from api_simple import app

# Экспортируем app для ASGI сервера
__all__ = ['app']

# Запускаем сервер если файл запущен напрямую
if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8000))
    host = "0.0.0.0"

    # Определяем Replit URL
    repl_slug = os.getenv('REPL_SLUG', 'daggerheart-bot')
    repl_owner = os.getenv('REPL_OWNER', 'username')
    replit_url = f"https://{repl_slug}.{repl_owner}.repl.co"

    print(f"🚀 Запуск Daggerheart API на {host}:{port}")
    print(f"📱 WebApp будет доступно по адресу: {replit_url}/webapp")

    uvicorn.run(app, host=host, port=port)