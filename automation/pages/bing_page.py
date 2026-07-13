# automation/pages/bing_page.py
import allure
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
from common.base_page import BasePage
from utils.logger import logger


class BingPage(BasePage):
    """
    Bing 页面对象
    """

    # Bing 搜索输入框
    search_input = (By.ID, "sb_form_q")
    search_button = (By.ID, "sb_form_go")
    search_results = (By.CSS_SELECTOR, "#b_results .b_algo")
    result_links = (By.CSS_SELECTOR, "#b_results .b_algo h2 a")

    def open(self):
        """打开 Bing 首页"""
        with allure.step(f"打开 Bing 首页: {self.BASE_URL}"):
            self.driver.get(self.BASE_URL)
            self.wait_for_page_load()
            logger.info(f"✅ 已打开 Bing 首页: {self.driver.title}")

    def search(self, keyword):
        """
        执行 Bing 搜索

        Args:
            keyword: 搜索关键词
        """
        logger.info(f"🔍 开始搜索: {keyword}")

        # 1. 查找输入框
        search_input = self.find_element(self.search_input)

        # 2. 清空并输入关键词
        search_input.clear()
        search_input.send_keys(keyword)
        logger.debug(f"✅ 已输入关键词: {keyword}")

        # 3. 点击搜索按钮
        with allure.step("点击搜索按钮"):
            self.click(self.search_button)

        # 4. 等待搜索结果加载
        self.wait_for_search_results()

        logger.info(f"✅ 搜索完成: {keyword}")

    def search_with_enter(self, keyword):
        """使用回车键搜索"""
        logger.info(f"🔍 开始搜索（回车）: {keyword}")

        search_input = self.find_element(self.search_input)
        search_input.clear()
        search_input.send_keys(keyword)
        search_input.send_keys(Keys.RETURN)

        self.wait_for_search_results()
        logger.info(f"✅ 搜索完成（回车）: {keyword}")

    def wait_for_search_results(self, timeout=15):
        """等待搜索结果加载完成"""
        logger.info("⏳ 等待搜索结果加载...")

        try:
            # 等待结果出现
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located(self.search_results)
            )
            logger.info(f"✅ 搜索结果已加载，标题: {self.driver.title}")
            return True
        except TimeoutException:
            # 尝试检查是否有结果
            try:
                WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".b_noresults"))
                )
                logger.warning("⚠️ 没有找到搜索结果")
                return False
            except TimeoutException:
                logger.error("❌ 等待搜索结果超时")
                return False

    def verify_result(self, expected_keyword):
        """
        验证搜索结果

        Args:
            expected_keyword: 期望包含的关键词
        """
        with allure.step(f"验证搜索结果包含: '{expected_keyword}'"):
            # 获取页面标题
            actual_title = self.driver.title
            logger.info(f"📄 页面标题: {actual_title}")

            # Bing 标题通常包含关键词
            assert expected_keyword in actual_title or expected_keyword.lower() in actual_title.lower(), \
                f"标题中不包含关键词 '{expected_keyword}'，实际标题: {actual_title}"

            # 获取结果数量
            results = self.driver.find_elements(*self.search_results)
            logger.info(f"✅ 找到 {len(results)} 个搜索结果")

            # 验证结果不为空
            assert len(results) > 0, "搜索结果为空"

            logger.info(f"✅ 搜索验证通过: {expected_keyword}")
            return len(results)

    def get_first_result(self):
        """获取第一个搜索结果"""
        try:
            elements = self.driver.find_elements(*self.result_links)
            if elements:
                return {
                    "title": elements[0].text,
                    "url": elements[0].get_attribute("href")
                }
        except:
            pass
        return None