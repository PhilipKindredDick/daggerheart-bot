import random
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class DaggerheartGameLogic:
    """Класс для обработки игровой логики Daggerheart"""

    def __init__(self):
        self.difficulty_levels = {
            "trivial": 6,
            "easy": 9,
            "moderate": 12,
            "hard": 15,
            "extreme": 18
        }

    def calculate_dice_result(self, hope_die: int, fear_die: int, difficulty: int = 12, modifier: int = 0) -> Dict[
        str, Any]:
        """Вычисление результата броска костей по правилам Daggerheart"""

        # Базовый результат - сумма наибольшей кости и модификатора
        total = max(hope_die, fear_die) + modifier
        success = total >= difficulty

        # Проверка на критические результаты
        critical_success = False
        critical_failure = False
        mixed_result = False

        # Если кости показывают одинаковое значение
        if hope_die == fear_die:
            if success:
                critical_success = True
            else:
                critical_failure = True

        # Смешанный результат - когда одна кость успешна, другая нет
        elif (hope_die >= difficulty and fear_die < difficulty) or (fear_die >= difficulty and hope_die < difficulty):
            mixed_result = True

        # Определение основной кости (Hope или Fear)
        dominant_die = "hope" if hope_die > fear_die else "fear" if fear_die > hope_die else "tied"

        # Создание описания результата
        description = self._create_result_description(
            hope_die, fear_die, total, difficulty, success,
            critical_success, critical_failure, mixed_result, dominant_die
        )

        return {
            "hope_die": hope_die,
            "fear_die": fear_die,
            "total": total,
            "difficulty": difficulty,
            "success": success,
            "critical_success": critical_success,
            "critical_failure": critical_failure,
            "mixed_result": mixed_result,
            "dominant_die": dominant_die,
            "description": description,
            "modifier": modifier
        }

    def _create_result_description(self, hope_die: int, fear_die: int, total: int, difficulty: int,
                                   success: bool, critical_success: bool, critical_failure: bool,
                                   mixed_result: bool, dominant_die: str) -> str:
        """Создание текстового описания результата броска"""

        if critical_success:
            return f"Критический успех! Обе кости показали {hope_die}, итого {total} против {difficulty}"
        elif critical_failure:
            return f"Критическая неудача! Обе кости показали {hope_die}, итого {total} против {difficulty}"
        elif mixed_result:
            return f"Смешанный результат: Hope {hope_die}, Fear {fear_die}, итого {total} против {difficulty}"
        elif success:
            return f"Успех! Hope {hope_die}, Fear {fear_die}, итого {total} против {difficulty}"
        else:
            return f"Неудача. Hope {hope_die}, Fear {fear_die}, итого {total} против {difficulty}"

    def update_hope_fear(self, character: Any, dice_result: Dict[str, Any]) -> Dict[str, int]:
        """Обновление Hope и Fear персонажа на основе результата броска"""

        hope_change = 0
        fear_change = 0

        # Базовые правила изменения Hope/Fear
        if dice_result["critical_success"]:
            hope_change = 2
        elif dice_result["success"]:
            hope_change = 1
        elif dice_result["critical_failure"]:
            fear_change = 2
        else:
            fear_change = 1

        # Дополнительные изменения на основе доминирующей кости
        if dice_result["dominant_die"] == "hope" and dice_result["success"]:
            hope_change += 1
        elif dice_result["dominant_die"] == "fear" and not dice_result["success"]:
            fear_change += 1

        # Применяем изменения с учетом лимитов
        new_hope = max(0, min(10, character.hope + hope_change))
        new_fear = max(0, min(10, character.fear + fear_change))

        return {
            "hope": new_hope,
            "fear": new_fear
        }

    def create_initial_prompt(self, character: Any) -> str:
        """Создание начального промпта для персонажа"""

        class_intros = {
            "warrior": "Ты - опытный воин, чья сила и мастерство владения оружием известны во многих землях.",
            "ranger": "Ты - следопыт, знающий тайны дикой природы и умеющий выживать в самых суровых условиях.",
            "guardian": "Ты - защитник, посвятивший себя служению высшим силам и защите невинных.",
            "seraph": "Ты - серафим, носитель божественной силы и света в этом мире.",
            "sorcerer": "Ты - чародей, в чьих жилах течет магическая сила, готовая вырваться наружу.",
            "wizard": "Ты - волшебник, изучивший тайны магии через долгие годы учебы и практики."
        }

        ancestry_traits = {
            "human": "Твоя человеческая находчивость и адаптивность помогают тебе в любых ситуациях.",
            "elf": "Твоя эльфийская грация и связь с природой дают тебе преимущество.",
            "dwarf": "Твоя дварфийская стойкость и знание ремесел делают тебя надежным спутником.",
            "halfling": "Твоя удачливость полурослика и жизнерадостность поднимают дух окружающих.",
            "orc": "Твоя орочья сила и решимость помогают преодолевать любые препятствия."
        }

        class_intro = class_intros.get(character.character_class,
                                       "Ты - искатель приключений с уникальными способностями.")
        ancestry_trait = ancestry_traits.get(character.ancestry, "Твое происхождение дает тебе особые черты.")

        return f"""
{class_intro} {ancestry_trait}

Твое имя - {character.name}, и ты стоишь на пороге нового приключения. 
Создай вступительную сцену для этого персонажа, опиши начальную ситуацию и предложи варианты действий.
Учти класс и происхождение персонажа при создании подходящего начала истории.
"""

    def create_dice_result_prompt(self, context: Dict[str, Any]) -> str:
        """Создание промпта для интерпретации результата броска костей"""

        dice_result = context["dice_result"]
        character = context["character"]

        return f"""
Персонаж {character['name']} только что совершил действие.

Результат броска:
{dice_result['description']}

Hope персонажа изменился с {character['hope'] - (character['hope'] - dice_result.get('hope_change', 0))} до {character['hope']}
Fear персонажа изменился с {character['fear'] - (character['fear'] - dice_result.get('fear_change', 0))} до {character['fear']}

Опиши результат этого действия, учитывая:
- Был ли это успех или неудача
- Как изменилось состояние персонажа
- Что происходит дальше в истории
"""

    def create_action_prompt(self, context: Dict[str, Any]) -> str:
        """Создание промпта для обработки действия игрока"""

        action = context["action"]
        description = context.get("description", "")
        character = context["character"]

        return f"""
Персонаж {character['name']} хочет выполнить действие: {action}
{f"Описание: {description}" if description else ""}

Текущее состояние персонажа:
- Hope: {character['hope']}/10
- Fear: {character['fear']}/10
- Здоровье: {character['current_hit_points']}/{character['hit_points']}

Опиши, как это действие развивается, какие препятствия или возможности возникают.
Если нужен бросок костей, намекни на это в повествовании.
"""

    def process_action(self, action: str, character: Any, session: Any) -> Dict[str, Any]:
        """Обработка действия игрока"""

        action_lower = action.lower()
        result = {
            "requires_dice_roll": False,
            "scene_change": False,
            "new_scene": None,
            "new_game_state": None
        }

        # Определяем тип действия
        if any(word in action_lower for word in ["атак", "бой", "удар", "нападен"]):
            result["requires_dice_roll"] = True
            result["action_type"] = "combat"
            result["difficulty"] = 12

        elif any(word in action_lower for word in ["исследов", "поиск", "осмотр"]):
            result["requires_dice_roll"] = True
            result["action_type"] = "investigation"
            result["difficulty"] = 10

        elif any(word in action_lower for word in ["магия", "заклинан", "колдовств"]):
            result["requires_dice_roll"] = True
            result["action_type"] = "magic"
            result["difficulty"] = 14

        elif any(word in action_lower for word in ["перемещ", "движен", "бег", "прыжок"]):
            result["requires_dice_roll"] = True
            result["action_type"] = "movement"
            result["difficulty"] = 9

        elif any(word in action_lower for word in ["общен", "убежден", "перегов"]):
            result["requires_dice_roll"] = True
            result["action_type"] = "social"
            result["difficulty"] = 11

        # Проверяем на смену локации
        if any(word in action_lower for word in ["вход", "выход", "направл", "идти к"]):
            result["scene_change"] = True
            result["new_scene"] = self._determine_new_scene(action, session)

        return result

    def _determine_new_scene(self, action: str, session: Any) -> str:
        """Определение новой сцены на основе действия"""

        action_lower = action.lower()

        if "таверн" in action_lower:
            return "Таверна"
        elif "лес" in action_lower:
            return "Темный лес"
        elif "город" in action_lower:
            return "Городская площадь"
        elif "подземель" in action_lower or "пещер" in action_lower:
            return "Подземелье"
        elif "храм" in action_lower:
            return "Древний храм"
        else:
            return "Новая локация"

    def get_random_encounter_type(self, location: str = "") -> str:
        """Получение случайного типа встречи"""

        encounters = [
            "hostile_creature",
            "friendly_npc",
            "mysterious_object",
            "environmental_hazard",
            "treasure",
            "trap",
            "magic_anomaly"
        ]

        return random.choice(encounters)

    def calculate_damage(self, attacker_stats: Dict, target_stats: Dict, weapon_damage: int = 6) -> int:
        """Расчет урона"""

        base_damage = weapon_damage
        strength_bonus = attacker_stats.get("strength", 0)
        armor_reduction = target_stats.get("armor_score", 0)

        total_damage = max(1, base_damage + strength_bonus - armor_reduction)

        return total_damage

    def check_death_saves(self, character: Any) -> Dict[str, Any]:
        """Проверка спасбросков от смерти"""

        if character.current_hit_points <= 0:
            hope_roll = random.randint(1, 12)
            fear_roll = random.randint(1, 12)

            # Успешный спасбросок если Hope больше Fear
            success = hope_roll > fear_roll

            return {
                "death_save_required": True,
                "hope_roll": hope_roll,
                "fear_roll": fear_roll,
                "success": success,
                "stabilized": success
            }

        return {"death_save_required": False}