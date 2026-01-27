import os
from pydantic_settings import BaseSettings
from enum import Enum


class Env(Enum):
    LOCAL = "local"
    PROD = "prod"


def current_env() -> Env:
    current_env = os.getenv("ENV")
    if (current_env):
        return Env(os.getenv("ENV"))
    else:
        raise Exception(f"App does not have a defined Environment. If running locally, set 'ENV=local' on your .env file. Otherwhise, it means there's no 'prod' ENV variable set on the cloud.")


class Configuration(BaseSettings):
    env: Env = current_env() 
    app_name: str = "Portuguese Politics API"


app_config = Configuration()
