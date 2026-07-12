import os
import yaml



BASE_DIR = os.path.dirname(
    os.path.dirname(__file__)
)



def load_env(env="test"):


    file_path = os.path.join(

        BASE_DIR,

        "config",

        f"config_{env}.yaml"

    )


    with open(
        file_path,
        encoding="utf-8"
    ) as f:


        return yaml.safe_load(f)
