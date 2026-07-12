from selenium import webdriver

from utils.logger import logger
from utils.config import config



def get_driver():

    logger.info(
        "启动浏览器:chrome"
    )


    options = webdriver.ChromeOptions()


    if config["browser"]["headless"]:

        options.add_argument(
            "--headless"
        )


    options.add_argument(
        "--disable-gpu"
    )


    options.add_argument(
        "--window-size=1920,1080"
    )


    driver = webdriver.Chrome(
        options=options
    )


    driver.maximize_window()


    return driver