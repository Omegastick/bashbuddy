from pathlib import Path

import tomllib
from platformdirs import user_config_dir
from pydantic import BaseSettings


class Config(BaseSettings):
    model: str = "gpt-3.5-turbo-0613"

    class Config:
        env_prefix = "bashbuddy_"


def load_config() -> Config:
    config_dir = user_config_dir("bashbuddy")
    config_path = Path(config_dir) / "config.toml"

    if config_path.exists():
        with open(config_path, "rb") as f:
            return Config(**tomllib.load(f))

    return Config()
