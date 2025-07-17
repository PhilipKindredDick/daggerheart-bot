from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional
from database.database import get_db, create_character, get_character_by_user_id, get_character_by_id, update_character, \
    deactivate_user_characters
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


# Pydantic модели для валидации
class CharacterCreate(BaseModel):
    name: str
    character_class: str = Field(..., alias="class")  # Используем alias для "class"
    ancestry: str
    userId: int


class CharacterUpdate(BaseModel):
    name: Optional[str] = None
    hope: Optional[int] = None
    fear: Optional[int] = None
    agility: Optional[int] = None
    strength: Optional[int] = None
    finesse: Optional[int] = None
    instinct: Optional[int] = None
    presence: Optional[int] = None
    knowledge: Optional[int] = None
    armor_score: Optional[int] = None
    hit_points: Optional[int] = None
    current_hit_points: Optional[int] = None
    stress: Optional[int] = None


class CharacterResponse(BaseModel):
    success: bool
    message: str
    character: Optional[dict] = None


@router.post("/", response_model=CharacterResponse)
async def create_new_character(character_data: CharacterCreate, db: Session = Depends(get_db)):
    """Создание нового персонажа"""
    try:
        logger.info(f"Создание персонажа для пользователя {character_data.userId}")

        # Проверяем, есть ли уже активный персонаж у пользователя
        existing_character = get_character_by_user_id(db, character_data.userId)
        if existing_character:
            # Деактивируем старого персонажа
            deactivate_user_characters(db, character_data.userId)
            logger.info(f"Деактивирован старый персонаж пользователя {character_data.userId}")

        # Создаем нового персонажа
        character_dict = {
            "user_id": character_data.userId,
            "name": character_data.name,
            "class": character_data.character_class,
            "ancestry": character_data.ancestry
        }

        character = create_character(db, character_dict)

        # Устанавливаем начальные характеристики в зависимости от класса
        character = set_initial_stats(db, character, character_data.character_class, character_data.ancestry)

        logger.info(f"Персонаж {character.name} создан успешно")

        return CharacterResponse(
            success=True,
            message="Персонаж создан успешно",
            character=character.to_dict()
        )

    except Exception as e:
        logger.error(f"Ошибка создания персонажа: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка создания персонажа: {str(e)}")


@router.get("/{user_id}", response_model=CharacterResponse)
async def get_user_character(user_id: int, db: Session = Depends(get_db)):
    """Получение персонажа пользователя"""
    try:
        character = get_character_by_user_id(db, user_id)

        if not character:
            return CharacterResponse(
                success=False,
                message="Персонаж не найден"
            )

        return CharacterResponse(
            success=True,
            message="Персонаж найден",
            character=character.to_dict()
        )

    except Exception as e:
        logger.error(f"Ошибка получения персонажа: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка получения персонажа: {str(e)}")


