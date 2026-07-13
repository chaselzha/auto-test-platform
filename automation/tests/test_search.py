# automation/tests/test_search.py
import allure
import pytest
from pages.bing_page import BingPage
from utils.config import get_config
from utils.data_reader import load_yaml
from utils.logger import logger

# 加载测试数据
search_cases = load_yaml("data/search_data.yaml")


@allure.epic("Web自动化测试")
@allure.feature("搜索引擎搜索")
@allure.label("owner", "chaselzha")
@allure.label("module", "search")
class TestSearch:

    @allure.story("搜索功能")
    @allure.title("搜索引擎搜索测试 - {case[title]}")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.tag("smoke", "regression", "web")
    @pytest.mark.parametrize(
        "case",
        search_cases,
        ids=lambda x: x["title"]
    )
    def test_search(self, driver, case):
        """
        测试搜索引擎搜索功能
        """
        # ===== 获取配置 =====
        config = get_config()
        keyword = case["keyword"]

        logger.info(f"🔍 开始测试: {keyword}")
        logger.info(f"🌍 当前环境: {config.env}")

        # ===== Step 1: 打开首页 =====
        with allure.step(f"1. 打开搜索引擎首页"):
            driver.get(config.base_url)
            # 等待页面加载
            driver.implicitly_wait(3)
            allure.attach(
                driver.get_screenshot_as_png(),
                name=f"首页截图_{keyword}",
                attachment_type=allure.attachment_type.PNG
            )
            logger.info(f"✅ 已打开首页")

        # ===== Step 2: 创建页面对象并搜索 =====
        page = BingPage(driver)

        with allure.step(f"2. 输入搜索词: '{keyword}'"):
            page.search(keyword)
            allure.attach(
                driver.get_screenshot_as_png(),
                name=f"搜索截图_{keyword}",
                attachment_type=allure.attachment_type.PNG
            )
            logger.info(f"✅ 已搜索: {keyword}")

        # ===== Step 3: 验证结果 =====
        with allure.step(f"3. 验证搜索结果"):
            result_count = page.verify_result(keyword)

            # 获取第一个结果
            first_result = page.get_first_result()
            if first_result:
                allure.attach(
                    f"第一个结果:\n标题: {first_result['title']}\n链接: {first_result['url']}",
                    name=f"第一个搜索结果_{keyword}",
                    attachment_type=allure.attachment_type.TEXT
                )

            allure.attach(
                driver.get_screenshot_as_png(),
                name=f"结果截图_{keyword}",
                attachment_type=allure.attachment_type.PNG
            )
            logger.info(f"✅ 搜索验证通过: {keyword}, 结果数: {result_count}")

        # ===== Step 4: 记录测试日志 =====
        with allure.step("4. 记录测试日志"):
            allure.attach(
                f"""
                测试用例: {case.get('title', '未知')}
                搜索关键词: {keyword}
                实际标题: {driver.title}
                结果数量: {result_count}
                执行结果: ✅ 通过
                """,
                name=f"测试日志_{keyword}",
                attachment_type=allure.attachment_type.TEXT
            )

        logger.info(f"✅ 测试完成: {keyword}")