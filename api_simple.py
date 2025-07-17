from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
import json
import os
import httpx
import random
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Создание FastAPI приложения
app = FastAPI(
    title="Daggerheart Bot API (Simple)",
    description="Упрощенная версия API для телеграм-бота игры Daggerheart",
    version="1.0.0"
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://web.telegram.org",
        "https://telegram.org",
        "*"  # Для разработки
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Временное хранилище данных (в продакшене заменить на БД)
characters_storage = {}
game_sessions_storage = {}


# Pydantic модели
class CharacterCreate(BaseModel):
    name: str
    character_class: str = Field(..., alias="class")
    ancestry: str
    userId: int


class DiceRollRequest(BaseModel):
    characterId: int
    userId: int
    actionType: Optional[str] = "general"
    difficulty: Optional[int] = 12


class GameStartRequest(BaseModel):
    characterId: int
    userId: int


# Статические файлы для веб-приложения
app.mount("/webapp", StaticFiles(directory="webapp", html=True), name="webapp")


@app.get("/")
async def root():
    """Главная страница API"""
    return {
        "message": "Daggerheart Bot API (Simple)",
        "version": "1.0.0",
        "docs": "/docs",
        "webapp": "/webapp"
    }


@app.get("/webapp")
async def webapp_redirect():
    """Редирект на главную страницу веб-приложения"""
    return FileResponse("webapp/index.html")


@app.get("/health")
async def health_check():
    """Проверка состояния API"""
    return {
        "status": "healthy",
        "database": "memory_storage"
    }


@app.post("/api/character/")
async def create_character(character_data: CharacterCreate):
    """Создание нового персонажа"""
    try:
        character_id = len(characters_storage) + 1

        # Базовые характеристики по классам
        class_stats = {
            "warrior": {"agility": 1, "strength": 2, "hit_points": 25},
            "ranger": {"agility": 2, "strength": 1, "hit_points": 22},
            "guardian": {"agility": 0, "strength": 1, "hit_points": 28},
            "seraph": {"agility": 1, "strength": 0, "hit_points": 20},
            "sorcerer": {"agility": 0, "strength": 0, "hit_points": 18},
            "wizard": {"agility": 0, "strength": 0, "hit_points": 16}
        }

        stats = class_stats.get(character_data.character_class, {"agility": 1, "strength": 1, "hit_points": 20})

        character = {
            "id": character_id,
            "user_id": character_data.userId,
            "name": character_data.name,
            "class": character_data.character_class,
            "ancestry": character_data.ancestry,
            "hope": 5,
            "fear": 3,
            "agility": stats["agility"],
            "strength": stats["strength"],
            "finesse": 1,
            "instinct": 1,
            "presence": 1,
            "knowledge": 1,
            "armor_score": 0,
            "hit_points": stats["hit_points"],
            "current_hit_points": stats["hit_points"],
            "stress": 0,
            "abilities": [],
            "equipment": [],
            "spells": [],
            "is_active": True
        }

        characters_storage[character_id] = character

        return {
            "success": True,
            "message": "Персонаж создан успешно",
            "character": character
        }

    except Exception as e:
        logger.error(f"Ошибка создания персонажа: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка создания персонажа: {str(e)}")


@app.get("/api/character/{user_id}")
async def get_character(user_id: int):
    """Получение персонажа пользователя"""
    try:
        # Ищем персонажа по user_id
        for character in characters_storage.values():
            if character["user_id"] == user_id and character["is_active"]:
                return {
                    "success": True,
                    "message": "Персонаж найден",
                    "character": character
                }

        return {
            "success": False,
            "message": "Персонаж не найден"
        }

    except Exception as e:
        logger.error(f"Ошибка получения персонажа: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка получения персонажа: {str(e)}")


@app.post("/api/game/start")
async def start_game(request: GameStartRequest):
    """Начало игровой сессии"""
    try:
        # Находим персонажа
        character = None
        for char in characters_storage.values():
            if char["id"] == request.characterId and char["user_id"] == request.userId:
                character = char
                break

        if not character:
            raise HTTPException(status_code=404, detail="Персонаж не найден")

        # Создаем игровую сессию
        session_id = len(game_sessions_storage) + 1
        session = {
            "id": session_id,
            "user_id": request.userId,
            "character_id": request.characterId,
            "is_active": True,
            "current_scene": "Начало приключения"
        }

        game_sessions_storage[session_id] = session

        # Генерируем начальное повествование
        narratives = [
            f"Приветствую, {character['name']}! Ты стоишь на пороге великого приключения. Перед тобой расстилается мир, полный тайн и опасностей.",
            f"Твоя история начинается здесь, {character['name']}. Магия этого мира уже чувствует твое присутствие...",
            f"Добро пожаловать в мир Daggerheart, {character['name']}! Твой путь героя только начинается."
        ]

        narrative = random.choice(narratives)

        return {
            "success": True,
            "message": "Игровая сессия начата",
            "narrative": narrative,
            "character": character,
            "game_state": session
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка начала игровой сессии: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка начала игровой сессии: {str(e)}")


@app.post("/api/game/roll-dice")
async def roll_dice(request: DiceRollRequest):
    """Бросок костей"""
    try:
        # Находим персонажа
        character = None
        for char in characters_storage.values():
            if char["id"] == request.characterId and char["user_id"] == request.userId:
                character = char
                break

        if not character:
            raise HTTPException(status_code=404, detail="Персонаж не найден")

        # Бросаем кости
        hope_die = random.randint(1, 12)
        fear_die = random.randint(1, 12)
        total = max(hope_die, fear_die)
        success = total >= request.difficulty

        # Обновляем Hope и Fear
        if success:
            character["hope"] = min(10, character["hope"] + 1)
        else:
            character["fear"] = min(10, character["fear"] + 1)

        # Генерируем описание результата
        if success:
            narratives = [
                f"Отличный бросок! (Hope: {hope_die}, Fear: {fear_die}) Твое действие увенчалось успехом!",
                f"Удача на твоей стороне! Результат {total} превышает сложность {request.difficulty}.",
                f"Превосходно! Боги благосклонны к тебе в этот момент."
            ]
        else:
            narratives = [
                f"Не все прошло гладко... (Hope: {hope_die}, Fear: {fear_die}) Но это лишь новая возможность для роста!",
                f"Результат {total} недостаточен, но неудачи делают нас сильнее!",
                f"Испытание оказалось сложнее ожидаемого, но твой дух не сломлен!"
            ]

        narrative = random.choice(narratives)

        return {
            "success": True,
            "message": "Кости брошены",
            "narrative": narrative,
            "character": character
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка броска костей: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка броска костей: {str(e)}")


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)