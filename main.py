from config import load_config
from logger import setup_logger
from redcap_client import RedcapClient
from csv_processor import CsvProcessor


def main():
    config = load_config()
    logger = setup_logger(config.log_level)

    logger.info("=" * 60)
    logger.info("CIM REDCap Export started")
    logger.info("=" * 60)

    logger.info("API URL      : %s", config.redcap_api_url)
    logger.info("Output Folder: %s", config.output_folder)
    logger.info("Log Level    : %s", config.log_level)

    client = RedcapClient(config, logger)
    processor = CsvProcessor(logger)

    raw_export_file = config.output_folder / "raw_export.csv"
    study_output_file = config.output_folder / "study_information.csv"
    patient_output_file = (
        config.output_folder / "patient_visit_dates.csv"
    )

    client.export_records(raw_export_file)

    rows = processor.load_csv(raw_export_file)

    headers = list(rows[0].keys())

    study_columns = processor.identify_study_columns(headers)

    study_rows = processor.create_study_rows(
        rows,
        study_columns,
    )

    patient_visit_rows = processor.create_patient_visit_rows(
        rows,
    )

    processor.save_csv(
        study_rows,
        study_output_file,
    )

    processor.save_csv(
        patient_visit_rows,
        patient_output_file,
    )

    logger.info("=" * 60)
    logger.info("CIM REDCap Export completed successfully.")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()