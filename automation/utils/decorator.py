from functools import wraps


from utils.screenshot import take_screenshot

from utils.logger import logger



def screenshot_on_exception(
        func
):


    @wraps(func)
    def wrapper(
            *args,
            **kwargs
    ):


        try:


            return func(
                *args,
                **kwargs
            )


        except Exception as e:


            logger.error(
                f"异常:{e}"
            )


            driver = None



            for arg in args:


                if hasattr(
                    arg,
                    "save_screenshot"
                ):


                    driver = arg


            if driver:


                take_screenshot(
                    driver
                )


            raise e



    return wrapper