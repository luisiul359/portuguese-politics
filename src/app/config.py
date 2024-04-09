import os
from pydantic_settings import BaseSettings


def current_env() -> str:
    current_env = os.getenv("ENV") 
    if (current_env):
        return current_env
    else:
        raise Exception(f"App does not have a defined Environment. If running locally, set 'ENV=local' on your .env file. Otherwhise, it means there's no 'production' ENV variable set on the cloud.")


class Configuration(BaseSettings):
    app_name: str = "Portuguese Politics API"
    env: str = current_env() 


config = Configuration()
