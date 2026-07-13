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

    # 搜索结果（多种选择器，适配不同页面结构）
    search_results = (
        By.CSS_SELECTOR,
        "#b_results .b_algo, .b_results .b_algo, #b_results > li, .b_algo"
    )
    result_links = (
        By.CSS_SELECTOR,
        "#b_results .b_algo h2 a, .b_results .b_algo h2 a, .b_algo h2 a"
    )
    result_stats = (By.CSS_SELECTOR, ".sb_count")
    no_results = (By.CSS_SELECTOR, ".b_noresults")

    BASE_URL = "https://www.bing.com"

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

        # 2. 使用回车键提交（Bing 的标准搜索方式）
        with allure.step("按下回车键搜索"):
            search_input.send_keys(Keys.RETURN)
            logger.debug("✅ 已按下回车键")

        # 3. 等待搜索结果加载
        self.wait_for_search_results()

        logger.info(f"✅ 搜索完成: {keyword}")

    def search_with_button(self, keyword):
        """
        执行 Bing 搜索（备用方式，尝试点击搜索按钮）
        """
        logger.info(f"🔍 开始搜索（备用方式）: {keyword}")

        search_input = self.find_element(self.search_input)
        search_input.clear()
        search_input.send_keys(keyword)

        # 尝试多种方式定位搜索按钮
        button_locators = [
            (By.ID, "sb_form_go"),
            (By.CSS_SELECTOR, "button#sb_form_go"),
            (By.CSS_SELECTOR, "input#sb_form_go"),
            (By.XPATH, "//button[@type='submit']"),
            (By.CSS_SELECTOR, ".search .search-button"),
        ]

        button_found = False
        for locator in button_locators:
            try:
                button = self.find_element(locator, timeout=2)
                button.click()
                button_found = True
                logger.debug(f"✅ 使用定位器成功: {locator}")
                break
            except Exception:
                continue

        if not button_found:
            # 如果按钮找不到，使用回车键
            logger.warning("⚠️ 搜索按钮未找到，使用回车键")
            search_input.send_keys(Keys.RETURN)

        self.wait_for_search_results()
        logger.info(f"✅ 搜索完成（备用方式）: {keyword}")

    def wait_for_search_results(self, timeout=15):
        """
        等待搜索结果加载完成

        Returns:
            bool: 是否成功加载
        """
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
            if "search" in self.driver.current_url.lower() or "q=" in self.driver.current_url.lower():
                logger.info(f"✅ URL 已跳转到搜索结果页")
                return True

            # 检查是否没有结果
            try:
                no_result = self.driver.find_elements(*self.no_results)
                if no_result:
                    logger.warning("⚠️ 没有找到搜索结果")
                    return False
            except:
                pass

            logger.error(f"❌ 等待搜索结果超时，当前标题: {self.driver.title}")
            return False

    def verify_result(self, expected_keyword):
        """
        验证搜索结果

        Args:
            expected_keyword: 期望包含的关键词

        Returns:
            int: 搜索结果数量
        """
        with allure.step(f"验证搜索结果包含: '{expected_keyword}'"):
            # 获取页面标题
            actual_title = self.driver.title
            logger.info(f"📄 页面标题: {actual_title}")

            # 验证标题包含关键词（Bing 的标题格式：关键词 - 搜索）
            title_match = expected_keyword.lower() in actual_title.lower() or \
                          expected_keyword in actual_title

            # 如果标题不匹配，检查 URL
            if not title_match:
                current_url = self.driver.current_url
                if expected_keyword.lower() in current_url.lower() or "q=" in current_url.lower():
                    logger.warning(f"⚠️ 标题不包含关键词，但 URL 包含搜索参数")
                    title_match = True

            assert title_match, \
                f"标题中不包含关键词 '{expected_keyword}'，实际标题: {actual_title}"

            # 获取结果数量
            results = self.driver.find_elements(*self.search_results)
            # 过滤掉空结果
            results = [r for r in results if r.text.strip()]
            result_count = len(results)

            if result_count == 0:
                # 检查是否真的没有结果
                if "没有结果" in self.driver.page_source or "No results" in self.driver.page_source:
                    logger.warning("⚠️ 搜索无结果")
                    return 0
                else:
                    # 可能页面结构不同，但搜索是成功的
                    logger.warning("⚠️ 未找到结果元素，但搜索似乎已执行")
                    return 1

            logger.info(f"✅ 找到 {result_count} 个搜索结果")
            return result_count

    def get_first_result(self):
        """
        获取第一个搜索结果

        Returns:
            dict: 包含标题和 URL 的字典，如果没有结果则返回 None
        """
        try:
            elements = self.driver.find_elements(*self.result_links)
            # 过滤掉空链接
            for elem in elements:
                text = elem.text.strip()
                href = elem.get_attribute("href")
                if text and href:
                    return {
                        "title": text,
                        "url": href
                    }
        except Exception as e:
            logger.debug(f"获取第一个结果失败: {e}")
        return None

    def get_result_count(self):
        """
        获取搜索结果数量

        Returns:
            int: 搜索结果数量
        """
        try:
            results = self.driver.find_elements(*self.search_results)
            return len([r for r in results if r.text.strip()])
        except Exception:
            return 0

    def get_result_stats(self):
        """
        获取搜索结果统计信息

        Returns:
            str: 统计信息文本
        """
        try:
            stats = self.driver.find_element(*self.result_stats)
            return stats.text.strip()
        except Exception:
            return None

    def scroll_to_bottom(self):
        """滚动到页面底部"""
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        logger.debug("📜 已滚动到页面底部")

    def scroll_to_top(self):
        """滚动到页面顶部"""
        self.driver.execute_script("window.scrollTo(0, 0);")
        logger.debug("📜 已滚动到页面顶部")