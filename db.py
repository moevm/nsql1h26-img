from urllib.parse import quote_plus
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class MongoDBConfig(BaseSettings):
    host: str = Field(alias="MONGO_HOST")
    port: int = Field(alias="MONGO_PORT")
    db: str = Field(alias="MONGO_DB")
    user: str = Field(alias="MONGO_USER")
    password: str = Field(alias="MONGO_PASSWORD")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    def get_mongo_url(self) -> str:
        user = quote_plus(self.user)
        password = quote_plus(self.password)

        return (
            f"mongodb://{user}:{password}"
            f"@{self.host}:{self.port}/{self.db}"
        )


if __name__ == "__main__":
    config = MongoDBConfig()
    print("MongoDB URL:", config.get_mongo_url())
