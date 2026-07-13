# automation/utils/config.py
import os
import yaml
from pathlib import Path
from utils.logger import logger


class Config:
    """配置管理类 - 支持多环境、环境变量覆盖"""

    _instance = None
    _config = None

    def __new__(cls, *args, **kwargs):
        """单例模式"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, env=None):
        """初始化配置"""
        if self._config is not None:
            return

        self.env = env or os.getenv("TEST_ENV", "test")
        self._config = self._load_config()

        # 合并环境变量
        self._merge_env_vars()

        logger.info(f"🌍 加载配置完成，环境: {self.env}")

    def _load_config(self):
        """加载配置文件"""
        # 获取项目根目录
        current_dir = Path(__file__).parent  # automation/utils/
        base_dir = current_dir.parent.parent  # 项目根目录

        config_file = base_dir / "config" / f"config_{self.env}.yaml"

        # 默认配置
        default_config = self._get_default_config()

        # 如果配置文件存在，合并配置
        if config_file.exists():
            try:
                with open(config_file, "r", encoding="utf-8") as f:
                    file_config = yaml.safe_load(f)
                    if file_config:
                        default_config.update(file_config)
                logger.debug(f"✅ 加载配置文件: {config_file}")
            except Exception as e:
                logger.warning(f"⚠️ 加载配置文件失败: {e}")
        else:
            logger.warning(f"⚠️ 配置文件不存在: {config_file}，使用默认配置")

        return default_config

    def _get_default_config(self):
        """获取默认配置"""
        return {
            "base_url": "https://www.baidu.com",
            "browser": {
                "type": "chrome",
                "headless": False,
                "timeout": 10,
                "window_size": "1920x1080"
            },
            "wait": {
                "implicit": 10,
                "explicit": 20,
                "poll_frequency": 0.5
            },
            "screenshot": {
                "on_failure": True,
                "save_dir": "screenshots"
            },
            "log": {
                "level": "INFO",
                "file": "logs/test.log",
                "rotation": "10MB"
            },
            "report": {
                "dir": "reports/allure-results",
                "clean": True
            }
        }

    def _merge_env_vars(self):
        """合并环境变量覆盖"""
        # 浏览器类型
        if os.getenv("BROWSER"):
            self._config["browser"]["type"] = os.getenv("BROWSER")
            logger.debug(f"📌 使用环境变量 BROWSER={os.getenv('BROWSER')}")

        # 无头模式
        if os.getenv("HEADLESS"):
            self._config["browser"]["headless"] = os.getenv("HEADLESS").lower() == "true"
            logger.debug(f"📌 使用环境变量 HEADLESS={os.getenv('HEADLESS')}")

        # 基础 URL
        if os.getenv("BASE_URL"):
            self._config["base_url"] = os.getenv("BASE_URL")
            logger.debug(f"📌 使用环境变量 BASE_URL={os.getenv('BASE_URL')}")

    def get(self, key, default=None):
        """
        获取配置值，支持点号分隔的键

        Args:
            key: 配置键，如 "browser.type"
            default: 默认值

        Returns:
            配置值
        """
        keys = key.split(".")
        value = self._config

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def set(self, key, value):
        """
        设置配置值

        Args:
            key: 配置键，如 "browser.type"
            value: 配置值
        """
        keys = key.split(".")
        target = self._config

        for k in keys[:-1]:
            if k not in target:
                target[k] = {}
            target = target[k]

        target[keys[-1]] = value

    @property
    def base_url(self):
        """获取基础 URL"""
        return self.get("base_url")

    @property
    def browser_type(self):
        """获取浏览器类型"""
        return self.get("browser.type", "chrome")

    @property
    def headless(self):
        """获取无头模式"""
        return self.get("browser.headless", False)

    @property
    def timeout(self):
        """获取超时时间"""
        return self.get("browser.timeout", 10)

    @property
    def implicit_wait(self):
        """获取隐式等待时间"""
        return self.get("wait.implicit", 10)

    @property
    def explicit_wait(self):
        """获取显式等待时间"""
        return self.get("wait.explicit", 20)

    @property
    def screenshot_dir(self):
        """获取截图目录"""
        return self.get("screenshot.save_dir", "screenshots")

    @property
    def allure_dir(self):
        """获取 Allure 报告目录"""
        return self.get("report.dir", "reports/allure-results")

    def __getitem__(self, key):
        """支持 config['key'] 访问"""
        return self.get(key)

    def __setitem__(self, key, value):
        """支持 config['key'] = value 赋值"""
        self.set(key, value)

    def __repr__(self):
        return f"Config(env='{self.env}')"

    def reload(self, env=None):
        """重新加载配置"""
        if env:
            self.env = env
        self._config = self._load_config()
        self._merge_env_vars()
        logger.info(f"🔄 配置已重新加载，环境: {self.env}")


# ===== 便捷函数 =====

def load_config(env=None):
    """
    加载配置（兼容旧代码）

    Args:
        env: 环境名称

    Returns:
        Config 实例
    """
    return Config(env)


def get_config():
    """获取全局配置实例"""
    return Config()


# ===== 创建全局配置实例 =====
config = Config()

# ===== 便捷导入 =====
__all__ = [
    'Config',
    'load_config',
    'get_config',
    'config',
]