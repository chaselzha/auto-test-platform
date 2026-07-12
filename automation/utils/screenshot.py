import os

import allure

from datetime import datetime

from utils.logger import logger



def take_screenshot(
        driver,
        name="error"
):


    path = os.path.join(

        os.path.dirname(
            os.path.dirname(__file__)
        ),

        "screenshots"

    )


    os.makedirs(
        path,
        exist_ok=True
    )



    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )


    filename = (
        f"{timestamp}_{name}.png"
    )


    filepath = os.path.join(
        path,
        filename
    )


    driver.save_screenshot(
        filepath
    )



    logger.error(
        f"失败截图:{filepath}"
    )



    # 添加到Allure

    with open(
        filepath,
        "rb"
    ) as f:


        allure.attach(

            f.read(),

            name=name,

            attachment_type=
            allure.attachment_type.PNG

        )


    return filepath