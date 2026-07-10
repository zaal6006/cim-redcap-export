from dataclasses import dataclass
import os

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Config:
    redcap_api_url: str
    redcap_api_token: str
    output_folder: str
    log_level: str


def load_config() -> Config:
    """
    Load configuration from environment variables.
    Raises ValueError if required variables are missing.
    """

    api_url = os.getenv("REDCAP_API_URL")
    api_token = os.getenv("REDCAP_API_TOKEN")

    if not api_url:
        raise ValueError("Environment variable REDCAP_API_URL is not defined.")

    if not api_token:
        raise ValueError("Environment variable REDCAP_API_TOKEN is not defined.")

    return Config(
        redcap_api_url=api_url,
        redcap_api_token=api_token,
        output_folder=os.getenv("OUTPUT_FOLDER", "output"),
        log_level=os.getenv("LOG_LEVEL", "INFO").upper(),
    )