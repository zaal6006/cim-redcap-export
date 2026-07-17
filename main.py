from config import load_config
from logger import setup_logger
from redcap_client import RedcapClient
from csv_processor import CsvProcessor
from network_export import NetworkExporter
from pathlib import Path
from datetime import datetime
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


def cleanup_old_archives(
    archive_folder: Path,
    days_to_keep: int,
    logger,
) -> None:
    """
    Delete archived raw export files older than `days_to_keep` days.

    Parameters
    ----------
    archive_folder : Path
        Folder containing the timestamped raw_export_*.csv files.

    days_to_keep : int
        Number of days of archives to retain.

    logger : Logger
    """

    if not archive_folder.exists():
        return

    cutoff = time.time() - (days_to_keep * 86400)
    deleted = 0

    for file in archive_folder.glob("raw_export_*.csv"):

        if file.stat().st_mtime < cutoff:

            try:
                file.unlink()
                deleted += 1

            except OSError as exc:
                logger.warning(
                    "Could not delete old archive file %s: %s",
                    file,
                    exc,
                )

    if deleted:
        logger.info(
            "Cleanup: removed %d archive file(s) older than %d days.",
            deleted,
            days_to_keep,
        )
    else:
        logger.debug(
            "Cleanup: no archive files older than %d days found.",
            days_to_keep,
        )


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

    # ------------------------------------------------------------
    # File paths
    # ------------------------------------------------------------
    # Raw exports are archived with a timestamp so we keep a history
    # of every pull for auditing/debugging purposes.
    #
    # Study/patient CSVs keep FIXED names, because the network share
    # consumers (e.g. Power BI) expect a stable filename to read from.
    # ------------------------------------------------------------

    run_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    archive_folder = config.output_folder / "archive"
    archive_folder.mkdir(parents=True, exist_ok=True)

    raw_export_file = archive_folder / f"raw_export_{run_timestamp}.csv"
    study_output_file = config.output_folder / "study_information.csv"
    patient_output_file = config.output_folder / "patient_visit_dates.csv"

    logger.debug("Raw export file (archived): %s", raw_export_file)

    client.export_records(raw_export_file)

    rows = processor.load_csv(raw_export_file)

    if not rows:
        logger.error("REDCap export returned zero records. Aborting.")
        raise SystemExit(1)

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

    # Keep 90 days of raw export archives, delete anything older.
    cleanup_old_archives(
        archive_folder=archive_folder,
        days_to_keep=90,
        logger=logger,
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
    try:
        main()
    except SystemExit:
        raise
    except Exception:
        import logging
        from pathlib import Path

        # Fallback: if setup_logger() never ran (e.g. config.py failed),
        # the "cim_export" logger has no handlers yet. Attach an emergency
        # one so the failure is never silently lost.
        logger = logging.getLogger("cim_export")
        if not logger.handlers:
            Path("logs").mkdir(exist_ok=True)
            logging.basicConfig(
                level=logging.ERROR,
                format="%(asctime)s %(levelname)s %(name)s - %(message)s",
                handlers=[
                    logging.FileHandler("logs/cim_export_fatal.log"),
                    logging.StreamHandler(),
                ],
            )

        logger.exception("Export FAILED with an unexpected error.")
        raise SystemExit(1)