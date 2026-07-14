# api/middleware/auth.py
from fastapi import HTTPException, Security
from fastapi.security import APIKeyHeader
from fastapi import Request
from starlette.status import HTTP_403_FORBIDDEN, HTTP_401_UNAUTHORIZED
import time
import hashlib
import hmac

from api.config.settings import settings

# API Key 认证
api_key_header = APIKeyHeader(name=settings.API_KEY_HEADER, auto_error=False)


async def verify_api_key(api_key: str = Security(api_key_header)):
    """
    验证 API Key
    """
    # 如果认证未启用，直接通过
    if not settings.AUTH_ENABLED:
        return True

    if not api_key:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail=f"Missing {settings.API_KEY_HEADER} header"
        )

    if api_key not in settings.VALID_API_KEYS:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail="Invalid API Key"
        )

    return api_key


async def verify_optional_api_key(api_key: str = Security(api_key_header)):
    """
    可选的 API Key 验证（用于公共接口）
    """
    # 如果认证未启用，直接通过
    if not settings.AUTH_ENABLED:
        return None

    if api_key and api_key not in settings.VALID_API_KEYS:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail="Invalid API Key"
        )

    return api_key


# 简单签名认证（用于 Webhook）
def verify_signature(payload: dict, signature: str, secret: str) -> bool:
    """
    验证请求签名
    """
    if not signature:
        return False

    # 对 payload 进行排序并生成签名
    sorted_payload = sorted(payload.items())
    message = "&".join([f"{k}={v}" for k, v in sorted_payload])

    expected_signature = hmac.new(
        secret.encode(),
        message.encode(),
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(signature, expected_signature)


# 速率限制（简单版）
class RateLimiter:
    """简单的速率限制器"""

    def __init__(self):
        self.requests = {}

    def is_allowed(self, key: str, limit: int = 60, window: int = 60) -> bool:
        """
        检查是否允许请求
        :param key: 请求标识（如 API Key 或 IP）
        :param limit: 窗口内允许的最大请求数
        :param window: 时间窗口（秒）
        """
        now = time.time()

        if key not in self.requests:
            self.requests[key] = []

        # 清理过期的请求记录
        self.requests[key] = [t for t in self.requests[key] if now - t < window]

        if len(self.requests[key]) >= limit:
            return False

        self.requests[key].append(now)
        return True


rate_limiter = RateLimiter()


def check_rate_limit(api_key: str, limit: int = 60, window: int = 60):
    """
    检查速率限制
    """
    if not rate_limiter.is_allowed(api_key, limit, window):
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded. Max {limit} requests per {window} seconds."
        )
    return True