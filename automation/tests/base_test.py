import pytest

import allure



class BaseTest:


    @pytest.fixture(
        autouse=True
    )
    def setup(self):


        with allure.step(
            "开始测试"
        ):

            pass



    def teardown_method(self):


        with allure.step(
            "结束测试"
        ):

            pass