"""Type definitions and response models for the BillionMail API."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional, TypedDict


class BillionMailRawResponse(TypedDict, total=False):
    """TypedDict representing the raw JSON response returned by BillionMail."""

    success: bool
    code: int
    msg: str
    data: Optional[Any]


@dataclass(frozen=True)
class BillionMailResponse:
    """Structured response model returned by BillionMail API calls."""

    success: bool
    code: int
    msg: str
    data: Optional[Any] = None
    raw: Optional[Dict[str, Any]] = None

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> BillionMailResponse:
        """Construct a BillionMailResponse from a raw JSON dictionary."""
        return cls(
            success=bool(payload.get("success", False)),
            code=int(payload.get("code", 0)),
            msg=str(payload.get("msg", "")),
            data=payload.get("data"),
            raw=payload,
        )
