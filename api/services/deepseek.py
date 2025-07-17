import httpx
import json
import logging
from typing import Dict, Any, Optional
from config.settings import settings

logger = logging.getLogger(__name__)


class DeepSeekService:
    """Сервис для взаимодействия с DeepSeek API"""

    def __init__(self):
        self.api_key = settings.DEEPSEEK_API_KEY
        self.api_url = settings.DEEPSEEK_API_URL
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        self.system_prompt = self._create_system_prompt()

    def _create_system_prompt(self) -> str:
        """Создание системного промпта для ГМ"""
        return """Ты - опытный Мастер игры (ГМ) в настольной ролевой игре Daggerheart. 

Твоя роль:
- Создавать увлекательные приключения и повествование
- Управлять НПС и окружающим миром
- Интерпретировать результаты бросков костей
- Создавать драматические и интересные ситуации
- Следовать правилам Daggerheart

Ключевые принципы Daggerheart:
- Система Hope/Fear: Hope (надежда) накапливается при успехах, Fear (страх) - при неудачах
- Двойные кости: игроки бросают кость Hope (d12) и кость Fear (d12)
- Порог сложности обычно 12
- При равенстве костей происходит критический результат
- Магия и способности влияют на Hope/Fear

Стиль повествования:
- Яркие описания и атмосфера
- Интерактивность и выбор для игрока
- Баланс между опасностью и героизмом
- Эмоциональная вовлеченность
- Ответы длиной 2-4 предложения

Всегда помни:
- Игрок должен чувствовать себя героем истории
- Неудачи должны создавать новые возможности
- Мир должен реагировать на действия персонажа
- Используй элементы фантастического мира с магией"""

    async def generate_narrative(self, prompt: str, character_context: Dict[str, Any]) -> str:
        """Генерация повествования от ГМ"""
        try:
            # Подготавливаем контекст персонажа
            character_summary = self._format_character_context(character_context)

            # Создаем полный промпт
            full_prompt = f"""
{character_summary}

{prompt}

Создай яркое и увлекательное повествование, учитывая контекст персонажа и ситуации. 
Ответ должен быть на русском языке, 2-4 предложения."""

            # Отправляем запрос к DeepSeek
            payload = {
                "model": "deepseek-chat",
                "messages": [
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": full_prompt}
                ],
                "temperature": 0.8,
                "max_tokens": 300,
                "stream": False
            }

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    self.api_url,
                    headers=self.headers,
                    json=payload
                )

                if response.status_code != 200:
                    logger.error(f"DeepSeek API error: {response.status_code} - {response.text}")
                    return self._get_fallback_narrative(prompt)

                result = response.json()
                narrative = result["choices"][0]["message"]["content"].strip()

                logger.info(f"Narrative generated successfully: {narrative[:100]}...")
                return narrative

        except Exception as e:
            logger.error(f"Error generating narrative: {e}")
            return self._get_fallback_narrative(prompt)

    def _format_character_context(self, character: Dict[str, Any]) -> str:
        """Форматирование контекста персонажа"""
        return f"""
Персонаж: {character.get('name', 'Неизвестный')}
Класс: {character.get('class', 'Неизвестный')}
Происхождение: {character.get('ancestry', 'Неизвестное')}
Hope: {character.get('hope', 5)}/10
Fear: {character.get('fear', 3)}/10
Здоровье: {character.get('current_hit_points', 20)}/{character.get('hit_points', 20)}
"""

    def _get_fallback_narrative(self, prompt: str) -> str:
        """Резервное повествование при ошибке API"""
        fallback_responses = [
            "Ты продолжаешь свое путешествие, чувствуя, как мир вокруг тебя полон тайн и возможностей. Что будешь делать дальше?",
            "Окружающий мир словно замер в ожидании твоего следующего шага. Приключение продолжается!",
            "Твой путь героя только начинается. Впереди ждут великие свершения и испытания.",
            "Магия этого мира откликается на твое присутствие. Время действовать!"
        ]

        import random
        return random.choice(fallback_responses)

    async def interpret_dice_result(self, hope_die: int, fear_die: int, success: bool, action_context: str) -> str:
        """Интерпретация результата броска костей"""
        try:
            prompt = f"""
Результат броска костей:
Hope (надежда): {hope_die}
Fear (страх): {fear_die}
Результат: {'Успех' if success else 'Неудача'}
Контекст действия: {action_context}

Опиши результат этого действия, учитывая значения костей и исход."""

            return await self.generate_narrative(prompt, {})

        except Exception as e:
            logger.error(f"Error interpreting dice result: {e}")
            if success:
                return f"Твое действие увенчалось успехом! (Hope: {hope_die}, Fear: {fear_die})"
            else:
                return f"Не все прошло гладко, но это лишь новая возможность! (Hope: {hope_die}, Fear: {fear_die})"

    async def create_initial_scenario(self, character: Dict[str, Any]) -> str:
        """Создание начального сценария для персонажа"""
        try:
            prompt = f"""
Создай начальный сценарий приключения для персонажа.
Учти класс и происхождение персонажа при создании подходящей стартовой ситуации.
Опиши место, где находится персонаж, и предложи несколько вариантов действий.
"""

            return await self.generate_narrative(prompt, character)

        except Exception as e:
            logger.error(f"Error creating initial scenario: {e}")
            return "Ты стоишь на пороге великого приключения. Перед тобой открывается мир, полный магии и опасностей. Что ты выберешь: исследовать древние руины впереди или направиться к оживленной таверне справа?"

    async def generate_random_encounter(self, character: Dict[str, Any], location: str = "") -> str:
        """Генерация случайной встречи"""
        try:
            prompt = f"""
Создай случайную встречу или событие для персонажа.
Локация: {location if location else "на пути"}
Встреча должна быть интересной и соответствовать уровню персонажа.
"""

            return await self.generate_narrative(prompt, character)

        except Exception as e:
            logger.error(f"Error generating random encounter: {e}")
            return "Внезапно ты замечаешь что-то необычное в этом месте. Стоит ли исследовать это ближе?"

    async def describe_location(self, location_name: str, character: Dict[str, Any]) -> str:
        """Описание локации"""
        try:
            prompt = f"""
Опиши локацию: {location_name}
Создай атмосферное описание места, включи детали, которые могут заинтересовать персонажа.
Упомяни возможные точки интереса или потенциальные взаимодействия.
"""

            return await self.generate_narrative(prompt, character)

        except Exception as e:
            logger.error(f"Error describing location: {e}")
            return f"Ты находишься в {location_name}. Это место хранит свои тайны и готово открыть их смелому искателю приключений."

    async def handle_character_death(self, character: Dict[str, Any]) -> str:
        """Обработка смерти персонажа"""
        try:
            prompt = f"""
Персонаж {character.get('name')} погиб в бою.
Создай драматичное, но не депрессивное описание этого момента.
Намекни на возможность возрождения или продолжения истории.
"""

            return await self.generate_narrative(prompt, character)

        except Exception as e:
            logger.error(f"Error handling character death: {e}")
            return "Твоя история не заканчивается здесь. Даже в самый темный час Hope (надежда) может найти способ вернуть героя к жизни."