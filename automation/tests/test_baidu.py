# automation/tests/test_baidu.py
import allure
import pytest
from pages.baidu_page import BaiduPage
from utils.logger import logger


@allure.epic("Web自动化测试")
@allure.feature("百度搜索")
@allure.label("owner", "chaselzha")
@allure.label("module", "search")
class TestBaiduSearch:
    """百度搜索功能测试"""

    @allure.story("搜索功能")
    @allure.title("百度搜索测试 - 关键词: {keyword}")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.tag("smoke", "regression", "web")
    @allure.link("https://github.com/chaselzha/auto-test-platform", name="项目仓库")
    @pytest.mark.parametrize(
        "keyword, expected_title",
        [
            ("pytest", "pytest"),
            ("selenium", "selenium"),
            ("python", "python"),
            ("自动化测试", "自动化测试"),
        ],
        ids=[
            "搜索pytest",
            "搜索selenium",
            "搜索python",
            "搜索自动化测试"
        ]
    )
    def test_search(self, baidu_page, keyword, expected_title):
        """
        测试百度搜索功能

        :param baidu_page: 百度页面 fixture
        :param keyword: 搜索关键词
        :param expected_title: 预期标题包含的关键词
        """
        logger.info(f"🔍 开始执行搜索测试，关键词: {keyword}")

        # 1. 打开百度首页
        baidu_page.open()
        allure.attach(
            baidu_page.driver.get_screenshot_as_png(),
            name=f"首页截图_{keyword}",
            attachment_type=allure.attachment_type.PNG
        )

        # 2. 执行搜索
        baidu_page.search(keyword)
        allure.attach(
            baidu_page.driver.get_screenshot_as_png(),
            name=f"搜索结果截图_{keyword}",
            attachment_type=allure.attachment_type.PNG
        )

        # 3. 验证结果
        result_count = baidu_page.verify_result(expected_title)

        # 4. 记录日志
        allure.attach(
            f"""
            搜索关键词    : {keyword}
            预期结果      : {expected_title}
            当前标题      : {baidu_page.driver.title}
            结果数量      : {result_count}
            执行结果      : ✅ 通过
            """,
            name=f"测试日志_{keyword}",
            attachment_type=allure.attachment_type.TEXT
        )

        logger.info(f"✅ 搜索测试通过: {keyword}")

    @allure.story("搜索功能")
    @allure.title("百度搜索 - 回车键搜索")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("smoke", "web")
    @pytest.mark.parametrize(
        "keyword",
        ["pytest", "selenium"],
        ids=["回车搜索pytest", "回车搜索selenium"]
    )
    def test_search_with_enter(self, baidu_page, keyword):
        """
        测试使用回车键进行搜索
        """
        logger.info(f"🔍 开始回车搜索测试: {keyword}")

        baidu_page.open()
        baidu_page.search_with_enter(keyword)

        allure.attach(
            baidu_page.driver.get_screenshot_as_png(),
            name=f"回车搜索结果_{keyword}",
            attachment_type=allure.attachment_type.PNG
        )

        baidu_page.verify_result(keyword)
        logger.info(f"✅ 回车搜索测试通过: {keyword}")

    @allure.story("搜索功能")
    @allure.title("百度搜索 - 空关键词测试")
    @allure.severity(allure.severity_level.MINOR)
    @allure.tag("edge", "negative")
    def test_search_empty_keyword(self, baidu_page):
        """
        测试空关键词搜索（边界测试）
        """
        logger.info("🔍 开始空关键词搜索测试")

        baidu_page.open()
        baidu_page.search("")

        allure.attach(
            baidu_page.driver.get_screenshot_as_png(),
            name="空关键词搜索结果",
            attachment_type=allure.attachment_type.PNG
        )

        # 验证仍在百度首页
        assert "baidu" in baidu_page.driver.current_url.lower()
        assert "百度" in baidu_page.driver.title

        logger.info("✅ 空关键词搜索测试通过")

    @allure.story("搜索功能")
    @allure.title("百度搜索 - 特殊字符测试")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("edge", "special-char")
    @pytest.mark.parametrize(
        "keyword",
        [
            "!@#$%^&*()",
            "测试 空格 测试",
            "1234567890",
            "中英文混合 Test 123",
        ],
        ids=[
            "特殊符号",
            "包含空格",
            "纯数字",
            "中英混合"
        ]
    )
    def test_search_special_chars(self, baidu_page, keyword):
        """
        测试特殊字符搜索
        """
        logger.info(f"🔍 开始特殊字符搜索测试: {keyword}")

        baidu_page.open()
        baidu_page.search(keyword)

        allure.attach(
            baidu_page.driver.get_screenshot_as_png(),
            name=f"特殊字符搜索结果_{keyword[:10]}",
            attachment_type=allure.attachment_type.PNG
        )

        # 验证页面标题不为空
        assert baidu_page.driver.title, "搜索后页面标题不应为空"
        logger.info(f"✅ 特殊字符搜索测试通过: {keyword}")

    @allure.story("搜索功能")
    @allure.title("百度搜索 - 搜索结果页滚动测试")
    @allure.severity(allure.severity_level.MINOR)
    @allure.tag("ui", "scroll")
    def test_search_scroll(self, baidu_page):
        """
        测试搜索结果页滚动功能
        """
        keyword = "pytest"
        logger.info("🔍 开始页面滚动测试")

        baidu_page.open()
        baidu_page.search(keyword)

        # 滚动到底部
        baidu_page.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        allure.attach(
            baidu_page.driver.get_screenshot_as_png(),
            name="页面底部截图",
            attachment_type=allure.attachment_type.PNG
        )

        # 滚动回顶部
        baidu_page.driver.execute_script("window.scrollTo(0, 0);")
        allure.attach(
            baidu_page.driver.get_screenshot_as_png(),
            name="页面顶部截图",
            attachment_type=allure.attachment_type.PNG
        )

        logger.info("✅ 页面滚动测试通过")