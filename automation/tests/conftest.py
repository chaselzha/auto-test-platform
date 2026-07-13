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
#from pages.baidu_page import BaiduPage
from pages.bing_page import BingPage
# ===== 设置编码 =====
os.environ['PYTHONIOENCODING'] = 'utf-8'
os.environ['LANG'] = 'zh_CN.UTF-8'
os.environ['LC_ALL'] = 'zh_CN.UTF-8'

# ===== 全局配置变量 =====
config = None


# ===== 线程安全的目录创建 =====
def ensure_dir(path):
    """线程安全的目录创建"""
    if not os.path.exists(path):
        try:
            os.makedirs(path)
        except FileExistsError:
            pass  # 其他线程已创建


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


# ===== Allure 环境信息 =====
@pytest.fixture(scope="session", autouse=True)
def allure_environment(env):
    """生成 Allure 环境信息"""
    env_file = "automation/reports/allure-results/environment.properties"
    ensure_dir(os.path.dirname(env_file))

    with open(env_file, "w", encoding="utf-8") as f:
        f.write(f"Browser={os.getenv('BROWSER', 'chrome')}\n")
        f.write(f"Environment={env}\n")
        f.write(f"OS={sys.platform}\n")
        f.write(f"Python={sys.version.split()[0]}\n")
        f.write(f"Build={os.getenv('BUILD_NUMBER', 'local')}\n")
        f.write(f"Execution.Time={datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    logger.info(f"✅ Allure 环境信息已生成")
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

    logger.info(f"✅ 浏览器启动成功: {browser}")

    yield driver

    logger.info("🔚 关闭浏览器")
    try:
        driver.quit()
    except Exception as e:
        logger.warning(f"关闭浏览器异常: {e}")


# ===== 页面对象 Fixture =====
@pytest.fixture
def baidu_page(driver):
    """BaiduPage fixture"""
    return BingPage(driver)


# ===== 测试失败时自动截图（线程安全） =====
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
            try:
                # 截图并附加到 Allure
                screenshot = driver.get_screenshot_as_png()
                allure.attach(
                    screenshot,
                    name=f"失败截图_{item.name}",
                    attachment_type=allure.attachment_type.PNG
                )
                logger.error(f"❌ 测试失败: {item.name}")

                # 保存截图到文件（线程安全）
                screenshot_dir = "screenshots"
                ensure_dir(screenshot_dir)

                # 使用时间戳和进程 ID 避免文件名冲突
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                pid = os.getpid()
                safe_name = item.name.replace("[", "_").replace("]", "_").replace("\\", "_")
                screenshot_path = os.path.join(screenshot_dir, f"{safe_name}_{timestamp}_{pid}.png")

                with open(screenshot_path, "wb") as f:
                    f.write(screenshot)
                logger.info(f"📸 截图已保存: {screenshot_path}")
            except Exception as e:
                logger.warning(f"截图保存失败: {e}")


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