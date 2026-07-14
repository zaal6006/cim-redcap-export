"""
redcap_client.py

REDCap API client for the CIM Dashboard Export project.
"""

from __future__ import annotations
from pathlib import Path

import requests

#
# Use Windows certificate store if available.
#
try:
    import truststore

    truststore.inject_into_ssl()
except ImportError:
    pass


class RedcapApiError(Exception):
    """Raised when the REDCap API returns an unexpected response."""


class RedcapClient:
    """Simple REDCap API client."""

    def __init__(self, config, logger):
        self.config = config
        self.logger = logger

        self.session = requests.Session()

    def _post(self, payload: dict) -> requests.Response:
        """
        Execute a POST request against the REDCap API.
        """

        self.logger.info("POST %s", self.config.redcap_api_url)
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

        self.logger.info("HTTP Status: %s", response.status_code)

        return response

    def test_project_access(self):
        """
        Verify that the API endpoint and project are accessible.
        """

        self.logger.info("Testing REDCap project access...")

        payload = {
            "token": self.config.redcap_api_token,
            "content": "project",
            "action": "export",
            "format": "csv",
            "type": "flat",
            "returnFormat": "json",
        }

        response = self._post(payload)

        #
        # Log first 500 characters for troubleshooting.
        #
        preview = response.text[:500].replace("\n", " ")

        self.logger.debug("Response Preview: %s", preview)

        if response.status_code != 200:
            raise RedcapApiError(
                f"REDCap returned HTTP {response.status_code}.\n"
                f"Response:\n{response.text}"
            )

        self.logger.info("Successfully connected to REDCap project.")

        return True
    
    
    def export_records(self, output_file: Path) -> Path:
        """
        Export REDCap records to CSV.
        """

        self.logger.info("Exporting REDCap records...")

        payload = {
            "token": self.config.redcap_api_token,
            "content": "record",
            "action": "export",
            "format": "csv",
            "type": "flat",
            "returnFormat": "json",
        }

        response = self._post(payload)

        if response.status_code != 200:
            raise RedcapApiError(
                f"HTTP {response.status_code}\n{response.text}"
            )

        #
        # Very simple sanity check.
        #
        if "," not in response.text:
            raise RedcapApiError(
                "Response does not appear to be CSV."
            )

        output_file.write_text(
            response.text,
            encoding="utf-8",
            newline=""
        )

        self.logger.info(
            "CSV exported successfully."
        )

        self.logger.info(
            "Saved to %s",
            output_file
        )

        return output_file    