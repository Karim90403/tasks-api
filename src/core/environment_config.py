import os
from functools import lru_cache
from typing import Optional

from aiocache.serializers import PickleSerializer
from pydantic import BaseSettings, Field
from pydantic.class_validators import validator


# Project name. Used in Swagger documentation
class ProjectConfig(BaseSettings):
    name: str = Field("", env="PROJECT_NAME")
    api_host: str = Field(default="127.0.0.1", env="API_HOST")
    api_port: int = Field(default=8000, env="API_PORT")
    debug: bool = Field(default=False, env="DEBUG")
    file_dir: str = Field(default="/data/uploads", env="FILE_DIR")
    base_dir: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class RedisConfig(BaseSettings):
    port: int = Field(default=6379, env="REDIS_PORT")
    host: str = Field(default="search_redis", env="REDIS_HOST")
    func_expire: int = Field(default=3600, env="FUNC_EXPIRE")
    search_expire: int = Field(default=3600, env="SEARCH_EXPIRE")
    expire_manager: int = Field(default=300, env="EXPIRE_MANAGER")

    @classmethod
    @validator("port", "func_expire", "search_expire", "expire_manager", pre=True, each_item=True)
    def validate_integer_fields(cls, value):
        if isinstance(value, str):
            return int(float(value))
        return value

    @property
    def cache_params(self):
        return {
            "timeout": 10,
            "serializer": PickleSerializer(),
            "port": self.port,
            "endpoint": self.host,
            "namespace": "main",
        }


class ElasticConfig(BaseSettings):
    url: str = Field(default="http://search_elasticsearch:9200", env="ELASTIC_URL")
    login: Optional[str] = Field(default=None, env="ELASTIC_LOGIN")
    password: Optional[str] = Field(default=None, env="ELASTIC_PASSWORD")
    index: str = Field(default="construction", env="ELASTIC_INDEX")
    users_index: str = Field(default="users", env="ELASTIC_USERS_INDEX")
    request_timeout: int = Field(default=10, env="ELASTIC_REQUEST_TIMEOUT")


class JWTConfig(BaseSettings):
    secret_key: str = Field(default="supersecret", env="JWT_SECRET_KEY")
    algorithm: str = Field(default="HS256", env="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(default=30, env="JWT_ACCESS_TOKEN_EXPIRE_MINUTES")
    refresh_token_expire_days: int = Field(default=30, env="REFRESH_TOKEN_EXPIRE_DAYS")
    access_token_proactive_refresh_seconds: int = Field(default=120, env="ACCESS_TOKEN_PROACTIVE_REFRESH_SECONDS")

class Settings(BaseSettings):
    project: ProjectConfig = ProjectConfig()
    redis: RedisConfig = RedisConfig()
    elasticsearch: ElasticConfig = ElasticConfig()
    jwt: JWTConfig = JWTConfig()

@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
