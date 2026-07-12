import allure


def attach_screenshot(driver):


    allure.attach(
        driver.get_screenshot_as_png(),

        name="失败截图",

        attachment_type=
        allure.attachment_type.PNG

    )



def attach_text(
        content,
        name="日志"
):


    allure.attach(

        content,

        name=name,

        attachment_type=
        allure.attachment_type.TEXT

    )