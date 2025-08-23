from typing import Annotated

from pydantic import BaseModel, MongoDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class MongoSettings(BaseModel):
    url: Annotated[str, MongoDsn] = "mongodb://172.27.32.1:27017"
    db_name: str = "chatbot_test"


class ServerSettings(BaseModel):
    workers: int = 1


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        extra="ignore",
        env_file_encoding="utf-8",
        env_file=".env",
        env_nested_delimiter="__",
    )

    mongo: MongoSettings = MongoSettings()
    server: ServerSettings = ServerSettings()


settings = Settings()
