from pydantic import BaseSettings, Field


class GunicornConfig(BaseSettings):
    host: str = Field(default="127.0.0.1", env="API_HOST")
    port: int = Field(default=8001, env="API_PORT")
    log_level: str = Field(default="info", env="API_LOG_LEVEL")

    @property
    def gunicorn_bind_url(self):
        return f"{self.host}:{self.port}"
