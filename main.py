from config import load_config
from logger import setup_logger
from redcap_client import RedcapClient


def main():

    config = load_config()

    logger = setup_logger(config.log_level)

    logger.info("CIM REDCap Export started")

    client = RedcapClient(config, logger)

    client.test_connection()

    logger.info("Initialization completed successfully.")


if __name__ == "__main__":
    main()