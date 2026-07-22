"""
Network file export utilities.
"""

from pathlib import Path
from datetime import datetime
import shutil
import time


class NetworkExporter:
    """
    Copies generated CSV files to a network share, archiving the
    previous version (if any) before each overwrite.
    """

    def __init__(self, logger):
        self.logger = logger

    def _archive_existing_file(
        self,
        target_file: Path,
        archive_folder: Path,
    ) -> None:
        """
        If target_file already exists, rename it into archive_folder
        with a timestamp, instead of letting it be silently overwritten.

        Example:
            study_information.csv
            -> archive/study_information_20260717_174230.csv
        """

        if not target_file.exists():
            return

        archive_folder.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archived_name = f"{target_file.stem}_{timestamp}{target_file.suffix}"
        archived_path = archive_folder / archived_name

        try:
            shutil.move(str(target_file), str(archived_path))

            self.logger.info(
                "Archived previous file: '%s' -> '%s'",
                target_file,
                archived_path,
            )

        except OSError as exc:
            # Archiving is a safety measure, not the primary task.
            # If it fails (e.g. permissions), log it clearly but don't
            # block the export - falling through means the new file
            # will simply overwrite the old one, same as before.
            self.logger.warning(
                "Could not archive existing file '%s': %s. "
                "It will be overwritten.",
                target_file,
                exc,
            )

    def cleanup_old_archives(
        self,
        archive_folder: Path,
        days_to_keep: int,
    ) -> None:
        """
        Delete archived files older than `days_to_keep` days.
        """

        if not archive_folder.exists():
            return

        cutoff = time.time() - (days_to_keep * 86400)
        deleted = 0

        for file in archive_folder.glob("*.csv"):

            try:
                if file.stat().st_mtime < cutoff:
                    file.unlink()
                    deleted += 1

            except OSError as exc:
                self.logger.warning(
                    "Could not delete old archive file %s: %s",
                    file,
                    exc,
                )

        if deleted:
            self.logger.info(
                "Cleanup: removed %d archive file(s) older than %d days from %s.",
                deleted,
                days_to_keep,
                archive_folder,
            )
        else:
            self.logger.debug(
                "Cleanup: no archive files older than %d days found in %s.",
                days_to_keep,
                archive_folder,
            )

    def copy_file(
        self,
        source_file: Path,
        destination_file: Path,
        archive: bool = True,
        days_to_keep: int = 30,
        retries: int = 3,
        delay_seconds: int = 5,
    ) -> None:
        """
        Copy one file to the destination, archiving any existing
        file at the destination first.

        Parameters
        ----------
        source_file : Path
            Source file (freshly generated CSV).

        destination_file : Path
            Destination file (published, fixed-name CSV).

        archive : bool
            If True, archive the existing destination file (if any)
            before overwriting, and clean up old archives.

        days_to_keep : int
            Retention window for archived files, in days.

        retries : int
            Number of copy attempts before giving up (handles
            transient network share issues).

        delay_seconds : int
            Delay between retry attempts.
        """

        if not source_file.exists():
            raise FileNotFoundError(
                f"Source file does not exist: {source_file}"
            )

        destination_file.parent.mkdir(parents=True, exist_ok=True)

        if archive:
            archive_folder = destination_file.parent / "archive"
            self._archive_existing_file(destination_file, archive_folder)

        self.logger.info("Copying %s", source_file.name)

        last_error = None

        for attempt in range(1, retries + 1):

            try:
                shutil.copy2(source_file, destination_file)

                self.logger.info(
                    "Copied '%s' -> '%s'",
                    source_file,
                    destination_file,
                )

                if archive:
                    self.cleanup_old_archives(
                        archive_folder=destination_file.parent / "archive",
                        days_to_keep=days_to_keep,
                    )

                return

            except OSError as exc:
                last_error = exc

                self.logger.warning(
                    "Copy attempt %d/%d failed for '%s': %s",
                    attempt,
                    retries,
                    destination_file,
                    exc,
                )

                if attempt < retries:
                    time.sleep(delay_seconds)

        self.logger.error(
            "All %d copy attempts failed for '%s'.",
            retries,
            destination_file,
        )

        raise last_error