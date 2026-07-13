# automation/utils/driver_factory.py
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from utils.logger import logger

# ===== 延迟导入 config，避免循环导入 =====
_config = None


def _get_config():
    """延迟加载 config，避免循环导入"""
    global _config
    if _config is None:
        from utils.config import config
        _config = config
    return _config


def get_driver(browser_type=None, headless=None):
    """
    获取 WebDriver 实例

    Args:
        browser_type: 浏览器类型，默认从配置读取
        headless: 是否无头模式，默认从配置读取

    Returns:
        WebDriver 实例
    """
    config = _get_config()

    # 从配置或参数获取
    if browser_type is None:
        browser_type = config.browser_type

    if headless is None:
        headless = config.headless

    browser_type = browser_type.lower()
    logger.info(f"🚀 启动浏览器: {browser_type} (headless={headless})")

    if browser_type == "chrome":
        return _create_chrome_driver(headless)
    elif browser_type == "firefox":
        return _create_firefox_driver(headless)
    else:
        raise ValueError(f"不支持的浏览器类型: {browser_type}")


def _create_chrome_driver(headless=False):
    """创建 Chrome 驱动"""
    config = _get_config()

    options = ChromeOptions()

    options.add_argument("--start-maximized")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--lang=zh-CN")

    if headless:
        options.add_argument("--headless")
        options.add_argument("--window-size=1920,1080")
        logger.info("🔇 Chrome 无头模式已启用")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    # 设置隐式等待
    driver.implicitly_wait(config.implicit_wait)

    logger.info("✅ Chrome 浏览器启动成功")
    return driver


def _create_firefox_driver(headless=False):
    """创建 Firefox 驱动"""
    config = _get_config()

    options = FirefoxOptions()
    options.add_argument("--start-maximized")

    if headless:
        options.add_argument("--headless")
        options.add_argument("--window-size=1920,1080")
        logger.info("🔇 Firefox 无头模式已启用")

    options.set_preference("intl.accept_languages", "zh-CN")

    service = FirefoxService(GeckoDriverManager().install())
    driver = webdriver.Firefox(service=service, options=options)

    driver.implicitly_wait(config.implicit_wait)

    logger.info("✅ Firefox 浏览器启动成功")
    return driver