"""
main.py

Entry point for the CIM REDCap Export application.
"""

from config import load_config
from logger import setup_logger
from redcap_client import RedcapClient


def main():
    # Load application configuration
    config = load_config()

    # Initialize logging
    logger = setup_logger(config.log_level)

    logger.info("=" * 60)
    logger.info("CIM REDCap Export started")
    logger.info("=" * 60)

    logger.info("API URL      : %s", config.redcap_api_url)
    logger.info("Output Folder: %s", config.output_folder)
    logger.info("Log Level    : %s", config.log_level)

    client = RedcapClient(config, logger)

    # Verify that the API and project are accessible.
    # client.test_project_access()

    output_file = config.output_folder / "raw_export.csv"

    client.export_records(output_file)

    from csv_processor import CsvProcessor

    processor = CsvProcessor(logger)

    rows = processor.load_csv(output_file)

    logger.info("First study: %s", rows[0]["study_name"])    

    logger.info("Initialization completed successfully.")


if __name__ == "__main__":
    main()