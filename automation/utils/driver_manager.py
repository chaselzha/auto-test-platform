from selenium import webdriver

from utils.config import config
from utils.logger import logger



class DriverManager:


    _driver = None



    @classmethod
    def create_driver(cls):


        logger.info(
            "创建Chrome浏览器"
        )


        options = webdriver.ChromeOptions()


        # 无头模式
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


        cls._driver = webdriver.Chrome(
            options=options
        )


        cls._driver.maximize_window()


        return cls._driver



    @classmethod
    def get_driver(cls):


        if cls._driver is None:

            return cls.create_driver()


        return cls._driver



    @classmethod
    def quit_driver(cls):


        if cls._driver:


            logger.info(
                "关闭浏览器"
            )


            cls._driver.quit()


            cls._driver = None