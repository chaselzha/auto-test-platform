from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from utils.logger import logger
from utils.decorator import screenshot_on_exception



class BasePage:


    def __init__(
            self,
            driver
    ):

        self.driver = driver



    @screenshot_on_exception
    def find_element(
            self,
            locator
    ):


        logger.info(
            f"查找元素:{locator}"
        )


        return WebDriverWait(
            self.driver,
            10
        ).until(

            EC.visibility_of_element_located(
                locator
            )

        )



    @screenshot_on_exception
    def click(
            self,
            locator
    ):


        element = self.find_element(
            locator
        )

        element.click()



    @screenshot_on_exception
    def input(
            self,
            locator,
            text
    ):


        element = self.find_element(
            locator
        )


        element.clear()

        element.send_keys(
            text
        )