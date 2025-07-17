# 🗡️ Daggerheart Telegram Bot

Телеграм-бот для игры в настольную РПГ Daggerheart с использованием Telegram Mini Apps и ИИ в роли Мастера игры.

## ✨ Возможности

- 🎲 **Создание персонажей** с различными классами и происхождением
- 🎮 **Интерактивная игра** через Telegram Mini App
- 🤖 **ИИ Мастер** на базе DeepSeek API
- ⚔️ **Система Hope/Fear** по правилам Daggerheart
- 🎯 **Броски костей** с автоматическим расчетом результатов
- 📊 **Отслеживание характеристик** персонажа в реальном времени

## 🏗️ Архитектура

- **Telegram Bot** (aiogram) - основное взаимодействие с пользователями
- **FastAPI** - backend API для игровой логики
- **Telegram Mini App** - веб-интерфейс игры
- **SQLite/PostgreSQL** - база данных для персонажей и сессий
- **DeepSeek API** - ИИ для генерации повествования

## 🚀 Установка и запуск

### Локальная разработка

1. **Клонируйте репозиторий:**
```bash
git clone https://github.com/ваш-username/daggerheart-bot.git
cd daggerheart-bot
```

2. **Создайте виртуальное окружение:**
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac  
source venv/bin/activate
```

3. **Установите зависимости:**
```bash
pip install -r requirements.txt
```

4. **Создайте файл .env:**
```env
BOT_TOKEN=your_telegram_bot_token
DEEPSEEK_API_KEY=your_deepseek_api_key
DATABASE_URL=sqlite:///./daggerheart.db
API_HOST=localhost
API_PORT=8000
WEBAPP_URL=http://localhost:8000/webapp
```

5. **Запустите проект:**
```bash
python run.py
```

### Деплой на Railway

1. **Форкните репозиторий на GitHub**

2. **Зарегистрируйтесь на Railway.app**

3. **Создайте новый проект и подключите GitHub**

4. **Добавьте переменные окружения:**
   - `BOT_TOKEN` - токен вашего Telegram бота
   - `DEEPSEEK_API_KEY` - API ключ DeepSeek

5. **Деплой произойдет автоматически**

## 🎲 Как играть

1. Найдите бота в Telegram: `@ваш_бот`
2. Отправьте команду `/start`
3. Нажмите кнопку "🎲 Начать игру в Daggerheart"
4. Создайте персонажа в Mini App
5. Следуйте указаниям ИИ Мастера
6. Используйте кнопки для взаимодействия с игрой

## 🔧 Конфигурация

### Переменные окружения

| Переменная | Описание | Обязательно |
|------------|----------|-------------|
| `BOT_TOKEN` | Токен Telegram бота | ✅ |
| `DEEPSEEK_API_KEY` | API ключ DeepSeek | ✅ |
| `DATABASE_URL` | URL базы данных | ❌ |
| `API_HOST` | Хост API сервера | ❌ |
| `API_PORT` | Порт API сервера | ❌ |
| `WEBAPP_URL` | URL веб-приложения | ❌ |

## 📁 Структура проекта

```
daggerheart_bot/
├── bot/                    # Telegram бот
│   ├── main.py            # Основной файл бота
│   ├── handlers/          # Обработчики команд
│   └── keyboards/         # Клавиатуры
├── api/                   # FastAPI backend
│   ├── main.py           # Основной файл API
│   ├── routes/           # API роуты
│   └── services/         # Сервисы (DeepSeek, игровая логика)
├── webapp/               # Telegram Mini App
│   ├── index.html       # Главная страница
│   ├── css/             # Стили
│   └── js/              # JavaScript логика
├── database/            # Модели и настройки БД
├── config/              # Конфигурация
├── requirements.txt     # Python зависимости
├── Dockerfile          # Docker конфигурация
├── railway.toml        # Railway конфигурация
└── run.py              # Скрипт запуска
```

## 🎮 Игровые механики

### Система Hope/Fear

- **Hope (Надежда)** - накапливается при успехах
- **Fear (Страх)** - накапливается при неудачах
- Влияет на повествование и возможности персонажа

### Броски костей

- Двойные кости: Hope (d12) + Fear (d12)
- Результат = максимальная кость + модификаторы
- Критические результаты при равенстве костей

### Классы персонажей

- **Воин** - мастер боя и защиты
- **Рейнджер** - следопыт и знаток природы
- **Страж** - защитник веры и целитель
- **Серафим** - носитель божественного света
- **Чародей** - мастер природной магии
- **Волшебник** - ученый магических искусств

## 🛠️ Разработка

### Технологии

- **Python 3.11+**
- **aiogram 3.4+** - Telegram Bot Framework
- **FastAPI** - Modern web framework
- **SQLAlchemy** - ORM для работы с БД
- **Pydantic** - Валидация данных
- **DeepSeek API** - ИИ для генерации контента

### Добавление новых возможностей

1. **Игровые механики** - добавляйте в `api/services/game_logic.py`
2. **ИИ промпты** - модифицируйте `api/services/deepseek.py`
3. **Веб-интерфейс** - обновляйте файлы в `webapp/`
4. **API эндпоинты** - добавляйте в `api/routes/`

## 📝 Лицензия

MIT License - см. файл LICENSE

## 🤝 Участие в разработке

1. Форкните репозиторий
2. Создайте ветку для новой функции
3. Внесите изменения
4. Создайте Pull Request

## 📞 Поддержка

Если у вас есть вопросы или предложения:
- Создайте Issue в GitHub
- Напишите в Telegram: @me

---

Создано с ❤️ для сообщества Daggerheart