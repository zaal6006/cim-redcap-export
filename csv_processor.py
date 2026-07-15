"""
csv_processor.py

CSV processing utilities for the CIM Dashboard project.
"""

from __future__ import annotations

import csv
from pathlib import Path
import re

class CsvProcessor:
    """
    Reads and processes CSV files produced by REDCap.
    """
    VISIT_COLUMN_PATTERNS = (
        r"^screening_date_p\d+$",
        r"^treatment_date_p\d+$",
        r"^fu_date_p\d+$",
    )

    VISIT_TYPE_PATTERNS = {
        "screening": r"^screening_date_p(\d+)$",
        "treatment": r"^treatment_date_p(\d+)$",
        "follow_up": r"^fu_date_p(\d+)$",
    }

    def __init__(self, logger):
        self.logger = logger

    # ---------------------------------------------------------
    # Helper methods
    # ---------------------------------------------------------    

    @staticmethod
    def _parse_visit_column(column_name: str) -> tuple[str, int] | None:
        """
        Parse a patient visit column name.

        Parameters
        ----------
        column_name : str
            Example: screening_date_p12

        Returns
        -------
        tuple[str, int] | None

            ("screening", 12)

            or

            None if the column is not a visit column.
        """

        for visit_type, pattern in CsvProcessor.VISIT_TYPE_PATTERNS.items():

            match = re.match(pattern, column_name)

            if match:

                patient_number = int(match.group(1))

                return visit_type, patient_number

        return None     
         

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
    
    def save_csv(
        self,
        rows: list[dict],
        output_file: str,
    ) -> None:
        """
        Save a list of dictionaries to a CSV file.

        Parameters
        ----------
        rows : list[dict]
            Rows to save.

        output_file : str
            Output CSV filename.
        """

        if not rows:
            self.logger.warning(
                "No rows to save: %s",
                output_file,
            )
            return

        output_path = Path(output_file)

        self.logger.info(
            "Saving CSV file: %s",
            output_path,
        )

        with output_path.open(
            "w",
            newline="",
            encoding="utf-8-sig",
        ) as csvfile:

            writer = csv.DictWriter(
                csvfile,
                fieldnames=rows[0].keys(),
            )

            writer.writeheader()
            writer.writerows(rows)

        self.logger.info(
            "Saved %d rows.",
            len(rows),
        )    
    
    def identify_study_columns(self, headers: list[str]) -> list[str]:
        """
        Return all columns that belong to study-level information.
        """

        study_columns = []

        for header in headers:

            is_visit_column = any(
                re.match(pattern, header)
                for pattern in self.VISIT_COLUMN_PATTERNS
            )

            if not is_visit_column:
                study_columns.append(header)

        self.logger.info(
            "Detected %d study columns.",
            len(study_columns),
        )

        return study_columns
    
    def create_study_rows(
        self,
        rows: list[dict],
        study_columns: list[str],
    ) -> list[dict]:
        """
        Create study-only rows by removing patient visit columns.

        Parameters
        ----------
        rows : list[dict]
            Rows loaded from the REDCap export.

        study_columns : list[str]
            Column names that belong to study-level information.

        Returns
        -------
        list[dict]
            Study-only rows.
        """

        self.logger.info("Creating study rows...")

        study_rows = []

        for row in rows:

            study_row = {}

            for column in study_columns:
                study_row[column] = row[column]

            study_rows.append(study_row)

        self.logger.info(
            "Created %d study rows.",
            len(study_rows),
        )

        return study_rows
    
    
    def create_patient_visit_rows(
        self,
        rows: list[dict],
    ) -> list[dict]:
        """
        Create patient visit rows from the REDCap export.

        Parameters
        ----------
        rows : list[dict]
            Rows loaded from the REDCap CSV export.

        Returns
        -------
        list[dict]
            Patient visit rows.
        """

        self.logger.info("Creating patient visit rows...")

        patient_visit_rows = []

        # Loop through every study
        for row in rows:

            # Loop through every column in the study
            for column_name, value in row.items():

                parsed = self._parse_visit_column(column_name)

                if parsed is None:
                    continue

                visit_type, patient_number = parsed
                
                if not value:
                    continue    # "If there is no visit date, skip this column."

                study_name = row.get("study_name")

                if not study_name:
                    self.logger.warning(
                        "Study row missing study_name."
                    )
                    continue

                patient_visit_row = {
                    "study_name": study_name, #row["study_name"]
                    "patient_number": patient_number,
                    "visit_type": visit_type,
                    "visit_date": value,
                }

                patient_visit_rows.append(patient_visit_row)

        self.logger.info(
            "Created %d patient visit rows.",
            len(patient_visit_rows),
        )

        return patient_visit_rows