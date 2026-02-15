from functools import lru_cache
from urllib.parse import quote_plus
from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class MongoDBConfig(BaseSettings):
    host: str = Field(alias="MONGO_HOST")
    port: int = Field(alias="MONGO_PORT")
    user: str = Field(alias="MONGO_USER")
    password: str = Field(alias="MONGO_PASSWORD")
    db_name: str = Field(alias="MONGO_DB_NAME")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @computed_field
    @property
    def mongo_url(self) -> str:
        user = quote_plus(self.user)
        password = quote_plus(self.password)

        return f"mongodb://{user}:{password}@{self.host}:{self.port}/{self.db_name}"


@lru_cache
def get_config() -> MongoDBConfig:
    return MongoDBConfig()


if __name__ == "__main__":
    config = get_config()
    print("MongoDB URL:", config.mongo_url)
