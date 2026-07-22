import logging
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path


def setup_logger(log_level: str) -> logging.Logger:
    """
    Configure application logging with daily rotation.

    Creates one log file per day (cim_export.log for today,
    cim_export.log.YYYY-MM-DD for previous days).
    Automatically deletes log files older than 30 days.
    """

    Path("logs").mkdir(exist_ok=True)

    file_handler = TimedRotatingFileHandler(
        filename="logs/cim_export.log",
        when="midnight",     # rotate at midnight, local server time
        interval=1,          # every 1 day
        backupCount=30,      # keep 30 days, delete anything older automatically
        encoding="utf-8",
    )

    stream_handler = logging.StreamHandler()

    formatter = logging.Formatter(
        "%(asctime)s %(levelname)s %(name)s - %(message)s"
    )
    file_handler.setFormatter(formatter)
    stream_handler.setFormatter(formatter)

    logger = logging.getLogger("cim_export")
    logger.setLevel(getattr(logging, log_level))

    # Avoid duplicate handlers if setup_logger() is ever called more than once
    # in the same process (e.g. during testing).
    logger.handlers.clear()
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

    return logger