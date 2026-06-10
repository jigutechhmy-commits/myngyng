from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str = "postgresql+psycopg://goodchoice:goodchoice@localhost:5432/goodchoice"
    cors_origins: list[str] = ["http://localhost:3000"]

    # AI Layer
    openai_api_key: str = ""
    anthropic_api_key: str = ""
    anthropic_model: str = "claude-opus-4-8"


settings = Settings()
