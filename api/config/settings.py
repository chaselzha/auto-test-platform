# api/config/settings.py
import os
from pathlib import Path
from dotenv import load_dotenv

# 加载 .env 文件
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(env_path)


class Settings:
    """应用配置"""

    # API 配置
    API_PORT: int = int(os.getenv("API_PORT", 8000))
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")

    # 安全配置
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key-change-me")
    API_KEY: str = os.getenv("API_KEY", "test-api-key-123456")
    API_KEY_HEADER: str = os.getenv("API_KEY_HEADER", "X-API-Key")

    # 允许的 API Key 列表（支持多个）
    VALID_API_KEYS: list = [
        API_KEY,
        os.getenv("API_KEY_2", ""),
        os.getenv("API_KEY_3", ""),
    ]
    # 过滤掉空值
    VALID_API_KEYS = [k for k in VALID_API_KEYS if k]

    # 是否启用认证（开发环境可以关闭）
    AUTH_ENABLED: bool = os.getenv("AUTH_ENABLED", "true").lower() == "true"

    # 数据库配置
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./test_platform.db")

    # 测试配置
    TEST_TIMEOUT: int = int(os.getenv("TEST_TIMEOUT", 3600))
    MAX_PARALLEL_TESTS: int = int(os.getenv("MAX_PARALLEL_TESTS", 4))


settings = Settings()