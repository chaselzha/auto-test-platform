import pytest



if __name__ == "__main__":


    pytest.main(
        [

            "-s",

            "-v",

            "tests",

            "--alluredir",

            "reports/allure-results"

        ]
    )