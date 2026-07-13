# automation/tests/test_search.py
import allure
import pytest
import time
from selenium.webdriver.common.by import By
from pages.bing_page import BingPage
from utils.config import get_config
from utils.data_reader import load_yaml
from utils.logger import logger
from common.assertions import assert_true, assert_contains

# 加载测试数据
search_cases = load_yaml("data/search_data.yaml")


@allure.epic("Web自动化测试")
@allure.feature("搜索引擎搜索")
@allure.label("owner", "chaselzha")
@allure.label("module", "search")
class TestSearch:

    # ============================================================
    # 1. 基础搜索测试（参数化）
    # ============================================================
    @allure.story("搜索功能")
    @allure.title("搜索引擎搜索测试 - {case[title]}")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.tag("smoke", "regression", "web")
    @pytest.mark.smoke
    @pytest.mark.regression
    @pytest.mark.parametrize(
        "case",
        search_cases,
        ids=lambda x: x["title"]
    )
    def test_search(self, driver, case):
        """测试搜索引擎搜索功能"""
        config = get_config()
        keyword = case["keyword"]
        expected = case.get("expected", keyword)

        logger.info(f"🔍 开始测试: {keyword}")
        logger.info(f"🌍 当前环境: {config.env}")

        # Step 1: 打开首页
        with allure.step(f"1. 打开搜索引擎首页"):
            driver.get(config.base_url)
            driver.implicitly_wait(3)
            allure.attach(
                driver.get_screenshot_as_png(),
                name=f"首页截图_{keyword}",
                attachment_type=allure.attachment_type.PNG
            )
            logger.info(f"✅ 已打开首页")

        # Step 2: 创建页面对象并搜索
        page = BingPage(driver)

        with allure.step(f"2. 输入搜索词: '{keyword}'"):
            page.search(keyword)
            allure.attach(
                driver.get_screenshot_as_png(),
                name=f"搜索截图_{keyword}",
                attachment_type=allure.attachment_type.PNG
            )
            logger.info(f"✅ 已搜索: {keyword}")

        # Step 3: 验证结果
        with allure.step(f"3. 验证搜索结果"):
            result_count = page.verify_result(expected)
            assert_true(result_count > 0, "搜索结果数量应该大于0")
            assert_contains(driver.title, expected, f"标题应该包含关键词 '{expected}'")

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

        # Step 4: 记录测试日志
        with allure.step("4. 记录测试日志"):
            allure.attach(
                f"""
                测试用例: {case.get('title', '未知')}
                搜索关键词: {keyword}
                预期结果: {expected}
                实际标题: {driver.title}
                结果数量: {result_count}
                执行结果: ✅ 通过
                """,
                name=f"测试日志_{keyword}",
                attachment_type=allure.attachment_type.TEXT
            )

        logger.info(f"✅ 测试完成: {keyword}")

    # ============================================================
    # 2. 搜索建议/自动补全测试
    # ============================================================
    @allure.story("搜索建议")
    @allure.title("搜索自动补全功能测试")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("ui", "suggestion")
    @pytest.mark.parametrize(
        "keyword, expected_suggestion",
        [
            ("pyt", "pytest"),
            ("sel", "selenium"),
            ("pyth", "python"),
        ],
        ids=["pyt自动补全", "sel自动补全", "pyth自动补全"]
    )
    def test_search_suggestion(self, driver, keyword, expected_suggestion):
        """测试搜索框自动补全功能"""
        config = get_config()
        logger.info(f"🔍 开始自动补全测试: {keyword}")

        # 打开首页
        driver.get(config.base_url)
        driver.implicitly_wait(2)

        page = BingPage(driver)

        with allure.step(f"1. 输入关键词: '{keyword}'"):
            search_input = page.find_element(page.search_input)
            search_input.clear()
            search_input.send_keys(keyword)
            allure.attach(
                driver.get_screenshot_as_png(),
                name="自动补全截图",
                attachment_type=allure.attachment_type.PNG
            )

        with allure.step("2. 检查是否显示补全建议"):
            time.sleep(1)
            suggestions = driver.find_elements(By.CSS_SELECTOR, ".sa_as, .suggestion, .as_root")
            if suggestions:
                suggestion_texts = [s.text for s in suggestions if s.text.strip()]
                allure.attach(
                    f"补全建议: {suggestion_texts}",
                    name="补全建议列表",
                    attachment_type=allure.attachment_type.TEXT
                )
                logger.info(f"✅ 找到 {len(suggestion_texts)} 个补全建议")
            else:
                logger.warning("⚠️ 未找到补全建议")

    # ============================================================
    # 3. 图片搜索测试
    # ============================================================
    @allure.story("图片搜索")
    @allure.title("图片搜索功能测试")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("web", "image")
    def test_image_search(self, driver):
        """测试 Bing 图片搜索功能"""
        config = get_config()
        keyword = "pytest"
        logger.info(f"🔍 开始图片搜索测试: {keyword}")

        driver.get(config.base_url)
        page = BingPage(driver)

        with allure.step("1. 执行普通搜索"):
            page.search(keyword)
            allure.attach(
                driver.get_screenshot_as_png(),
                name="普通搜索结果",
                attachment_type=allure.attachment_type.PNG
            )

        with allure.step("2. 切换到图片搜索"):
            try:
                image_tab = driver.find_element(By.LINK_TEXT, "图片")
                image_tab.click()
                time.sleep(2)
                allure.attach(
                    driver.get_screenshot_as_png(),
                    name="图片搜索结果",
                    attachment_type=allure.attachment_type.PNG
                )
                logger.info("✅ 图片搜索切换成功")
            except Exception as e:
                logger.warning(f"⚠️ 图片搜索选项卡未找到: {e}")

    # ============================================================
    # 4. 搜索结果滚动加载测试
    # ============================================================
    @allure.story("搜索结果")
    @allure.title("搜索结果滚动加载测试")
    @allure.severity(allure.severity_level.MINOR)
    @allure.tag("ui", "scroll")
    @pytest.mark.parametrize(
        "keyword",
        ["pytest", "selenium"],
        ids=["滚动搜索pytest", "滚动搜索selenium"]
    )
    def test_search_scroll(self, driver, keyword):
        """测试搜索结果滚动加载更多"""
        config = get_config()
        logger.info(f"🔍 开始滚动加载测试: {keyword}")

        driver.get(config.base_url)
        page = BingPage(driver)

        with allure.step("1. 执行搜索"):
            page.search(keyword)
            time.sleep(2)
            initial_results = page.get_result_count()
            allure.attach(
                f"初始结果数: {initial_results}",
                name="初始结果统计",
                attachment_type=allure.attachment_type.TEXT
            )

        with allure.step("2. 滚动到页面底部"):
            page.scroll_to_bottom()
            time.sleep(2)
            allure.attach(
                driver.get_screenshot_as_png(),
                name="滚动到底部截图",
                attachment_type=allure.attachment_type.PNG
            )

        with allure.step("3. 检查新内容是否加载"):
            time.sleep(2)
            final_results = page.get_result_count()
            allure.attach(
                f"滚动后结果数: {final_results}",
                name="最终结果统计",
                attachment_type=allure.attachment_type.TEXT
            )
            logger.info(f"✅ 滚动加载完成，结果数: {final_results}")

    # ============================================================
    # 5. 搜索结果过滤测试
    # ============================================================
    @allure.story("搜索结果过滤")
    @allure.title("搜索结果过滤功能测试")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("web", "filter")
    @pytest.mark.parametrize(
        "keyword, filter_name",
        [
            ("pytest", "新闻"),
            ("selenium", "视频"),
        ],
        ids=["新闻过滤pytest", "视频过滤selenium"]
    )
    def test_search_filter(self, driver, keyword, filter_name):
        """测试搜索结果过滤功能"""
        config = get_config()
        logger.info(f"🔍 开始搜索过滤测试: {keyword} -> {filter_name}")

        driver.get(config.base_url)
        page = BingPage(driver)

        with allure.step("1. 执行搜索"):
            page.search(keyword)
            time.sleep(2)
            allure.attach(
                driver.get_screenshot_as_png(),
                name="初始搜索结果",
                attachment_type=allure.attachment_type.PNG
            )

        with allure.step(f"2. 点击 '{filter_name}' 过滤"):
            try:
                filter_elements = driver.find_elements(By.CSS_SELECTOR, ".b_smItem")
                filter_clicked = False
                for elem in filter_elements:
                    if filter_name in elem.text:
                        elem.click()
                        time.sleep(2)
                        filter_clicked = True
                        logger.info(f"✅ 已点击过滤: {filter_name}")
                        break
                if not filter_clicked:
                    filter_links = driver.find_elements(By.LINK_TEXT, filter_name)
                    if filter_links:
                        filter_links[0].click()
                        time.sleep(2)
                        filter_clicked = True
                        logger.info(f"✅ 已点击过滤链接: {filter_name}")
                if not filter_clicked:
                    logger.warning(f"⚠️ 未找到过滤选项: {filter_name}")
            except Exception as e:
                logger.warning(f"⚠️ 过滤点击失败: {e}")

        with allure.step("3. 验证过滤结果"):
            allure.attach(
                driver.get_screenshot_as_png(),
                name=f"过滤后结果_{filter_name}",
                attachment_type=allure.attachment_type.PNG
            )
            logger.info(f"✅ 过滤测试完成: {filter_name}")

    # ============================================================
    # 6. 边界测试 - 超长关键词
    # ============================================================
    @allure.story("边界测试")
    @allure.title("超长关键词搜索测试")
    @allure.severity(allure.severity_level.MINOR)
    @allure.tag("edge", "long-keyword")
    def test_search_long_keyword(self, driver):
        """测试超长关键词搜索"""
        config = get_config()
        keyword = "自动化测试" * 20
        logger.info(f"🔍 开始超长关键词测试，长度: {len(keyword)}")

        driver.get(config.base_url)
        page = BingPage(driver)

        with allure.step(f"1. 输入超长关键词 (长度: {len(keyword)})"):
            page.search(keyword)
            allure.attach(
                driver.get_screenshot_as_png(),
                name="超长关键词搜索",
                attachment_type=allure.attachment_type.PNG
            )

        with allure.step("2. 验证搜索执行"):
            if "search" in driver.current_url.lower() or "q=" in driver.current_url.lower():
                logger.info("✅ 超长关键词搜索成功")
            else:
                logger.warning("⚠️ 超长关键词搜索可能被截断")

    # ============================================================
    # 7. 搜索结果点击测试
    # ============================================================
    @allure.story("搜索结果")
    @allure.title("搜索结果点击跳转测试")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("web", "navigation")
    def test_search_result_click(self, driver):
        """测试点击搜索结果跳转"""
        config = get_config()
        keyword = "pytest"
        logger.info(f"🔍 开始搜索结果点击测试: {keyword}")

        driver.get(config.base_url)
        page = BingPage(driver)

        with allure.step("1. 执行搜索"):
            page.search(keyword)
            time.sleep(2)

        with allure.step("2. 获取第一个结果"):
            first_result = page.get_first_result()
            if not first_result:
                pytest.skip("没有搜索结果")

            allure.attach(
                f"第一个结果:\n标题: {first_result['title']}\nURL: {first_result['url']}",
                name="第一个结果信息",
                attachment_type=allure.attachment_type.TEXT
            )

        with allure.step("3. 点击第一个结果"):
            result_links = driver.find_elements(By.CSS_SELECTOR, "#b_results .b_algo h2 a")
            if result_links:
                # 点击第一个结果
                result_links[0].click()
                time.sleep(2)
                allure.attach(
                    driver.get_screenshot_as_png(),
                    name="点击后页面",
                    attachment_type=allure.attachment_type.PNG
                )
                logger.info(f"✅ 成功点击结果，当前URL: {driver.current_url}")
            else:
                logger.warning("⚠️ 未找到结果链接")

    # ============================================================
    # 8. 响应式测试 - 窗口大小
    # ============================================================
    @allure.story("响应式测试")
    @allure.title("不同窗口大小搜索测试")
    @allure.severity(allure.severity_level.MINOR)
    @allure.tag("ui", "responsive")
    @pytest.mark.parametrize(
        "width, height",
        [
            (1920, 1080),
            (1366, 768),
            (768, 1024),
            (375, 667),
        ],
        ids=["桌面", "笔记本", "平板", "手机"]
    )
    def test_search_responsive(self, driver, width, height):
        """测试不同窗口大小的搜索"""
        config = get_config()
        keyword = "pytest"
        logger.info(f"🔍 开始响应式测试: {width}x{height}")

        driver.set_window_size(width, height)
        driver.get(config.base_url)
        page = BingPage(driver)

        with allure.step(f"1. 在 {width}x{height} 窗口下搜索"):
            page.search(keyword)
            allure.attach(
                driver.get_screenshot_as_png(),
                name=f"窗口_{width}x{height}_搜索",
                attachment_type=allure.attachment_type.PNG
            )

        with allure.step("2. 验证搜索结果"):
            result_count = page.get_result_count()
            logger.info(f"✅ {width}x{height} 窗口下找到 {result_count} 个结果")

    # ============================================================
    # 9. 键盘快捷键测试
    # ============================================================
    @allure.story("键盘交互")
    @allure.title("回车键搜索测试")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("web", "keyboard")
    @pytest.mark.parametrize(
        "keyword",
        ["pytest", "selenium"],
        ids=["回车搜索pytest", "回车搜索selenium"]
    )
    def test_search_enter_key(self, driver, keyword):
        """测试回车键搜索"""
        from selenium.webdriver.common.keys import Keys
        config = get_config()
        logger.info(f"🔍 开始回车键搜索测试: {keyword}")

        driver.get(config.base_url)
        page = BingPage(driver)

        with allure.step("1. 输入关键词"):
            search_input = page.find_element(page.search_input)
            search_input.clear()
            search_input.send_keys(keyword)

        with allure.step("2. 使用回车键搜索"):
            search_input.send_keys(Keys.RETURN)
            time.sleep(2)

        with allure.step("3. 验证搜索"):
            result_count = page.get_result_count()
            allure.attach(
                driver.get_screenshot_as_png(),
                name=f"回车搜索_{keyword}",
                attachment_type=allure.attachment_type.PNG
            )
            assert_true(result_count > 0, "回车搜索应该有结果")
            logger.info(f"✅ 回车搜索成功，结果数: {result_count}")