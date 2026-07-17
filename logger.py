import logging
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path


def setup_logger(log_level: str) -> logging.Logger:
    """
    Configure application logging with daily rotation.
    Keeps 30 days of history, then deletes older logs automatically.
    """
    Path("logs").mkdir(exist_ok=True)

    formatter = logging.Formatter(
        "%(asctime)s %(levelname)s %(name)s - %(message)s"
    )

    file_handler = TimedRotatingFileHandler(
        filename="logs/cim_export.log",
        when="midnight",
        interval=1,
        backupCount=30,      # keep 30 days, delete older automatically
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    logger = logging.getLogger("cim_export")
    logger.setLevel(getattr(logging, log_level))
    logger.handlers.clear()   # avoid duplicate handlers if setup_logger is called twice
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

    return logger