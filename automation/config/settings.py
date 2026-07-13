# automation/config/settings.py
import os
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional, Dict, Any


@dataclass
class BrowserConfig:
    """浏览器配置"""
    type: str = "chrome"
    headless: bool = False
    timeout: int = 10
    window_size: str = "1920x1080"
    user_agent: Optional[str] = None
    proxy: Optional[str] = None


@dataclass
class WaitConfig:
    """等待配置"""
    implicit: int = 10
    explicit: int = 20
    poll_frequency: float = 0.5


@dataclass
class ScreenshotConfig:
    """截图配置"""
    on_failure: bool = True
    save_dir: str = "screenshots"
    format: str = "png"


@dataclass
class LogConfig:
    """日志配置"""
    level: str = "INFO"
    file: str = "logs/test.log"
    rotation: str = "10MB"
    retention: str = "30 days"


@dataclass
class ReportConfig:
    """报告配置"""
    dir: str = "reports/allure-results"
    clean: bool = True


@dataclass
class TestConfig:
    """测试配置"""
    base_url: str = "https://www.bing.com"
    env: str = "test"
    browser: BrowserConfig = field(default_factory=BrowserConfig)
    wait: WaitConfig = field(default_factory=WaitConfig)
    screenshot: ScreenshotConfig = field(default_factory=ScreenshotConfig)
    log: LogConfig = field(default_factory=LogConfig)
    report: ReportConfig = field(default_factory=ReportConfig)

    @classmethod
    def from_yaml(cls, env: str = None):
        """从 YAML 加载配置"""
        import yaml
        env = env or os.getenv("TEST_ENV", "test")
        config_dir = Path(__file__).parent
        config_file = config_dir / f"config_{env}.yaml"

        if config_file.exists():
            with open(config_file, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
                return cls._from_dict(data, env)
        return cls(env=env)

    @classmethod
    def _from_dict(cls, data: Dict[str, Any], env: str):
        """从字典创建配置"""
        browser = BrowserConfig(**data.get("browser", {}))
        wait = WaitConfig(**data.get("wait", {}))
        screenshot = ScreenshotConfig(**data.get("screenshot", {}))
        log = LogConfig(**data.get("log", {}))
        report = ReportConfig(**data.get("report", {}))

        return cls(
            base_url=data.get("base_url", "https://www.bing.com"),
            env=env,
            browser=browser,
            wait=wait,
            screenshot=screenshot,
            log=log,
            report=report
        )

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "base_url": self.base_url,
            "env": self.env,
            "browser": {
                "type": self.browser.type,
                "headless": self.browser.headless,
                "timeout": self.browser.timeout,
                "window_size": self.browser.window_size,
            },
            "wait": {
                "implicit": self.wait.implicit,
                "explicit": self.wait.explicit,
                "poll_frequency": self.wait.poll_frequency,
            },
            "screenshot": {
                "on_failure": self.screenshot.on_failure,
                "save_dir": self.screenshot.save_dir,
            },
            "log": {
                "level": self.log.level,
                "file": self.log.file,
                "rotation": self.log.rotation,
            },
            "report": {
                "dir": self.report.dir,
                "clean": self.report.clean,
            }
        }