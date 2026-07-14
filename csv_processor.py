"""
csv_processor.py

CSV processing utilities for the CIM Dashboard project.
"""

from __future__ import annotations

import csv
from pathlib import Path


class CsvProcessor:
    """
    Reads and processes CSV files produced by REDCap.
    """

    def __init__(self, logger):
        self.logger = logger

    def load_csv(self, input_file: Path) -> list[dict]:
        """
        Load a CSV file into memory.

        Parameters
        ----------
        input_file : Path
            Path to the CSV file.

        Returns
        -------
        list[dict]
            One dictionary per row.
        """

        self.logger.info("Loading CSV file: %s", input_file)

        rows = []

        with input_file.open(
            mode="r",
            encoding="utf-8-sig",
            newline=""
        ) as csv_file:

            reader = csv.DictReader(csv_file)

            for row in reader:
                rows.append(row)

        self.logger.info(
            "Loaded %d records.",
            len(rows),
        )

        return rows