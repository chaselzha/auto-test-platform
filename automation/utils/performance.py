# automation/utils/performance.py
import time
from functools import wraps
from contextlib import contextmanager
from utils.logger import logger


class PerformanceMonitor:
    """性能监控"""

    _metrics = {}

    @classmethod
    def record(cls, name, duration):
        """记录性能指标"""
        if name not in cls._metrics:
            cls._metrics[name] = []
        cls._metrics[name].append(duration)

    @classmethod
    def get_stats(cls, name):
        """获取统计信息"""
        data = cls._metrics.get(name, [])
        if not data:
            return None
        return {
            "count": len(data),
            "min": min(data),
            "max": max(data),
            "avg": sum(data) / len(data),
            "total": sum(data)
        }

    @classmethod
    def get_all_stats(cls):
        """获取所有统计信息"""
        return {name: cls.get_stats(name) for name in cls._metrics}

    @classmethod
    def reset(cls):
        """重置所有指标"""
        cls._metrics.clear()

    @classmethod
    def report(cls):
        """生成性能报告"""
        stats = cls.get_all_stats()
        report = "\n" + "=" * 50 + "\n"
        report += "📊 性能报告\n"
        report += "=" * 50 + "\n"
        for name, data in stats.items():
            if data:
                report += f"{name}:\n"
                report += f"  - 执行次数: {data['count']}\n"
                report += f"  - 平均耗时: {data['avg']:.3f}s\n"
                report += f"  - 最小耗时: {data['min']:.3f}s\n"
                report += f"  - 最大耗时: {data['max']:.3f}s\n"
                report += f"  - 总耗时: {data['total']:.3f}s\n"
        report += "=" * 50 + "\n"
        return report


def measure_time(name=None):
    """计时装饰器"""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start = time.time()
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start
                metric_name = name or func.__name__
                PerformanceMonitor.record(metric_name, duration)
                if duration > 5:
                    logger.warning(f"⏱️ {metric_name} 执行较慢: {duration:.3f}s")
                else:
                    logger.debug(f"⏱️ {metric_name} 耗时: {duration:.3f}s")
                return result
            except Exception as e:
                duration = time.time() - start
                logger.error(f"❌ {func.__name__} 执行失败，耗时: {duration:.3f}s")
                raise

        return wrapper

    return decorator


@contextmanager
def measure_context(name):
    """上下文计时器"""
    start = time.time()
    try:
        yield
    finally:
        duration = time.time() - start
        PerformanceMonitor.record(name, duration)
        logger.debug(f"⏱️ {name} 耗时: {duration:.3f}s")