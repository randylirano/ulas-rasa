from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # App
    app_name: str = "Ulas Rasa API"
    environment: str = "development"

    # CORS
    allowed_origins: list[str] = ["http://localhost:3000"]

    class Config:
        env_file = ".env"


settings = Settings()