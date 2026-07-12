import yaml
import os


BASE_DIR = os.path.dirname(
    os.path.dirname(__file__)
)


CONFIG_DIR = os.path.join(
    BASE_DIR,
    "config"
)



def load_env_config(env):


    file = os.path.join(
        CONFIG_DIR,
        f"config_{env}.yaml"
    )


    with open(
        file,
        encoding="utf-8"
    ) as f:


        return yaml.safe_load(f)