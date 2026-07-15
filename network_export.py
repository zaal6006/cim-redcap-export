"""
Network file export utilities.
"""

from pathlib import Path
import shutil


class NetworkExporter:
    """
    Copies generated CSV files to a network share.
    """

    def __init__(self, logger):
        self.logger = logger

    def copy_file(self,
        source_file: Path,
        destination_file: Path,
    ) -> None:
        """
        Copy one file to the destination.

        Parameters
        ----------
        source_file : Path
            Source file.

        destination_file : Path
            Destination file.
        """
        if not source_file.exists():
            raise FileNotFoundError(
                f"Source file does not exist: {source_file}"
            )        

        self.logger.info(
            "Copying %s",
            source_file.name,
        )

        destination_file.parent.mkdir(
            parents=True,
            exist_ok=True,
        )        

        shutil.copy2(
            source_file,
            destination_file,
        )
        
        self.logger.info(
            "Copied '%s' -> '%s'",
            source_file,
            destination_file,
        )