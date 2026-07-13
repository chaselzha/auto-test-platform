# automation/tests/conftest.py
import sys
import os
import time
from datetime import datetime
import pytest
import allure
from utils.driver_factory import get_driver
from utils.config import load_config
from utils.logger import logger
from pages.baidu_page import BaiduPage

# ===== 设置编码（Python 3 兼容） =====
# Python 3 默认使用 UTF-8，不需要手动设置
# 只需要设置环境变量即可
os.environ['PYTHONIOENCODING'] = 'utf-8'
os.environ['LANG'] = 'zh_CN.UTF-8'
os.environ['LC_ALL'] = 'zh_CN.UTF-8'

# ===== 全局配置变量 =====
config = None


# ===== 命令行参数 =====
def pytest_addoption(parser):
    parser.addoption(
        "--env",
        action="store",
        default="test",
        help="运行环境 (test/dev/prod)"
    )
    parser.addoption(
        "--browser",
        action="store",
        default="chrome",
        help="浏览器类型 (chrome/firefox)"
    )
    parser.addoption(
        "--headless",
        action="store_true",
        default=False,
        help="是否启用无头模式"
    )


# ===== Session 级别 Fixture =====
@pytest.fixture(scope="session")
def env(request):
    """获取环境参数"""
    return request.config.getoption("--env")


@pytest.fixture(scope="session")
def browser(request):
    """获取浏览器参数"""
    return request.config.getoption("--browser")


@pytest.fixture(scope="session")
def headless(request):
    """获取无头模式参数"""
    return request.config.getoption("--headless")


@pytest.fixture(scope="session", autouse=True)
def load_env(env):
    """加载环境配置（自动执行）"""
    global config
    config = load_config(env)
    logger.info(f"🌍 当前环境: {env}")
    return config


# ===== 浏览器 Fixture =====
@pytest.fixture
def driver(browser, headless):
    """
    WebDriver fixture

    支持参数:
        --browser: chrome/firefox
        --headless: 启用无头模式
    """
    logger.info("🚀 启动浏览器")

    # 设置环境变量，让 get_driver 使用
    os.environ['BROWSER'] = browser
    if headless:
        os.environ['HEADLESS'] = 'true'

    driver = get_driver()

    # 最大化窗口
    driver.maximize_window()
    driver.implicitly_wait(10)

    logger.info(f"✅ 浏览器启动成功: {browser}")

    yield driver

    logger.info("🔚 关闭浏览器")
    driver.quit()


# ===== 页面对象 Fixture =====
@pytest.fixture
def baidu_page(driver):
    """
    BaiduPage fixture
    返回已初始化的百度页面对象
    """
    return BaiduPage(driver)


# ===== 测试失败时自动截图 =====
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    测试失败时自动截图并附加到 Allure 报告
    """
    outcome = yield
    rep = outcome.get_result()

    if rep.when == "call" and rep.failed:
        # 获取 driver
        driver = item.funcargs.get("driver")
        if driver:
            # 截图并附加到 Allure
            screenshot = driver.get_screenshot_as_png()
            allure.attach(
                screenshot,
                name=f"失败截图_{item.name}",
                attachment_type=allure.attachment_type.PNG
            )
            logger.error(f"❌ 测试失败: {item.name}")

            # 保存截图到文件（备用）
            screenshot_dir = "screenshots"
            if not os.path.exists(screenshot_dir):
                os.makedirs(screenshot_dir)

            # 使用 datetime 生成时间戳
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            screenshot_path = os.path.join(screenshot_dir, f"{item.name}_{timestamp}.png")

            with open(screenshot_path, "wb") as f:
                f.write(screenshot)
            logger.info(f"📸 截图已保存: {screenshot_path}")


# ===== 测试会话开始/结束钩子 =====
def pytest_sessionstart(session):
    """测试会话开始时执行"""
    logger.info("=" * 50)
    logger.info("🧪 自动化测试会话开始")
    logger.info("=" * 50)


def pytest_sessionfinish(session, exitstatus):
    """测试会话结束时执行"""
    logger.info("=" * 50)
    logger.info("✅ 自动化测试会话结束")
    logger.info("=" * 50)


# ===== 测试用例执行前后钩子 =====
@pytest.fixture(autouse=True)
def test_logging(request):
    """自动记录测试用例执行"""
    test_name = request.node.name
    logger.info(f"▶️ 开始执行测试: {test_name}")

    yield

    logger.info(f"✅ 测试执行完成: {test_name}")