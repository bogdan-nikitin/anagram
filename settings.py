from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    BOT_TOKEN: SecretStr
    PGPASSWORD: SecretStr
    APP_BASE_URL: str
    ANAGRAM_FILE: str

    model_config = SettingsConfigDict(env_file='.env')


settings = Settings()
