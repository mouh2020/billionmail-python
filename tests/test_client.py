"""Unit tests for BillionMailClient and custom exceptions."""

from __future__ import annotations

from typing import Any, Dict
from unittest.mock import MagicMock

import pytest
import requests

from billionmail import (
    BillionMailClient,
    BillionMailError,
    BillionMailHTTPError,
    InvalidAPIKeyError,
    InvalidRecipientError,
    IPNotAllowedError,
    SendingFailedError,
    TemplateNotFoundError,
)


def _mock_response(json_data: Dict[str, Any], status_code: int = 200) -> MagicMock:
    resp = MagicMock(spec=requests.Response)
    resp.status_code = status_code
    resp.ok = 200 <= status_code < 300
    resp.json.return_value = json_data
    resp.text = str(json_data)
    return resp


def test_send_single_email_success() -> None:
    session = MagicMock(spec=requests.Session)
    session.headers = {}
    session.post.return_value = _mock_response(
        {
            "success": True,
            "code": 0,
            "msg": "Email sent successfully",
            "data": None,
        }
    )

    client = BillionMailClient(
        api_key="test-key",
        base_url="mail.example.com/",
        session=session,
    )
    result = client.send(
        recipient="recipient@example.com",
        addresser="custom@example.com",
        attribs={"username": "Jesse", "order_id": 20240501},
    )

    assert result.success is True
    assert result.code == 0
    assert result.msg == "Email sent successfully"
    session.post.assert_called_once_with(
        "https://mail.example.com/api/batch_mail/api/send",
        json={
            "recipient": "recipient@example.com",
            "addresser": "custom@example.com",
            "attribs": {"username": "Jesse", "order_id": "20240501"},
        },
        timeout=30.0,
        verify=True,
    )


def test_batch_send_email_success() -> None:
    session = MagicMock(spec=requests.Session)
    session.headers = {}
    session.post.return_value = _mock_response(
        {
            "success": True,
            "code": 0,
            "msg": "Batch email send request accepted, 2 emails queued",
            "data": None,
        }
    )

    client = BillionMailClient(
        api_key="test-key",
        base_url="https://mail.example.com",
        session=session,
    )
    result = client.batch_send(
        recipients=["user1@example.com", "user2@example.com"],
        addresser="custom@example.com",
        attribs={"promo_code": "VIP2024", "username": "Dear User"},
    )

    assert result.success is True
    assert result.code == 0
    assert "2 emails queued" in result.msg
    session.post.assert_called_once_with(
        "https://mail.example.com/api/batch_mail/api/batch_send",
        json={
            "recipients": ["user1@example.com", "user2@example.com"],
            "addresser": "custom@example.com",
            "attribs": {"promo_code": "VIP2024", "username": "Dear User"},
        },
        timeout=30.0,
        verify=True,
    )


@pytest.mark.parametrize(
    ("code", "exc_cls"),
    [
        (1001, InvalidAPIKeyError),
        (1002, IPNotAllowedError),
        (1003, InvalidRecipientError),
        (1004, TemplateNotFoundError),
        (1005, SendingFailedError),
        (9999, BillionMailError),
    ],
)
def test_error_code_mapping(code: int, exc_cls: type[BillionMailError]) -> None:
    session = MagicMock(spec=requests.Session)
    session.headers = {}
    session.post.return_value = _mock_response(
        {
            "success": False,
            "code": code,
            "msg": f"Simulated error {code}",
            "data": None,
        }
    )

    client = BillionMailClient(
        api_key="test-key",
        base_url="https://mail.example.com",
        session=session,
    )

    with pytest.raises(exc_cls) as exc_info:
        client.send(recipient="recipient@example.com")

    assert exc_info.value.code == code
    assert f"Simulated error {code}" in str(exc_info.value)


def test_network_exception_raises_http_error() -> None:
    session = MagicMock(spec=requests.Session)
    session.headers = {}
    session.post.side_effect = requests.ConnectionError("Connection refused")

    client = BillionMailClient(
        api_key="test-key",
        base_url="https://mail.example.com",
        session=session,
    )

    with pytest.raises(BillionMailHTTPError):
        client.send(recipient="recipient@example.com")
