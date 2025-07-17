from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config.settings import settings
import logging

logger = logging.getLogger(__name__)

# Создание движка базы данных
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)

# Создание сессии
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


# Зависимость для получения сессии базы данных
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Инициализация базы данных
async def init_db():
    """Создание таблиц в базе данных"""
    try:
        from database.models import Base
        Base.metadata.create_all(bind=engine)
        logger.info("База данных инициализирована успешно")
    except Exception as e:
        logger.error(f"Ошибка инициализации базы данных: {e}")
        raise


# Функции для работы с персонажами
def create_character(db, character_data):
    """Создание нового персонажа"""
    from database.models import Character

    character = Character(
        user_id=character_data["user_id"],
        name=character_data["name"],
        character_class=character_data["class"],
        ancestry=character_data["ancestry"]
    )

    db.add(character)
    db.commit()
    db.refresh(character)
    return character


def get_character_by_user_id(db, user_id):
    """Получение активного персонажа пользователя"""
    from database.models import Character

    return db.query(Character).filter(
        Character.user_id == user_id,
        Character.is_active == True
    ).first()


def get_character_by_id(db, character_id):
    """Получение персонажа по ID"""
    from database.models import Character

    return db.query(Character).filter(Character.id == character_id).first()


def update_character(db, character_id, updates):
    """Обновление данных персонажа"""
    from database.models import Character

    character = db.query(Character).filter(Character.id == character_id).first()
    if character:
        for key, value in updates.items():
            if hasattr(character, key):
                setattr(character, key, value)
        db.commit()
        db.refresh(character)
    return character


# Функции для работы с игровыми сессиями
def create_game_session(db, session_data):
    """Создание новой игровой сессии"""
    from database.models import GameSession

    session = GameSession(
        user_id=session_data["user_id"],
        character_id=session_data["character_id"]
    )

    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def get_active_game_session(db, user_id):
    """Получение активной игровой сессии пользователя"""
    from database.models import GameSession

    return db.query(GameSession).filter(
        GameSession.user_id == user_id,
        GameSession.is_active == True
    ).first()


def update_game_session(db, session_id, updates):
    """Обновление игровой сессии"""
    from database.models import GameSession
    from datetime import datetime

    session = db.query(GameSession).filter(GameSession.id == session_id).first()
    if session:
        for key, value in updates.items():
            if hasattr(session, key):
                setattr(session, key, value)
        session.last_action_at = datetime.utcnow()
        db.commit()
        db.refresh(session)
    return session


def add_narrative_to_session(db, session_id, narrative):
    """Добавление повествования в сессию"""
    from database.models import GameSession
    from datetime import datetime

    session = db.query(GameSession).filter(GameSession.id == session_id).first()
    if session:
        if session.narrative_log:
            session.narrative_log += f"\n\n{narrative}"
        else:
            session.narrative_log = narrative
        session.last_action_at = datetime.utcnow()
        db.commit()
        db.refresh(session)
    return session


def add_action_to_session(db, session_id, action):
    """Добавление действия в лог сессии"""
    from database.models import GameSession
    from datetime import datetime

    session = db.query(GameSession).filter(GameSession.id == session_id).first()
    if session:
        if not session.action_log:
            session.action_log = []

        action_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "action": action
        }
        session.action_log.append(action_entry)
        session.last_action_at = datetime.utcnow()
        db.commit()
        db.refresh(session)
    return session


# Функции для работы с бросками костей
def create_dice_roll(db, roll_data):
    """Создание записи о броске костей"""
    from database.models import DiceRoll

    dice_roll = DiceRoll(
        session_id=roll_data["session_id"],
        user_id=roll_data["user_id"],
        hope_die=roll_data["hope_die"],
        fear_die=roll_data["fear_die"],
        modifier=roll_data.get("modifier", 0),
        action_type=roll_data["action_type"],
        difficulty=roll_data.get("difficulty", 12),
        success=roll_data.get("success", False),
        description=roll_data.get("description", ""),
        result_description=roll_data.get("result_description", "")
    )

    db.add(dice_roll)
    db.commit()
    db.refresh(dice_roll)
    return dice_roll


def get_session_dice_rolls(db, session_id, limit=10):
    """Получение последних бросков костей для сессии"""
    from database.models import DiceRoll

    return db.query(DiceRoll).filter(
        DiceRoll.session_id == session_id
    ).order_by(DiceRoll.created_at.desc()).limit(limit).all()


# Вспомогательные функции
def close_all_user_sessions(db, user_id):
    """Закрытие всех активных сессий пользователя"""
    from database.models import GameSession

    sessions = db.query(GameSession).filter(
        GameSession.user_id == user_id,
        GameSession.is_active == True
    ).all()

    for session in sessions:
        session.is_active = False

    db.commit()
    return len(sessions)


def deactivate_user_characters(db, user_id):
    """Деактивация всех персонажей пользователя"""
    from database.models import Character

    characters = db.query(Character).filter(
        Character.user_id == user_id,
        Character.is_active == True
    ).all()

    for character in characters:
        character.is_active = False

    db.commit()
    return len(characters)