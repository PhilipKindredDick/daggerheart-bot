from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class Character(Base):
    """Модель персонажа"""
    __tablename__ = "characters"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)  # Telegram User ID
    name = Column(String(100), nullable=False)
    character_class = Column(String(50), nullable=False)
    ancestry = Column(String(50), nullable=False)

    # Основные характеристики
    hope = Column(Integer, default=5)
    fear = Column(Integer, default=3)

    # Атрибуты
    agility = Column(Integer, default=0)
    strength = Column(Integer, default=0)
    finesse = Column(Integer, default=0)
    instinct = Column(Integer, default=0)
    presence = Column(Integer, default=0)
    knowledge = Column(Integer, default=0)

    # Дополнительные характеристики
    armor_score = Column(Integer, default=0)
    hit_points = Column(Integer, default=20)
    current_hit_points = Column(Integer, default=20)
    stress = Column(Integer, default=0)

    # Способности и снаряжение (JSON)
    abilities = Column(JSON, default=list)
    equipment = Column(JSON, default=list)
    spells = Column(JSON, default=list)

    # Метаданные
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    # Связи
    game_sessions = relationship("GameSession", back_populates="character")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "name": self.name,
            "class": self.character_class,
            "ancestry": self.ancestry,
            "hope": self.hope,
            "fear": self.fear,
            "agility": self.agility,
            "strength": self.strength,
            "finesse": self.finesse,
            "instinct": self.instinct,
            "presence": self.presence,
            "knowledge": self.knowledge,
            "armor_score": self.armor_score,
            "hit_points": self.hit_points,
            "current_hit_points": self.current_hit_points,
            "stress": self.stress,
            "abilities": self.abilities,
            "equipment": self.equipment,
            "spells": self.spells,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "is_active": self.is_active
        }


class GameSession(Base):
    """Модель игровой сессии"""
    __tablename__ = "game_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    character_id = Column(Integer, ForeignKey("characters.id"), nullable=False)

    # Состояние сессии
    is_active = Column(Boolean, default=True)
    current_scene = Column(String(200), default="")
    game_state = Column(JSON, default=dict)  # Текущее состояние игры

    # История игры
    narrative_log = Column(Text, default="")  # Полная история повествования
    action_log = Column(JSON, default=list)  # Лог действий игрока

    # Метаданные
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_action_at = Column(DateTime, default=datetime.utcnow)

    # Связи
    character = relationship("Character", back_populates="game_sessions")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "character_id": self.character_id,
            "is_active": self.is_active,
            "current_scene": self.current_scene,
            "game_state": self.game_state,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "last_action_at": self.last_action_at.isoformat() if self.last_action_at else None
        }


class DiceRoll(Base):
    """Модель бросков костей"""
    __tablename__ = "dice_rolls"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("game_sessions.id"), nullable=False)
    user_id = Column(Integer, nullable=False)

    # Результаты броска
    hope_die = Column(Integer, nullable=False)  # Результат кости Hope
    fear_die = Column(Integer, nullable=False)  # Результат кости Fear
    modifier = Column(Integer, default=0)

    # Контекст броска
    action_type = Column(String(50), nullable=False)  # Тип действия
    difficulty = Column(Integer, default=12)  # Сложность
    success = Column(Boolean, default=False)  # Успех/неудача

    # Дополнительная информация
    description = Column(String(500), default="")
    result_description = Column(Text, default="")

    # Метаданные
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "session_id": self.session_id,
            "user_id": self.user_id,
            "hope_die": self.hope_die,
            "fear_die": self.fear_die,
            "modifier": self.modifier,
            "action_type": self.action_type,
            "difficulty": self.difficulty,
            "success": self.success,
            "description": self.description,
            "result_description": self.result_description,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }