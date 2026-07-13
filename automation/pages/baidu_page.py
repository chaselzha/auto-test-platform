# automation/pages/baidu_page.py
import allure
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
from common.base_page import BasePage
from utils.logger import logger


class BaiduPage(BasePage):
    """
    百度页面对象
    """

    # 百度AI搜索输入框
    search_input = (By.ID, "chat-textarea")

    # 搜索结果相关元素
    search_results = (By.CSS_SELECTOR, ".result")  # 普通搜索结果
    ai_results = (By.CLASS_NAME, "ai-result")  # AI搜索结果
    result_container = (By.CLASS_NAME, "content")  # 结果容器

    def search(self, keyword):
        """
        百度搜索 - 使用 AI 搜索框
        """
        logger.info(f"🔍 开始搜索: {keyword}")

        # 1. 查找输入框
        element = self.find_element(self.search_input)

        # 2. 点击输入框
        element.click()
        logger.debug("✅ 已点击输入框")

        # 3. 输入关键词
        element.clear()
        element.send_keys(keyword)
        logger.debug(f"✅ 已输入关键词: {keyword}")

        # 4. 等待输入完成
        time.sleep(0.5)

        # 5. 回车提交
        element.send_keys(Keys.ENTER)
        logger.debug("✅ 已按下回车键")

        # 6. 等待搜索结果加载完成
        self.wait_for_search_results()

        logger.info(f"✅ 搜索完成: {keyword}")

    def wait_for_search_results(self, timeout=15):
        """
        等待搜索结果加载完成

        Returns:
            bool: 是否成功加载
        """
        logger.info("⏳ 等待搜索结果加载...")

        try:
            # 方式1: 等待标题变化（不再是"百度一下，你就知道"）
            WebDriverWait(self.driver, timeout).until(
                lambda driver: "百度" in driver.title and "百度一下" not in driver.title
            )
            logger.info(f"✅ 搜索结果页面已加载，标题: {self.driver.title}")
            return True

        except TimeoutException:
            logger.warning(f"⚠️ 等待标题变化超时，当前标题: {self.driver.title}")

            # 方式2: 尝试等待结果元素出现
            try:
                WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located(self.search_results)
                )
                logger.info("✅ 搜索结果元素已出现")
                return True
            except TimeoutException:
                # 方式3: 尝试等待 AI 结果
                try:
                    WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located(self.ai_results)
                    )
                    logger.info("✅ AI 搜索结果已出现")
                    return True
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

            # 验证标题包含关键词
            assert expected_keyword in actual_title, \
                f"标题中不包含关键词 '{expected_keyword}'，实际标题: {actual_title}"

            logger.info(f"✅ 标题验证通过: {expected_keyword}")
            return True

    def get_result_count(self):
        """
        获取搜索结果数量
        """
        try:
            results = self.driver.find_elements(*self.search_results)
            return len(results)
        except:
            return 0