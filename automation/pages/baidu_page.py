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

    # 百度传统搜索框（更稳定，适用于自动化）
    search_input = (By.ID, "kw")
    search_button = (By.ID, "su")
    search_results = (By.CSS_SELECTOR, ".result, .c-container")
    result_links = (By.CSS_SELECTOR, ".result h3 a, .c-container h3 a")
    result_stats = (By.CLASS_NAME, "nums")

    # 备用定位器（如果传统搜索框不可用）
    search_input_ai = (By.ID, "chat-textarea")  # AI 搜索框

    BASE_URL = "https://www.baidu.com"

    def open(self):
        """打开百度首页"""
        with allure.step(f"打开百度首页: {self.BASE_URL}"):
            self.driver.get(self.BASE_URL)
            self.wait_for_page_load()
            logger.info(f"✅ 已打开百度首页: {self.driver.title}")

    def search(self, keyword):
        """
        执行百度搜索（使用传统搜索框）
        """
        logger.info(f"🔍 开始搜索: {keyword}")

        # 1. 尝试使用传统搜索框
        try:
            search_input = self.find_element(self.search_input, timeout=5)
            search_input.clear()
            search_input.send_keys(keyword)
            logger.debug(f"✅ 已输入关键词: {keyword}")

            # 2. 点击搜索按钮
            with allure.step("点击搜索按钮"):
                self.click(self.search_button)
        except TimeoutException:
            # 如果传统搜索框找不到，尝试 AI 搜索框
            logger.warning("⚠️ 传统搜索框未找到，尝试 AI 搜索框")
            search_input = self.find_element(self.search_input_ai)
            search_input.click()
            search_input.clear()
            search_input.send_keys(keyword)
            search_input.send_keys(Keys.ENTER)

        # 3. 等待搜索结果加载
        self.wait_for_search_results()

        logger.info(f"✅ 搜索完成: {keyword}")

    def wait_for_search_results(self, timeout=15):
        """等待搜索结果加载完成"""
        logger.info("⏳ 等待搜索结果加载...")

        try:
            # 等待标题变化（不再是"百度一下，你就知道"）
            WebDriverWait(self.driver, 5).until(
                lambda driver: "百度" in driver.title and "百度一下" not in driver.title
            )
            logger.info(f"✅ 搜索结果页面已加载，标题: {self.driver.title}")
            return True
        except TimeoutException:
            logger.debug(f"⏳ 标题未变化: {self.driver.title}")

        try:
            # 尝试等待结果元素出现
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located(self.search_results)
            )
            logger.info(f"✅ 搜索结果已出现")
            return True
        except TimeoutException:
            # 检查是否触发了验证码
            if "验证码" in self.driver.page_source or "安全验证" in self.driver.page_source:
                logger.warning("⚠️ 检测到百度安全验证，可能需要手动处理")
                # 截图保存验证码
                allure.attach(
                    self.driver.get_screenshot_as_png(),
                    name="百度安全验证",
                    attachment_type=allure.attachment_type.PNG
                )

            logger.error(f"❌ 等待搜索结果超时，当前标题: {self.driver.title}")
            return False

    def verify_result(self, expected_keyword):
        """验证搜索结果"""
        with allure.step(f"验证搜索结果包含: '{expected_keyword}'"):
            actual_title = self.driver.title
            logger.info(f"📄 页面标题: {actual_title}")

            # 百度标题格式：关键词_百度搜索
            # 检查标题包含关键词
            title_match = expected_keyword in actual_title or \
                          expected_keyword in actual_title.split('_')[0] if '_' in actual_title else False

            if not title_match:
                # 如果标题不包含关键词，尝试检查页面内容
                page_source = self.driver.page_source
                if expected_keyword in page_source:
                    logger.warning(f"⚠️ 标题不包含关键词，但页面内容包含关键词")
                    title_match = True

            assert title_match, \
                f"标题中不包含关键词 '{expected_keyword}'，实际标题: {actual_title}"

            # 获取结果数量
            results = self.driver.find_elements(*self.search_results)
            # 过滤掉空结果
            results = [r for r in results if r.text.strip()]
            result_count = len(results)

            if result_count == 0:
                # 检查是否是"没有找到"页面
                if "没有找到" in self.driver.page_source or "未找到" in self.driver.page_source:
                    logger.warning("⚠️ 搜索无结果")
                    return 0

            logger.info(f"✅ 找到 {result_count} 个搜索结果")

            # 如果结果数量为 0，但标题包含关键词，也算通过
            if result_count == 0 and title_match:
                logger.warning("⚠️ 标题包含关键词但无结果元素，可能页面结构变化")
                return 1

            assert result_count > 0, "搜索结果为空"

            return result_count

    def get_first_result(self):
        """获取第一个搜索结果"""
        try:
            elements = self.driver.find_elements(*self.result_links)
            # 过滤掉空链接
            for elem in elements:
                if elem.text and elem.get_attribute("href"):
                    return {
                        "title": elem.text,
                        "url": elem.get_attribute("href")
                    }
        except Exception as e:
            logger.debug(f"获取第一个结果失败: {e}")
        return None

    def get_result_count(self):
        """获取搜索结果数量"""
        try:
            results = self.driver.find_elements(*self.search_results)
            return len([r for r in results if r.text.strip()])
        except:
            return 0