from pydantic_settings import BaseSettings
from pydantic import Field
import os


class Settings(BaseSettings):
    # Telegram Bot
    BOT_TOKEN: str = Field(..., description="Telegram Bot Token")

    # DeepSeek API
    DEEPSEEK_API_KEY: str = Field(..., description="DeepSeek API Key")
    DEEPSEEK_API_URL: str = Field(default="https://api.deepseek.com/v1/chat/completions",
                                  description="DeepSeek API URL")

    # Database
    DATABASE_URL: str = Field(default="sqlite:///./daggerheart.db", description="Database URL")

    # API Server
    API_HOST: str = Field(default="0.0.0.0", description="API Host")
    API_PORT: int = Field(default=int(os.getenv("PORT", 8000)), description="API Port")

    # WebApp - автоматически определяем URL в продакшене
    WEBAPP_URL: str = Field(default="", description="WebApp URL")

    # Game Settings
    MAX_HOPE: int = Field(default=10, description="Максимальное количество Hope")
    MAX_FEAR: int = Field(default=10, description="Максимальное количество Fear")

    @property
    def webapp_url(self) -> str:
        """Автоматическое определение URL веб-приложения"""
        if self.WEBAPP_URL:
            return self.WEBAPP_URL

        # Определяем URL на основе переменных окружения хостинга
        railway_url = os.getenv("RAILWAY_STATIC_URL")
        render_url = os.getenv("RENDER_EXTERNAL_URL")
        heroku_url = os.getenv("HEROKU_APP_NAME")

        if railway_url:
            return f"{railway_url}/webapp"
        elif render_url:
            return f"{render_url}/webapp"
        elif heroku_url:
            return f"https://{heroku_url}.herokuapp.com/webapp"
        else:
            return f"http://{self.API_HOST}:{self.API_PORT}/webapp"

    class Config:
        env_file = ".env"
        case_sensitive = True


# Создаем глобальный объект настроек
settings = Settings()