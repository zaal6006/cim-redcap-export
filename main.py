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

    # logger.info("First study: %s", rows[0]["study_name"])    

    headers = rows[0].keys()

    study_columns = processor.identify_study_columns(list(headers))

    logger.info("Study columns detected: %d", len(study_columns))
    # logger.info("First five study columns: %s", study_columns[:5])

    study_rows = processor.create_study_rows(rows, study_columns)

    logger.info("Study rows created: %d", len(study_rows))
    logger.info("Columns in first study row: %d", len(study_rows[0]))
    # logger.info("First study: %s", study_rows[0]["study_name"])    

    patient_visit_rows = processor.create_patient_visit_rows(rows)

    logger.info(
        "Patient visit rows created: %d",
        len(patient_visit_rows),
    )

    if patient_visit_rows:
        logger.info(
            "First patient visit row: %s",
            patient_visit_rows[0],
        )

    processor.save_csv(
        study_rows,
        "output/study_information.csv",
    )        

    processor.save_csv(
        patient_visit_rows,
        "output/patient_visit_dates.csv",
    )

    logger.info("Initialization completed successfully.")


if __name__ == "__main__":
    main()