from selenium import webdriver

from utils.config import config

from utils.logger import logger



def get_driver():


    logger.info(
        "创建Chrome浏览器"
    )


    options = webdriver.ChromeOptions()


    # 加速页面加载
    options.page_load_strategy="eager"


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


    driver=webdriver.Chrome(
        options=options
    )


    driver.maximize_window()


    return driver