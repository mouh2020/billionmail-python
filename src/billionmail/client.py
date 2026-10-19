"""Synchronous HTTP client for the BillionMail Email Sending API."""

from __future__ import annotations

from types import TracebackType
from typing import Any, Dict, List, Mapping, Optional, Sequence, Type

import requests

from .exceptions import (
    BillionMailError,
    BillionMailHTTPError,
    raise_for_billionmail_error,
)
from .models import BillionMailResponse


class BillionMailClient:
    """Synchronous client for interacting with the BillionMail API.

    Args:
        api_key: The API key generated in the BillionMail dashboard.
        base_url: Base domain or URL of your BillionMail server
            (e.g., ``"https://mail.example.com"`` or ``"mail.example.com"``).
        timeout: Default request timeout in seconds (default: ``30.0``).
        verify_ssl: Whether to verify SSL certificates (default: ``True``).
        session: Optional custom ``requests.Session`` instance.
    """

    SEND_ENDPOINT = "/api/batch_mail/api/send"
    BATCH_SEND_ENDPOINT = "/api/batch_mail/api/batch_send"

    def __init__(
        self,
        api_key: str,
        base_url: str,
        *,
        timeout: float = 30.0,
        verify_ssl: bool = True,
        session: Optional[requests.Session] = None,
    ) -> None:
        if not api_key or not api_key.strip():
            raise ValueError("api_key must be a non-empty string.")
        if not base_url or not base_url.strip():
            raise ValueError("base_url must be a non-empty string.")

        normalized_url = base_url.strip().rstrip("/")
        if not normalized_url.startswith(("http://", "https://")):
            normalized_url = f"https://{normalized_url}"

        self.api_key: str = api_key.strip()
        self.base_url: str = normalized_url
        self.timeout: float = timeout
        self.verify_ssl: bool = verify_ssl

        self._owns_session: bool = session is None
        self._session: requests.Session = session or requests.Session()
        self._session.headers.update(
            {
                "X-API-Key": self.api_key,
                "Content-Type": "application/json",
                "Accept": "application/json",
            }
        )

    def __enter__(self) -> BillionMailClient:
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        self.close()

    def close(self) -> None:
        """Close the underlying HTTP session if owned by this client."""
        if self._owns_session:
            self._session.close()

    def _request(
        self,
        endpoint: str,
        payload: Dict[str, Any],
        *,
        timeout: Optional[float] = None,
    ) -> BillionMailResponse:
        """Send a POST request to the BillionMail API and parse the response."""
        url = f"{self.base_url}{endpoint}"
        effective_timeout = self.timeout if timeout is None else timeout

        try:
            response = self._session.post(
                url,
                json=payload,
                timeout=effective_timeout,
                verify=self.verify_ssl,
            )
        except requests.RequestException as exc:
            raise BillionMailHTTPError(
                message=f"HTTP request to {url} failed: {exc}",
            ) from exc

        try:
            response_data: Dict[str, Any] = response.json()
        except ValueError as exc:
            raise BillionMailHTTPError(
                message=(
                    f"Non-JSON response received from {url} "
                    f"(HTTP {response.status_code}): {response.text[:200]}"
                ),
                status_code=response.status_code,
            ) from exc

        if not isinstance(response_data, dict):
            raise BillionMailError(
                message=f"Unexpected JSON response format from {url}.",
                status_code=response.status_code,
            )

        raise_for_billionmail_error(
            response_data=response_data,
            status_code=response.status_code,
        )

        if not response.ok:
            raise BillionMailHTTPError(
                message=response_data.get("msg")
                or f"HTTP error {response.status_code}",
                code=response_data.get("code"),
                status_code=response.status_code,
                response_data=response_data,
            )

        return BillionMailResponse.from_dict(response_data)

    def send(
        self,
        recipient: str,
        *,
        addresser: Optional[str] = None,
        attribs: Optional[Mapping[str, Any]] = None,
        timeout: Optional[float] = None,
    ) -> BillionMailResponse:
        """Send a single email via ``/api/batch_mail/api/send``.

        Args:
            recipient: Recipient's email address.
            addresser: Optional custom sender email address. If omitted,
                BillionMail uses the default sender configured for the API key.
            attribs: Optional dictionary of custom template variables
                (referenced as ``{{.API.<key>}}`` in the BillionMail template).
            timeout: Optional per-request timeout override in seconds.

        Returns:
            A :class:`BillionMailResponse` object containing the API response.
        """
        if not recipient or not recipient.strip():
            raise ValueError("recipient must be a non-empty email address.")

        payload: Dict[str, Any] = {"recipient": recipient.strip()}
        if addresser is not None:
            payload["addresser"] = addresser.strip()
        if attribs is not None:
            payload["attribs"] = {str(k): str(v) for k, v in attribs.items()}

        return self._request(self.SEND_ENDPOINT, payload, timeout=timeout)

    def batch_send(
        self,
        recipients: Sequence[str],
        *,
        addresser: Optional[str] = None,
        attribs: Optional[Mapping[str, Any]] = None,
        timeout: Optional[float] = None,
    ) -> BillionMailResponse:
        """Send a batch email via ``/api/batch_mail/api/batch_send``.

        Args:
            recipients: List or sequence of recipient email addresses.
            addresser: Optional custom sender email address.
            attribs: Optional dictionary of custom template variables shared
                across all recipients in the batch.
            timeout: Optional per-request timeout override in seconds.

        Returns:
            A :class:`BillionMailResponse` object containing the API response.
        """
        if isinstance(recipients, (str, bytes)) or not recipients:
            raise ValueError(
                "recipients must be a non-empty list or sequence of email addresses."
            )

        cleaned_recipients: List[str] = [
            r.strip() for r in recipients if r and r.strip()
        ]
        if not cleaned_recipients:
            raise ValueError("recipients must contain at least one non-empty email.")

        payload: Dict[str, Any] = {"recipients": cleaned_recipients}
        if addresser is not None:
            payload["addresser"] = addresser.strip()
        if attribs is not None:
            payload["attribs"] = {str(k): str(v) for k, v in attribs.items()}

        return self._request(self.BATCH_SEND_ENDPOINT, payload, timeout=timeout)
