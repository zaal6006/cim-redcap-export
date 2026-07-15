"""
Application configuration.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

@dataclass(slots=True)
class Config:
    redcap_api_url: str
    redcap_api_token: str
    output_folder: Path
    log_folder: Path
    log_level: str
    network_share: Path

def load_config() -> Config:
    """
    Load configuration from .env
    """
    # REDCap configuration
    api_url = os.getenv("REDCAP_API_URL")
    api_token = os.getenv("REDCAP_API_TOKEN")
    
    # Output configuration
    output_folder = Path(os.getenv("OUTPUT_FOLDER", "output"))
    network_share=Path(os.getenv("NETWORK_SHARE", "output/network_share"))
    
    # Logging configuration
    log_folder = Path(os.getenv("LOG_FOLDER", "logs"))
    log_level = os.getenv("LOG_LEVEL", "INFO")

    if not api_url:
        raise ValueError("REDCAP_API_URL is not defined.")

    if not api_token:
        raise ValueError("REDCAP_API_TOKEN is not defined.")

    output_folder.mkdir(parents=True, exist_ok=True)
    log_folder.mkdir(parents=True, exist_ok=True)
    network_share.mkdir(parents=True, exist_ok=True)

    return Config(
        redcap_api_url=api_url,
        redcap_api_token=api_token,
        output_folder=output_folder,
        network_share=network_share,
        log_folder=log_folder,
        log_level=log_level,
    )