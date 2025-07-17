from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from database.database import (
    get_db, create_game_session, get_active_game_session,
    update_game_session, add_narrative_to_session, add_action_to_session,
    create_dice_roll, get_character_by_id, update_character,
    close_all_user_sessions
)
from api.services.deepseek import DeepSeekService
from api.services.game_logic import DaggerheartGameLogic
import logging
import random

logger = logging.getLogger(__name__)

router = APIRouter()


# Pydantic модели
class GameStartRequest(BaseModel):
    characterId: int
    userId: int


class DiceRollRequest(BaseModel):
    characterId: int
    userId: int
    actionType: Optional[str] = "general"
    difficulty: Optional[int] = 12


class GameActionRequest(BaseModel):
    characterId: int
    userId: int
    action: str
    description: Optional[str] = ""


class GameResponse(BaseModel):
    success: bool
    message: str
    narrative: Optional[str] = None
    character: Optional[dict] = None
    game_state: Optional[dict] = None


# Инициализация сервисов
deepseek_service = DeepSeekService()
game_logic = DaggerheartGameLogic()


@router.post("/start", response_model=GameResponse)
async def start_game_session(request: GameStartRequest, db: Session = Depends(get_db)):
    """Начало новой игровой сессии"""
    try:
        logger.info(f"Начало игровой сессии для пользователя {request.userId}")

        # Получаем персонажа
        character = get_character_by_id(db, request.characterId)
        if not character:
            raise HTTPException(status_code=404, detail="Персонаж не найден")

        if character.user_id != request.userId:
            raise HTTPException(status_code=403, detail="Нет доступа к этому персонажу")

        # Закрываем все активные сессии пользователя
        close_all_user_sessions(db, request.userId)

        # Создаем новую сессию
        session_data = {
            "user_id": request.userId,
            "character_id": request.characterId
        }
        session = create_game_session(db, session_data)

        # Генерируем начальное повествование с помощью DeepSeek
        initial_prompt = game_logic.create_initial_prompt(character)
        narrative = await deepseek_service.generate_narrative(initial_prompt, character.to_dict())

        # Сохраняем повествование
        add_narrative_to_session(db, session.id, narrative)

        # Обновляем состояние сессии
        update_game_session(db, session.id, {
            "current_scene": "Начало приключения",
            "game_state": {"scene": "intro", "location": "starting_area"}
        })

        logger.info(f"Игровая сессия {session.id} создана успешно")

        return GameResponse(
            success=True,
            message="Игровая сессия начата",
            narrative=narrative,
            character=character.to_dict(),
            game_state=session.to_dict()
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка начала игровой сессии: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка начала игровой сессии: {str(e)}")


@router.post("/roll-dice", response_model=GameResponse)
async def roll_dice(request: DiceRollRequest, db: Session = Depends(get_db)):
    """Бросок костей"""
    try:
        logger.info(f"Бросок костей для персонажа {request.characterId}")

        # Получаем персонажа и активную сессию
        character = get_character_by_id(db, request.characterId)
        if not character:
            raise HTTPException(status_code=404, detail="Персонаж не найден")

        session = get_active_game_session(db, request.userId)
        if not session:
            raise HTTPException(status_code=404, detail="Активная игровая сессия не найдена")

        # Бросаем кости
        hope_die = random.randint(1, 12)
        fear_die = random.randint(1, 12)

        # Вычисляем результат
        result = game_logic.calculate_dice_result(hope_die, fear_die, request.difficulty)

        # Обновляем Hope и Fear персонажа
        character_updates = game_logic.update_hope_fear(character, result)
        updated_character = update_character(db, character.id, character_updates)

        # Сохраняем бросок в базу
        dice_roll_data = {
            "session_id": session.id,
            "user_id": request.userId,
            "hope_die": hope_die,
            "fear_die": fear_die,
            "action_type": request.actionType,
            "difficulty": request.difficulty,
            "success": result["success"],
            "description": f"Бросок: Hope {hope_die}, Fear {fear_die}",
            "result_description": result["description"]
        }
        create_dice_roll(db, dice_roll_data)

        # Генерируем повествование на основе результата
        context = {
            "dice_result": result,
            "character": updated_character.to_dict(),
            "session": session.to_dict()
        }
        narrative_prompt = game_logic.create_dice_result_prompt(context)
        narrative = await deepseek_service.generate_narrative(narrative_prompt, updated_character.to_dict())

        # Сохраняем повествование и действие
        add_narrative_to_session(db, session.id, narrative)
        add_action_to_session(db, session.id, f"dice_roll: {result['description']}")

        logger.info(f"Бросок костей выполнен: Hope {hope_die}, Fear {fear_die}, Успех: {result['success']}")

        return GameResponse(
            success=True,
            message="Кости брошены",
            narrative=narrative,
            character=updated_character.to_dict(),
            game_state=session.to_dict()
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка броска костей: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка броска костей: {str(e)}")


@router.post("/action", response_model=GameResponse)
async def perform_action(request: GameActionRequest, db: Session = Depends(get_db)):
    """Выполнение игрового действия"""
    try:
        logger.info(f"Действие '{request.action}' для персонажа {request.characterId}")

        # Получаем персонажа и активную сессию
        character = get_character_by_id(db, request.characterId)
        if not character:
            raise HTTPException(status_code=404, detail="Персонаж не найден")

        session = get_active_game_session(db, request.userId)
        if not session:
            raise HTTPException(status_code=404, detail="Активная игровая сессия не найдена")

        # Обрабатываем действие
        action_result = game_logic.process_action(request.action, character, session)

        # Генерируем повествование
        context = {
            "action": request.action,
            "description": request.description,
            "character": character.to_dict(),
            "session": session.to_dict(),
            "result": action_result
        }
        narrative_prompt = game_logic.create_action_prompt(context)
        narrative = await deepseek_service.generate_narrative(narrative_prompt, character.to_dict())

        # Сохраняем повествование и действие
        add_narrative_to_session(db, session.id, narrative)
        add_action_to_session(db, session.id, f"action: {request.action} - {request.description}")

        # Обновляем состояние сессии если нужно
        if action_result.get("scene_change"):
            update_game_session(db, session.id, {
                "current_scene": action_result["new_scene"],
                "game_state": action_result.get("new_game_state", session.game_state)
            })

        logger.info(f"Действие '{request.action}' выполнено успешно")

        return GameResponse(
            success=True,
            message="Действие выполнено",
            narrative=narrative,
            character=character.to_dict(),
            game_state=session.to_dict()
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка выполнения действия: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка выполнения действия: {str(e)}")


@router.get("/session/{user_id}")
async def get_game_session(user_id: int, db: Session = Depends(get_db)):
    """Получение активной игровой сессии"""
    try:
        session = get_active_game_session(db, user_id)

        if not session:
            return {
                "success": False,
                "message": "Активная игровая сессия не найдена"
            }

        character = get_character_by_id(db, session.character_id)

        return {
            "success": True,
            "message": "Игровая сессия найдена",
            "session": session.to_dict(),
            "character": character.to_dict() if character else None
        }

    except Exception as e:
        logger.error(f"Ошибка получения игровой сессии: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка получения игровой сессии: {str(e)}")


@router.post("/session/{session_id}/end")
async def end_game_session(session_id: int, user_id: int, db: Session = Depends(get_db)):
    """Завершение игровой сессии"""
    try:
        session = get_active_game_session(db, user_id)

        if not session or session.id != session_id:
            raise HTTPException(status_code=404, detail="Игровая сессия не найдена")

        # Завершаем сессию
        update_game_session(db, session_id, {"is_active": False})

        logger.info(f"Игровая сессия {session_id} завершена")

        return {
            "success": True,
            "message": "Игровая сессия завершена"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка завершения игровой сессии: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка завершения игровой сессии: {str(e)}")