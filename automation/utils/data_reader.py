import os
import yaml

from utils.logger import logger



def load_yaml(path):


    base_dir = os.path.dirname(
        os.path.dirname(__file__)
    )


    file_path = os.path.join(
        base_dir,
        path
    )


    logger.info(
        f"读取测试数据:{file_path}"
    )


    with open(
        file_path,
        "r",
        encoding="utf-8"
    ) as f:


        return yaml.safe_load(f)