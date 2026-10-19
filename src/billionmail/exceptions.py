"""Custom exceptions for the BillionMail API client."""

from __future__ import annotations

from typing import Any, Dict, Optional


class BillionMailError(Exception):
    """Base exception for all BillionMail API errors."""

    def __init__(
        self,
        message: str,
        code: Optional[int] = None,
        status_code: Optional[int] = None,
        response_data: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code
        self.response_data = response_data

    def __str__(self) -> str:
        if self.code is not None:
            return f"[Error {self.code}] {self.message}"
        if self.status_code is not None:
            return f"[HTTP {self.status_code}] {self.message}"
        return self.message


class InvalidAPIKeyError(BillionMailError):
    """Error 1001: Invalid API key. Check if the API key is correct."""


class IPNotAllowedError(BillionMailError):
    """Error 1002: IP not allowed. Check if the IP whitelist is set."""


class InvalidRecipientError(BillionMailError):
    """Error 1003: Invalid recipient. Check the email address format."""


class TemplateNotFoundError(BillionMailError):
    """Error 1004: Template does not exist. Check the template ID."""


class SendingFailedError(BillionMailError):
    """Error 1005: Sending failed. View detailed error logs."""


class BillionMailHTTPError(BillionMailError):
    """Raised when an underlying HTTP or network error occurs."""


ERROR_CODE_MAP: Dict[int, type[BillionMailError]] = {
    1001: InvalidAPIKeyError,
    1002: IPNotAllowedError,
    1003: InvalidRecipientError,
    1004: TemplateNotFoundError,
    1005: SendingFailedError,
}


def raise_for_billionmail_error(
    response_data: Dict[str, Any],
    status_code: Optional[int] = None,
) -> None:
    """Inspect a parsed BillionMail JSON response and raise a mapped exception on error."""
    code = response_data.get("code")
    success = response_data.get("success")

    if success is True and (code == 0 or code is None):
        return

    message = str(response_data.get("msg") or "Unknown BillionMail API error")
    if isinstance(code, int) and code in ERROR_CODE_MAP:
        exc_cls = ERROR_CODE_MAP[code]
        raise exc_cls(
            message=message,
            code=code,
            status_code=status_code,
            response_data=response_data,
        )

    raise BillionMailError(
        message=message,
        code=code if isinstance(code, int) else None,
        status_code=status_code,
        response_data=response_data,
    )
