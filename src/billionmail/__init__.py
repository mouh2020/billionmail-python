"""billionmail-python: Synchronous Python client for the BillionMail API."""

from .client import BillionMailClient
from .exceptions import (
     ERROR_CODE_MAP,
    BillionMailError,
    BillionMailHTTPError,
    InvalidAPIKeyError,
    InvalidRecipientError,
    IPNotAllowedError,
    SendingFailedError,
    TemplateNotFoundError,
)
from .models import BillionMailRawResponse, BillionMailResponse

__version__ = "0.1.0"

__all__ = [
    "BillionMailClient",
    "BillionMailResponse",
    "BillionMailRawResponse",
    "BillionMailError",
    "BillionMailHTTPError",
    "InvalidAPIKeyError",
    "IPNotAllowedError",
    "InvalidRecipientError",
    "TemplateNotFoundError",
    "SendingFailedError",
    "ERROR_CODE_MAP",
    "__version__",
]
