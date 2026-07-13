# automation/common/browser.py
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


class Browser:
    """浏览器管理类"""

    @staticmethod
    def get_driver(browser_type="chrome", headless=False):
        """获取浏览器驱动"""
        if browser_type == "chrome":
            return Browser._create_chrome_driver(headless)
        elif browser_type == "firefox":
            return Browser._create_firefox_driver(headless)
        else:
            raise ValueError(f"不支持的浏览器: {browser_type}")

    @staticmethod
    def _create_chrome_driver(headless=False):
        """创建 Chrome 驱动"""
        options = Options()
        options.add_argument("--start-maximized")
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")

        if headless:
            options.add_argument("--headless")
            options.add_argument("--window-size=1920,1080")

        service = Service(ChromeDriverManager().install())
        return webdriver.Chrome(service=service, options=options)

    @staticmethod
    def _create_firefox_driver(headless=False):
        """创建 Firefox 驱动"""
        from selenium.webdriver.firefox.options import Options as FirefoxOptions
        from selenium.webdriver.firefox.service import Service as FirefoxService
        from webdriver_manager.firefox import GeckoDriverManager

        options = FirefoxOptions()
        options.add_argument("--start-maximized")

        if headless:
            options.add_argument("--headless")
            options.add_argument("--window-size=1920,1080")

        service = FirefoxService(GeckoDriverManager().install())
        return webdriver.Firefox(service=service, options=options)

    @staticmethod
    def quit_driver(driver):
        """安全关闭浏览器"""
        if driver:
            try:
                driver.quit()
                return True
            except Exception:
                return False
        return False