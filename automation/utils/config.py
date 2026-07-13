# automation/tests/test_baidu.py
import allure
import pytest
from pages.baidu_page import BaiduPage
from utils.logger import logger
from utils.config import config  # 👈 导入 config


@allure.epic("Web自动化测试")
@allure.feature("百度搜索")
@allure.label("owner", "chaselzha")
@allure.label("module", "search")
class TestBaiduSearch:

    @allure.story("搜索功能")
    @allure.title("百度搜索测试 - 关键词: {keyword}")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.tag("smoke", "regression", "web")
    @allure.link("https://github.com/chaselzha/auto-test-platform", name="项目仓库")
    @pytest.mark.parametrize(
        "keyword",
        ["pytest", "selenium", "python"],
        ids=["搜索pytest", "搜索selenium", "搜索python"]
    )
    def test_search(self, baidu_page, keyword):
        """
        测试百度搜索功能
        """
        # ===== 从 config 获取基础 URL =====
        base_url = config.base_url  # 👈 使用属性方式访问
        logger.info(f"🌍 当前环境: {config.env}")
        logger.info(f"🔍 开始执行搜索测试，关键词: {keyword}")

        # 1. 打开百度首页
        with allure.step(f"1. 打开百度首页"):
            baidu_page.driver.get(base_url)
            allure.attach(
                baidu_page.driver.get_screenshot_as_png(),
                name=f"首页截图_{keyword}",
                attachment_type=allure.attachment_type.PNG
            )

        # 2. 执行搜索
        with allure.step(f"2. 输入搜索词: '{keyword}'"):
            baidu_page.search(keyword)
            allure.attach(
                baidu_page.driver.get_screenshot_as_png(),
                name=f"搜索结果截图_{keyword}",
                attachment_type=allure.attachment_type.PNG
            )

        # 3. 验证结果
        with allure.step(f"3. 验证搜索结果包含 '{keyword}'"):
            baidu_page.verify_result(keyword)

        # 4. 记录日志
        with allure.step("4. 记录测试日志"):
            allure.attach(
                f"""
                搜索关键词    : {keyword}
                当前标题      : {baidu_page.driver.title}
                执行结果      : ✅ 通过
                """,
                name=f"测试日志_{keyword}",
                attachment_type=allure.attachment_type.TEXT
            )

        logger.info(f"✅ 搜索测试通过: {keyword}")