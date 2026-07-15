from config import load_config
from logger import setup_logger
from redcap_client import RedcapClient
from csv_processor import CsvProcessor
from network_export import NetworkExporter
from pathlib import Path
import time


def log_export_summary(
    logger,
    study_count: int,
    patient_visit_count: int,
    study_file: Path,
    patient_file: Path,
    network_share: Path,
) -> None:
    """
    Write a summary of the export process.
    """

    logger.info("=" * 60)
    logger.info("Export Summary")
    logger.info("=" * 60)

    logger.info(
        "Studies exported      : %d",
        study_count,
    )

    logger.info(
        "Patient visits        : %d",
        patient_visit_count,
    )

    logger.info(
        "Study CSV             : %s",
        study_file,
    )

    logger.info(
        "Patient CSV           : %s",
        patient_file,
    )

    logger.info(
        "Network Share         : %s",
        network_share,
    )

    logger.info(
        "Status                : SUCCESS",
    )

    logger.info("=" * 60)


def main():
    start_time = time.perf_counter()
    config = load_config()
    logger = setup_logger(config.log_level)

    logger.info("=" * 60)
    logger.info("CIM REDCap Export started")
    logger.info("=" * 60)

    logger.debug("API URL      : %s", config.redcap_api_url)
    logger.debug("Output Folder: %s", config.output_folder)
    logger.debug("Log Level    : %s", config.log_level)
    logger.debug("Network Share: %s", config.network_share,)    

    client = RedcapClient(config, logger)
    processor = CsvProcessor(logger)
    network_exporter = NetworkExporter(logger)

    raw_export_file = config.output_folder / "raw_export.csv"
    study_output_file = config.output_folder / "study_information.csv"
    patient_output_file = config.output_folder / "patient_visit_dates.csv"

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

    network_exporter.copy_file(
        study_output_file,
        config.network_share / study_output_file.name,
    )

    processor.save_csv(
        patient_visit_rows,
        patient_output_file,
    )

    network_exporter.copy_file(
        patient_output_file,
        config.network_share / patient_output_file.name,
    )

    duration = time.perf_counter() - start_time
    duration: float
    logger.info(
        "Duration              : %.2f seconds",
        duration,
    )
    log_export_summary(
        logger=logger,
        study_count=len(study_rows),
        patient_visit_count=len(patient_visit_rows),
        study_file=study_output_file,
        patient_file=patient_output_file,
        network_share=config.network_share,
    )


if __name__ == "__main__":
    main()