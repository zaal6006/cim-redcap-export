"""
redcap_client.py

Simple REDCap API client for the CIM Dashboard project.
"""

from __future__ import annotations

import requests

#
# Use the Windows certificate store when available.
#
try:
    import truststore
    truststore.inject_into_ssl()
except ImportError:
    pass


class RedcapClient:
    """Simple REDCap API client."""

    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        self.session = requests.Session()

    def _post(self, payload: dict) -> requests.Response:
        """
        Send a POST request to the REDCap API.

        Returns the Response object even if REDCap returns
        an HTTP error. This allows us to inspect the response body.
        """

        try:

            self.logger.info("POST %s", self.config.redcap_api_url)
            self.logger.debug("Payload: %s", payload)

            response = self.session.post(
                self.config.redcap_api_url,
                data=payload,
                timeout=30,
            )

            self.logger.info("HTTP Status: %s", response.status_code)

            return response

        except requests.exceptions.SSLError as exc:
            self.logger.exception("SSL certificate verification failed.")
            raise

        except requests.exceptions.Timeout as exc:
            self.logger.exception("Connection timed out.")
            raise

        except requests.exceptions.ConnectionError as exc:
            self.logger.exception("Unable to connect to REDCap.")
            raise

    def test_connection(self):
        """
        Attempt a small REDCap record export.

        We intentionally request records because this is the
        operation the production job will perform.
        """

        self.logger.info("Testing REDCap API...")

        payload = {
            "token": self.config.redcap_api_token,
            "content": "record",
            "action": "export",
            "format": "csv",
            "type": "flat",
            "returnFormat": "json",
        }

        response = self._post(payload)

        print()
        print("=" * 80)
        print("HTTP STATUS")
        print("=" * 80)
        print(response.status_code)

        print()
        print("=" * 80)
        print("HEADERS")
        print("=" * 80)
        for key, value in response.headers.items():
            print(f"{key}: {value}")

        print()
        print("=" * 80)
        print("BODY")
        print("=" * 80)

        print(response.text[:2000])

        print("=" * 80)

        if response.status_code == 200:
            self.logger.info("Connection test completed successfully.")
        else:
            self.logger.warning(
                "Server returned HTTP %s",
                response.status_code,
            )

        return response