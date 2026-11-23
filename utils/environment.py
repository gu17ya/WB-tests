import os

from dotenv import load_dotenv

load_dotenv()


def get_string_environment(env_variable: str, required: bool = True, default: str = "") -> str:
    value = os.getenv(env_variable, default)
    if required and not value:
        raise ValueError(f"Required environment variable '{env_variable}' is not set")
    return value
