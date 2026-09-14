from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Ulas Rasa API"
    environment: str = "development"
    allowed_origins: list[str] = ["http://localhost:3000"]
    database_url: str

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()  # pyright: ignore[reportCallIssue]
