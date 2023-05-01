from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    project_name: str = Field(..., env="PROJECT_NAME")
    storage_url: str
    limit: int = 10
    time_window: int = 1
    service_api_url: str = "http://127.0.0.1:8080"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
