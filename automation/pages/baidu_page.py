from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

import time

from common.base_page import BasePage



class BaiduPage(BasePage):
    """
    百度页面对象
    """


    # 百度AI搜索输入框
    search_input = (
        By.ID,
        "chat-textarea"
    )



    def search(self, keyword):
        """
        百度搜索
        """


        element = self.find_element(
            self.search_input
        )


        # 点击输入框
        element.click()


        # 输入关键词
        element.send_keys(
            keyword
        )


        # 等待输入完成
        time.sleep(1)


        # 回车提交
        element.send_keys(
            Keys.ENTER
        )