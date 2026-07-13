import allure
import pytest


from pages.baidu_page import BaiduPage

from utils.config import config
from utils.data_reader import load_yaml

from utils.logger import logger



search_cases = load_yaml(
    "data/search_data.yaml"
)



@allure.feature(
    "百度搜索"
)
class TestBaiduSearch:



    @pytest.mark.parametrize(
        "case",
        search_cases,
        ids=lambda x:x["title"]
    )


    @allure.story(
        "搜索功能"
    )


    def test_search(
            self,
            driver,
            case
    ):


        keyword = case["keyword"]



        logger.info(
            f"开始测试:{keyword}"
        )



        with allure.step(
            "打开首页"
        ):


            driver.get(
                config["env"]["url"]
            )



        page = BaiduPage(
            driver
        )



        with allure.step(
            "输入关键词"
        ):


            page.search(
                keyword
            )



        assert (
            driver.title
            ==
            "百度一下，你就知道"
        )



