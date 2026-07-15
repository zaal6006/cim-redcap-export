"""
redcap_client.py

REDCap API client for the CIM Dashboard Export project.
"""

from __future__ import annotations

import csv
import io
from pathlib import Path

import requests

#
# Use Windows Certificate Store if available.
#
try:
    import truststore

    truststore.inject_into_ssl()
except ImportError:
    pass


class RedcapApiError(Exception):
    """Raised when the REDCap API returns an unexpected response."""


class RedcapClient:
    """
    REDCap API client.

    Responsible only for communication with REDCap.
    """

    def __init__(self, config, logger):

        self.config = config
        self.logger = logger

        self.session = requests.Session()

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _post(self, payload: dict) -> requests.Response:
        """
        Execute a POST request against the REDCap API.
        """

        self.logger.debug("POST %s",self.config.redcap_api_url,)
        self.logger.debug("Payload: %s", payload)

        try:

            response = self.session.post(
                self.config.redcap_api_url,
                data=payload,
                timeout=60,
            )

        except requests.exceptions.SSLError as exc:
            raise RedcapApiError(
                "SSL certificate verification failed."
            ) from exc

        except requests.exceptions.Timeout as exc:
            raise RedcapApiError(
                "Connection to REDCap timed out."
            ) from exc

        except requests.exceptions.ConnectionError as exc:
            raise RedcapApiError(
                "Unable to connect to REDCap."
            ) from exc

        except requests.exceptions.RequestException as exc:
            raise RedcapApiError(str(exc)) from exc

        self.logger.debug("HTTP Status: %s", response.status_code)

        return response

    def _validate_http_response(self, response: requests.Response) -> None:
        """
        Validate HTTP response.
        """

        if response.status_code != 200:

            self.logger.error(
                "HTTP %s returned by REDCap.",
                response.status_code,
            )

            self.logger.error(response.text)

            raise RedcapApiError(
                f"HTTP {response.status_code}"
            )

    def _validate_csv(self, csv_text: str) -> list[str]:
        """
        Validate returned CSV.

        Returns
        -------
        list[str]
            Header row.
        """

        try:

            reader = csv.reader(io.StringIO(csv_text))

            headers = next(reader)

        except StopIteration:

            raise RedcapApiError(
                "Returned CSV is empty."
            )

        except Exception as exc:

            raise RedcapApiError(
                f"Unable to parse CSV ({exc})"
            ) from exc

        #
        # Sanity check
        #

        if len(headers) < 2:

            raise RedcapApiError(
                "CSV contains too few columns."
            )

        #
        # Future validation.
        # Add required fields here.
        #
        
        """
        required_columns = [
            "record_id",
        ]

        missing = [
            column
            for column in required_columns
            if column not in headers
        ]

        if missing:

            raise RedcapApiError(
                "Missing required columns: "
                + ", ".join(missing)
            )
        """

        self.logger.debug("CSV validation successful (%d columns).",len(headers),)
        self.logger.debug("CSV Headers: %s",headers,)

        return headers

    def _save_csv(
        self,
        csv_text: str,
        output_file: Path,
    ) -> None:
        """
        Save CSV to disk.
        """

        output_file.write_text(
            csv_text,
            encoding="utf-8",
            newline="",
        )

        self.logger.info(
            "CSV saved to %s",
            output_file,
        )

    # ------------------------------------------------------------------
    # Public methods
    # ------------------------------------------------------------------

    def test_project_access(self) -> bool:
        """
        Verify that the REDCap API and project are accessible.
        """

        self.logger.info(
            "Testing REDCap project access..."
        )

        payload = {
            "token": self.config.redcap_api_token,
            "content": "project",
            "action": "export",
            "format": "csv",
            "type": "flat",
            "returnFormat": "json",
        }

        response = self._post(payload)

        self._validate_http_response(response)

        self.logger.info(
            "Successfully connected to REDCap project."
        )

        return True

    def export_records(
        self,
        output_file: Path,
    ) -> Path:
        """
        Export REDCap records to CSV.
        """

        self.logger.info(
            "Exporting REDCap records..."
        )

        payload = {
            "token": self.config.redcap_api_token,
            "content": "record",
            "action": "export",
            "format": "csv",
            "type": "flat",
            "returnFormat": "json",
        }

        response = self._post(payload)

        self._validate_http_response(response)

        headers = self._validate_csv(response.text)

        self.logger.debug("Detected %d columns.",len(headers),)

        self.logger.debug("First column: %s",headers[0],)

        self._save_csv(
            response.text,
            output_file,
        )

        self.logger.info(
            "REDCap export completed successfully."
        )

        return output_file