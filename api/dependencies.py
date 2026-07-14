# api/dependencies.py
from fastapi import Request, HTTPException
from api.middleware.auth import verify_api_key, check_rate_limit
from api.config.settings import settings


async def get_current_user(api_key: str = verify_api_key):
    """
    获取当前用户（从 API Key 解析）
    """
    return {
        "api_key": api_key,
        "authenticated": True
    }


def require_auth():
    """
    需要认证的依赖
    """
    return verify_api_key


def optional_auth():
    """
    可选认证的依赖
    """
    from api.middleware.auth import verify_optional_api_key
    return verify_optional_api_key


def rate_limit(limit: int = 60, window: int = 60):
    """
    速率限制依赖
    """
    async def _rate_limit(request: Request, api_key: str = verify_api_key):
        # 使用 API Key + 路径作为限流 key
        key = f"{api_key}:{request.url.path}"
        return check_rate_limit(key, limit, window)
    return _rate_limit