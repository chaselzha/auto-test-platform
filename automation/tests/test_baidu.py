# automation/tests/test_baidu.py
import allure
import pytest
from pages.baidu_page import BaiduPage
from utils.config import get_config
from utils.data_reader import load_yaml
from utils.logger import logger

# 加载测试数据
search_cases = load_yaml("data/search_data.yaml")


@allure.feature("百度搜索")
class TestBaiduSearch:

    @pytest.mark.parametrize(
        "case",
        search_cases,
        ids=lambda x: x["title"]
    )
    @allure.story("搜索功能")
    @allure.title("百度搜索测试 - {case[title]}")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_search(self, driver, case):
        """
        测试百度搜索功能
        """
        # ===== 获取配置 =====
        config = get_config()
        keyword = case["keyword"]

        logger.info(f"🔍 开始测试: {keyword}")
        logger.info(f"🌍 当前环境: {config.env}")

        # ===== Step 1: 打开首页 =====
        with allure.step(f"1. 打开百度首页"):
            driver.get(config.base_url)
            allure.attach(
                driver.get_screenshot_as_png(),
                name=f"首页截图_{keyword}",
                attachment_type=allure.attachment_type.PNG
            )
            logger.info(f"✅ 已打开百度首页")

        # ===== Step 2: 创建页面对象并搜索 =====
        page = BaiduPage(driver)

        with allure.step(f"2. 输入搜索词: '{keyword}'"):
            page.search(keyword)
            allure.attach(
                driver.get_screenshot_as_png(),
                name=f"搜索截图_{keyword}",
                attachment_type=allure.attachment_type.PNG
            )
            logger.info(f"✅ 已搜索: {keyword}")

        # ===== Step 3: 验证结果（使用页面对象的验证方法） =====
        with allure.step(f"3. 验证搜索结果"):
            # 👇 调用页面对象的 verify_result 方法
            page.verify_result(keyword)

            allure.attach(
                driver.get_screenshot_as_png(),
                name=f"结果截图_{keyword}",
                attachment_type=allure.attachment_type.PNG
            )
            logger.info(f"✅ 搜索验证通过: {keyword}")

        # ===== Step 4: 记录测试日志 =====
        with allure.step("4. 记录测试日志"):
            allure.attach(
                f"""
                测试用例: {case.get('title', '未知')}
                搜索关键词: {keyword}
                实际标题: {driver.title}
                执行结果: ✅ 通过
                """,
                name=f"测试日志_{keyword}",
                attachment_type=allure.attachment_type.TEXT
            )

        logger.info(f"✅ 测试完成: {keyword}")