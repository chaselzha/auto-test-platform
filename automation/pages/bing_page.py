# automation/pages/bing_page.py
import allure
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from common.base_page import BasePage
from utils.logger import logger


class BingPage(BasePage):
    """
    Bing 页面对象
    """

    # Bing 搜索输入框
    search_input = (By.ID, "sb_form_q")

    # 搜索结果
    search_results = (By.CSS_SELECTOR, "#b_results .b_algo, .b_results .b_algo, #b_results > li")
    result_links = (By.CSS_SELECTOR, "#b_results .b_algo h2 a, .b_results .b_algo h2 a")
    result_stats = (By.CSS_SELECTOR, ".sb_count")

    def open(self):
        """打开 Bing 首页"""
        with allure.step(f"打开 Bing 首页: {self.BASE_URL}"):
            self.driver.get(self.BASE_URL)
            self.wait_for_page_load()
            logger.info(f"✅ 已打开 Bing 首页: {self.driver.title}")

    def search(self, keyword):
        """
        执行 Bing 搜索（使用回车键提交）
        """
        logger.info(f"🔍 开始搜索: {keyword}")

        # 1. 查找输入框
        search_input = self.find_element(self.search_input)
        search_input.clear()
        search_input.send_keys(keyword)
        logger.debug(f"✅ 已输入关键词: {keyword}")

        # 2. 使用回车键提交（Bing 没有独立的搜索按钮，回车是标准方式）
        with allure.step("按下回车键搜索"):
            search_input.send_keys(Keys.RETURN)
            logger.debug("✅ 已按下回车键")

        # 3. 等待搜索结果加载
        self.wait_for_search_results()

        logger.info(f"✅ 搜索完成: {keyword}")

    def wait_for_search_results(self, timeout=15):
        """等待搜索结果加载完成"""
        logger.info("⏳ 等待搜索结果加载...")

        try:
            # 等待标题变化（Bing 搜索后标题会变化）
            WebDriverWait(self.driver, 5).until(
                lambda driver: "Bing" in driver.title and "搜索" not in driver.title
            )
            logger.debug(f"✅ 标题已变化: {self.driver.title}")
        except TimeoutException:
            logger.debug(f"⏳ 标题未变化，继续等待结果: {self.driver.title}")

        try:
            # 等待结果出现
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located(self.search_results)
            )
            logger.info(f"✅ 搜索结果已加载，标题: {self.driver.title}")
            return True
        except TimeoutException:
            # 尝试通过 URL 判断是否跳转
            if "search" in self.driver.current_url.lower():
                logger.info(f"✅ URL 已跳转到搜索结果页")
                return True

            # 检查是否有错误页面
            if "没有结果" in self.driver.page_source or "No results" in self.driver.page_source:
                logger.warning("⚠️ 没有找到搜索结果")
                return False

            logger.error(f"❌ 等待搜索结果超时，当前标题: {self.driver.title}")
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

            # 验证标题包含关键词（Bing 的标题格式：关键词 - 搜索）
            assert expected_keyword.lower() in actual_title.lower() or \
                   expected_keyword in actual_title, \
                f"标题中不包含关键词 '{expected_keyword}'，实际标题: {actual_title}"

            # 获取结果数量
            results = self.driver.find_elements(*self.search_results)
            result_count = len(results)
            logger.info(f"✅ 找到 {result_count} 个搜索结果")

            # 验证结果不为空
            assert result_count > 0, "搜索结果为空"

            return result_count

    def get_first_result(self):
        """获取第一个搜索结果"""
        try:
            elements = self.driver.find_elements(*self.result_links)
            if elements:
                return {
                    "title": elements[0].text,
                    "url": elements[0].get_attribute("href")
                }
        except Exception as e:
            logger.debug(f"获取第一个结果失败: {e}")
        return None

    def get_result_count(self):
        """获取搜索结果数量"""
        try:
            results = self.driver.find_elements(*self.search_results)
            return len(results)
        except:
            return 0