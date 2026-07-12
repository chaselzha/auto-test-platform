import logging
import os
from datetime import datetime


BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)


LOG_DIR = os.path.join(
    BASE_DIR,
    "logs"
)


if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)



log_file = os.path.join(
    LOG_DIR,
    datetime.now().strftime(
        "%Y-%m-%d"
    ) + ".log"
)



def get_logger():

    logger = logging.getLogger(
        "automation"
    )


    logger.setLevel(
        logging.INFO
    )


    if not logger.handlers:


        file_handler = logging.FileHandler(
            log_file,
            encoding="utf-8"
        )


        console_handler = logging.StreamHandler()



        formatter = logging.Formatter(
            "%(asctime)s "
            "[%(levelname)s] "
            "%(message)s"
        )


        file_handler.setFormatter(
            formatter
        )


        console_handler.setFormatter(
            formatter
        )



        logger.addHandler(
            file_handler
        )

        logger.addHandler(
            console_handler
        )


    return logger



logger = get_logger()