# automation/utils/driver_factory.py
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from .logger import logger


def get_driver(browser_type=None, headless=None):
    """
    获取 WebDriver 实例

    Args:
        browser_type: 浏览器类型，默认从配置读取
        headless: 是否无头模式，默认从配置读取

    Returns:
        WebDriver 实例
    """
    # 延迟导入配置，避免循环导入
    try:
        from .config import get_config
        config = get_config()
        if browser_type is None:
            browser_type = config.browser_type
        if headless is None:
            headless = config.headless
    except Exception as e:
        logger.debug(f"使用环境变量配置: {e}")
        browser_type = browser_type or os.getenv("BROWSER", "chrome")
        headless = headless or os.getenv("HEADLESS", "false").lower() == "true"

    browser_type = browser_type.lower()
    logger.info(f"🚀 启动浏览器: {browser_type} (headless={headless})")

    if browser_type == "chrome":
        return _create_chrome_driver(headless)
    elif browser_type == "firefox":
        return _create_firefox_driver(headless)
    elif browser_type == "edge":
        return _create_edge_driver(headless)
    else:
        raise ValueError(f"不支持的浏览器类型: {browser_type}")


def _create_chrome_driver(headless=False):
    """创建 Chrome 驱动（含反检测配置）"""
    options = ChromeOptions()

    # ===== 基础配置 =====
    options.add_argument("--start-maximized")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--lang=zh-CN")

    # ===== 反检测配置（避免被识别为自动化工具） =====
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    # 设置 User-Agent（模拟真实浏览器）
    options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36")

    # 无头模式
    if headless:
        options.add_argument("--headless")
        options.add_argument("--window-size=1920,1080")
        logger.info("🔇 Chrome 无头模式已启用")

    # 使用 WebDriver Manager 自动管理驱动
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    # ===== 执行反检测 JS =====
    try:
        driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
            'source': '''
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5]
                });
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['zh-CN', 'zh']
                });
            '''
        })
    except Exception as e:
        logger.debug(f"CDP 命令执行失败: {e}")

    # 设置隐式等待
    try:
        from .config import get_config
        config = get_config()
        driver.implicitly_wait(config.implicit_wait)
    except Exception:
        driver.implicitly_wait(10)

    logger.info("✅ Chrome 浏览器启动成功")
    return driver


def _create_firefox_driver(headless=False):
    """创建 Firefox 驱动"""
    options = FirefoxOptions()
    options.add_argument("--start-maximized")

    # 无头模式
    if headless:
        options.add_argument("--headless")
        options.add_argument("--window-size=1920,1080")
        logger.info("🔇 Firefox 无头模式已启用")

    # 语言和反检测设置
    options.set_preference("intl.accept_languages", "zh-CN")
    options.set_preference("dom.webdriver.enabled", False)
    options.set_preference("useAutomationExtension", False)

    # 使用 WebDriver Manager 自动管理驱动
    service = FirefoxService(GeckoDriverManager().install())
    driver = webdriver.Firefox(service=service, options=options)

    try:
        from .config import get_config
        config = get_config()
        driver.implicitly_wait(config.implicit_wait)
    except Exception:
        driver.implicitly_wait(10)

    logger.info("✅ Firefox 浏览器启动成功")
    return driver


def _create_edge_driver(headless=False):
    """创建 Edge 驱动"""
    from selenium.webdriver.edge.service import Service as EdgeService
    from selenium.webdriver.edge.options import Options as EdgeOptions
    from webdriver_manager.microsoft import EdgeChromiumDriverManager

    options = EdgeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--lang=zh-CN")

    if headless:
        options.add_argument("--headless")
        options.add_argument("--window-size=1920,1080")
        logger.info("🔇 Edge 无头模式已启用")

    service = EdgeService(EdgeChromiumDriverManager().install())
    driver = webdriver.Edge(service=service, options=options)

    try:
        from .config import get_config
        config = get_config()
        driver.implicitly_wait(config.implicit_wait)
    except Exception:
        driver.implicitly_wait(10)

    logger.info("✅ Edge 浏览器启动成功")
    return driver


def quit_driver(driver):
    """安全关闭浏览器"""
    try:
        if driver:
            driver.quit()
            logger.info("🔚 浏览器已关闭")
            return True
    except Exception as e:
        logger.error(f"关闭浏览器失败: {e}")
    return False


def get_browser_info(driver):
    """获取浏览器信息"""
    try:
        capabilities = driver.capabilities
        return {
            "browser_name": capabilities.get("browserName", "unknown"),
            "browser_version": capabilities.get("browserVersion", "unknown"),
            "platform": capabilities.get("platformName", "unknown"),
            "session_id": driver.session_id,
        }
    except Exception as e:
        logger.error(f"获取浏览器信息失败: {e}")
        return {
            "browser_name": "unknown",
            "browser_version": "unknown",
            "platform": "unknown",
            "session_id": None,
        }