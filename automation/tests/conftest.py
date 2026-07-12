import pytest

from utils.driver_factory import get_driver
from utils.config import load_config
from utils.logger import logger



def pytest_addoption(parser):

    parser.addoption(
        "--env",
        action="store",
        default="test",
        help="运行环境"
    )



@pytest.fixture(scope="session")
def env(request):

    return request.config.getoption(
        "--env"
    )



@pytest.fixture(scope="session", autouse=True)
def load_env(env):

    global config

    config = load_config(
        env
    )

    logger.info(
        f"当前环境:{env}"
    )



@pytest.fixture
def driver():

    logger.info(
        "启动浏览器"
    )


    driver = get_driver()


    yield driver


    logger.info(
        "关闭浏览器"
    )


    driver.quit()