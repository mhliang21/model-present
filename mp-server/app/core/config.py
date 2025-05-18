from pydantic import BaseSettings
from typing import List


class Settings(BaseSettings):
    # 应用设置
    APP_NAME: str = "智能问答系统"
    API_V1_STR: str = "/api"

    # CORS设置
    CORS_ORIGINS: List[str] = ["*"]

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
