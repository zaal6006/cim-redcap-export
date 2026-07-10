import logging
from pathlib import Path


def setup_logger(log_level: str) -> logging.Logger:
    """
    Configure application logging.
    """

    Path("logs").mkdir(exist_ok=True)

    logging.basicConfig(
        level=getattr(logging, log_level),
        format="%(asctime)s %(levelname)s %(name)s - %(message)s",
        handlers=[
            logging.FileHandler("logs/cim_export.log"),
            logging.StreamHandler(),
        ],
    )

    return logging.getLogger("cim_export")