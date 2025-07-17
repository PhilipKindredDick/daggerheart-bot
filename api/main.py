from fastapi import FastAPI, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database.database import get_db, init_db
from database.models import Character, GameSession
from api.routes import character, game
from config.settings import settings
import uvicorn
import logging
import os

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Создание FastAPI приложения
app = FastAPI(
    title="Daggerheart Bot API",
    description="API для телеграм-бота игры Daggerheart",
    version="1.0.0"
)

# Настройка CORS
allowed_origins = [
    "https://web.telegram.org",
    "https://telegram.org",
    "https://*.ngrok.io",
    "https://*.ngrok-free.app",
    "https://*.railway.app",
    "https://*.render.com",
    "https://*.herokuapp.com"
]

if settings.API_HOST == "localhost":
    allowed_origins.extend(["http://localhost:*", "http://127.0.0.1:*"])

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение роутов
app.include_router(character.router, prefix="/api/character", tags=["character"])
app.include_router(game.router, prefix="/api/game", tags=["game"])

# Статические файлы для веб-приложения
app.mount("/webapp", StaticFiles(directory="webapp", html=True), name="webapp")


@app.get("/")
async def root():
    """Главная страница API"""
    return {
        "message": "Daggerheart Bot API",
        "version": "1.0.0",
        "docs": "/docs",
        "webapp": "/webapp"
    }


@app.get("/webapp")
async def webapp_redirect():
    """Редирект на главную страницу веб-приложения"""
    return FileResponse("webapp/index.html")


@app.get("/webapp/")
async def webapp_index():
    """Главная страница веб-приложения"""
    return FileResponse("webapp/index.html")


@app.get("/health")
async def health_check():
    """Проверка состояния API"""
    return {
        "status": "healthy",
        "database": "connected"
    }


@app.on_event("startup")
async def startup_event():
    """Инициализация при запуске"""
    logger.info("Запуск Daggerheart Bot API...")

    # Инициализация базы данных
    await init_db()

    logger.info("API успешно запущен!")


@app.on_event("shutdown")
async def shutdown_event():
    """Очистка при остановке"""
    logger.info("Остановка Daggerheart Bot API...")


if __name__ == "__main__":
    uvicorn.run(
        "api.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=True,
        log_level="info"
    )