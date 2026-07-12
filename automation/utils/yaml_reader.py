import os
import yaml

from utils.logger import logger



def read_yaml(file_name):


    file_path = os.path.join(

        os.path.dirname(
            os.path.dirname(__file__)
        ),

        "data",

        file_name
    )


    logger.info(
        f"读取测试数据:{file_path}"
    )


    if not os.path.exists(file_path):

        raise FileNotFoundError(
            f"文件不存在:{file_path}"
        )


    with open(

        file_path,

        "r",

        encoding="utf-8"

    ) as file:


        data = yaml.safe_load(file)



    if not data:

        raise ValueError(
            "YAML数据为空"
        )


    return data