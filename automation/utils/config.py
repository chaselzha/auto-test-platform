import yaml
import os


BASE_DIR = os.path.dirname(
    os.path.dirname(__file__)
)


def load_config(env):

    file = os.path.join(
        BASE_DIR,
        "config",
        f"config_{env}.yaml"
    )


    with open(
        file,
        "r",
        encoding="utf-8"
    ) as f:

        return yaml.safe_load(f)


config = load_config("test")