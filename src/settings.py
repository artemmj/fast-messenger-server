from pydantic import SecretStr, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class DBSettings(BaseSettings):
    db_name: str = Field(default="postgres", alias="DB_DATABASENAME")
    db_user: str = Field(default="postgres", alias="DB_USERNAME")
    db_password: SecretStr = Field(default="postgres", alias="DB_PASSWORD")
    db_host: str = Field(default="localhost", alias="DB_HOST")
    db_port: int = Field(default="5432", alias="DB_PORT")
    db_echo: bool = Field(default=False, alias="DB_ECHO")

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf8", extra="ignore"
    )

    @property
    def db_url(self):
        return (
            f"postgresql+asyncpg://{self.db_user}:"
            f"{self.db_password.get_secret_value()}@"
            f"{self.db_host}:{self.db_port}/{self.db_name}"
        )


class Settings(BaseSettings):
    debug: bool = Field(default=True, alias="DEBUG")

    db_settings: DBSettings = DBSettings()

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf8", extra="ignore"
    )


settings = Settings()
