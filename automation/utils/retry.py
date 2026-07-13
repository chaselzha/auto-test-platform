# automation/utils/retry.py
import time
import functools
from utils.logger import logger


def retry(max_attempts=3, delay=1, exceptions=(Exception,)):
    """
    重试装饰器

    Args:
        max_attempts: 最大重试次数
        delay: 重试间隔（秒）
        exceptions: 需要重试的异常类型
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_attempts:
                        logger.warning(
                            f"⚠️ {func.__name__} 执行失败 (尝试 {attempt}/{max_attempts}): {e}"
                        )
                        time.sleep(delay)
                    else:
                        logger.error(
                            f"❌ {func.__name__} 执行失败，已重试 {max_attempts} 次: {e}"
                        )
            raise last_exception

        return wrapper

    return decorator


class RetryContext:
    """重试上下文管理器"""

    def __init__(self, max_attempts=3, delay=1, exceptions=(Exception,)):
        self.max_attempts = max_attempts
        self.delay = delay
        self.exceptions = exceptions
        self.attempt = 0
        self.last_exception = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_val is None:
            return True

        if isinstance(exc_val, self.exceptions):
            self.last_exception = exc_val
            self.attempt += 1
            if self.attempt < self.max_attempts:
                logger.warning(f"⚠️ 操作失败，等待 {self.delay}s 后重试 ({self.attempt}/{self.max_attempts})")
                time.sleep(self.delay)
                return False  # 重试
            else:
                logger.error(f"❌ 操作失败，已重试 {self.max_attempts} 次")
                raise exc_val
        return False

    def __call__(self, func):
        """作为装饰器使用"""

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            with self:
                return func(*args, **kwargs)

        return wrapper


def retry_if_false(max_attempts=3, delay=1):
    """如果返回 False 则重试"""

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(1, max_attempts + 1):
                result = func(*args, **kwargs)
                if result is not False:
                    return result
                if attempt < max_attempts:
                    logger.warning(f"⚠️ {func.__name__} 返回 False，等待 {delay}s 后重试")
                    time.sleep(delay)
            return False

        return wrapper

    return decorator