@router.put("/{character_id}", response_model=CharacterResponse)
async def update_user_character(character_id: int, updates: CharacterUpdate, db: Session = Depends(get_db)):
    """Обновление персонажа"""
    try:
        character = get_character_by_id(db, character_id)

        if not character:
            raise HTTPException(status_code=404, detail="Персонаж не найден")

        # Подготавливаем обновления
        update_data = {k: v for k, v in updates.dict().items() if v is not None}

        # Проверяем ограничения
        if "hope" in update_data:
            update_data["hope"] = max(0, min(10, update_data["hope"]))
        if "fear" in update_data:
            update_data["fear"] = max(0, min(10, update_data["fear"]))

        updated_character = update_character(db, character_id, update_data)

        logger.info(f"Персонаж {character_id} обновлен")

        return CharacterResponse(
            success=True,
            message="Персонаж обновлен",
            character=updated_character.to_dict()
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка обновления персонажа: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка обновления персонажа: {str(e)}")


@router.delete("/{character_id}")
async def delete_character(character_id: int, db: Session = Depends(get_db)):
    """Удаление (деактивация) персонажа"""
    try:
        character = get_character_by_id(db, character_id)

        if not character:
            raise HTTPException(status_code=404, detail="Персонаж не найден")

        # Деактивируем персонажа вместо удаления
        update_character(db, character_id, {"is_active": False})

        logger.info(f"Персонаж {character_id} деактивирован")

        return {"success": True, "message": "Персонаж деактивирован"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка деактивации персонажа: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка деактивации персонажа: {str(e)}")


def set_initial_stats(db: Session, character, character_class: str, ancestry: str):
    """Установка начальных характеристик персонажа"""

    # Базовые характеристики по классам
    class_stats = {
        "warrior": {
            "agility": 1,
            "strength": 2,
            "finesse": 0,
            "instinct": 1,
            "presence": 0,
            "knowledge": 0,
            "hit_points": 25,
            "abilities": ["Combat Mastery", "Weapon Training"]
        },
        "ranger": {
            "agility": 2,
            "strength": 1,
            "finesse": 1,
            "instinct": 2,
            "presence": 0,
            "knowledge": 0,
            "hit_points": 22,
            "abilities": ["Nature's Bond", "Tracking"]
        },
        "guardian": {
            "agility": 0,
            "strength": 1,
            "finesse": 0,
            "instinct": 1,
            "presence": 2,
            "knowledge": 1,
            "hit_points": 28,
            "abilities": ["Divine Protection", "Healing Touch"]
        },
        "seraph": {
            "agility": 1,
            "strength": 0,
            "finesse": 1,
            "instinct": 0,
            "presence": 2,
            "knowledge": 1,
            "hit_points": 20,
            "abilities": ["Divine Magic", "Sacred Light"]
        },
        "sorcerer": {
            "agility": 0,
            "strength": 0,
            "finesse": 1,
            "instinct": 1,
            "presence": 1,
            "knowledge": 2,
            "hit_points": 18,
            "abilities": ["Arcane Power", "Spell Weaving"]
        },
        "wizard": {
            "agility": 0,
            "strength": 0,
            "finesse": 1,
            "instinct": 0,
            "presence": 1,
            "knowledge": 3,
            "hit_points": 16,
            "abilities": ["Arcane Studies", "Spell Preparation"]
        }
    }

    # Модификаторы происхождения
    ancestry_mods = {
        "human": {
            "agility": 0,
            "strength": 0,
            "finesse": 0,
            "instinct": 0,
            "presence": 1,
            "knowledge": 0,
            "abilities": ["Adaptability"]
        },
        "elf": {
            "agility": 1,
            "strength": 0,
            "finesse": 1,
            "instinct": 0,
            "presence": 0,
            "knowledge": 0,
            "abilities": ["Elven Grace"]
        },
        "dwarf": {
            "agility": 0,
            "strength": 1,
            "finesse": 0,
            "instinct": 0,
            "presence": 0,
            "knowledge": 1,
            "abilities": ["Dwarven Resilience"]
        },
        "halfling": {
            "agility": 1,
            "strength": 0,
            "finesse": 1,
            "instinct": 1,
            "presence": 0,
            "knowledge": 0,
            "abilities": ["Lucky"]
        },
        "orc": {
            "agility": 0,
            "strength": 2,
            "finesse": 0,
            "instinct": 1,
            "presence": 0,
            "knowledge": 0,
            "abilities": ["Orcish Fury"]
        }
    }

    # Применяем характеристики класса
    if character_class in class_stats:
        stats = class_stats[character_class]
        updates = {
            "agility": stats["agility"],
            "strength": stats["strength"],
            "finesse": stats["finesse"],
            "instinct": stats["instinct"],
            "presence": stats["presence"],
            "knowledge": stats["knowledge"],
            "hit_points": stats["hit_points"],
            "current_hit_points": stats["hit_points"],
            "abilities": stats["abilities"]
        }

        # Применяем модификаторы происхождения
        if ancestry in ancestry_mods:
            ancestry_stats = ancestry_mods[ancestry]
            for stat in ["agility", "strength", "finesse", "instinct", "presence", "knowledge"]:
                if stat in ancestry_stats:
                    updates[stat] += ancestry_stats[stat]

            # Добавляем способности происхождения
            if "abilities" in ancestry_stats:
                updates["abilities"].extend(ancestry_stats["abilities"])

        # Обновляем персонажа
        character = update_character(db, character.id, updates)

    return character