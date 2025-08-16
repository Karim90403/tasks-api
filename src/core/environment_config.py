import os
from functools import lru_cache

from pydantic import BaseSettings, Field


# Project name. Used in Swagger documentation
class ProjectConfig(BaseSettings):
    name: str = Field("", env="PROJECT_NAME")
    api_host: str = Field(default="127.0.0.1", env="API_HOST")
    api_port: int = Field(default=8000, env="API_PORT")
    debug: bool = Field(default=False, env="DEBUG")
    base_dir: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class Settings(BaseSettings):
    project: ProjectConfig = ProjectConfig()


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
