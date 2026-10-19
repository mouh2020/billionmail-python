# billionmail-python

[![PyPI version](https://img.shields.io/pypi/v/billionmail-python.svg)](https://pypi.org/project/billionmail-python/)
[![Python Versions](https://img.shields.io/pypi/pyversions/billionmail-python.svg)](https://pypi.org/project/billionmail-python/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

A clean, synchronous, fully typed Python wrapper for the [BillionMail Email Sending API](https://www.billionmail.com/start/api_mail_guide.html).

## Features

- **Synchronous & Lightweight**: Built on top of `requests` with persistent `requests.Session` connection pooling and context-manager support.
- **Strict Type Hinting**: Full PEP 561 support (`py.typed`) with typed responses (`BillionMailResponse`).
- **Explicit Error Mapping**: Dedicated exception classes for all documented BillionMail API error codes (`1001`–`1005`).

## Installation

```bash
pip install billionmail-python
```

## Quick Start

### 1. Initialize the Client

```python
from billionmail import BillionMailClient

client = BillionMailClient(
    api_key="YOUR_API_KEY",
    base_url="https://mail.your-domain.com",
)
```

You can also use `BillionMailClient` as a context manager to automatically close the underlying HTTP session:

```python
with BillionMailClient(api_key="YOUR_API_KEY", base_url="https://mail.your-domain.com") as client:
    response = client.send(recipient="user@example.com")
    print(response.msg)
```

### 2. Send a Single Email (`/api/batch_mail/api/send`)

Template variables defined in your BillionMail template (e.g., `{{.API.username}}`, `{{.API.order_id}}`) can be passed via `attribs`:

```python
from billionmail import BillionMailClient

client = BillionMailClient(
    api_key="YOUR_API_KEY",
    base_url="https://mail.your-domain.com",
)

response = client.send(
    recipient="recipient@example.com",
    addresser="custom@yourdomain.com",  # Optional: uses default sender if omitted
    attribs={
        "username": "Jesse",
        "order_id": "20240501",
    },
)

print(response.success)  # True
print(response.code)     # 0
print(response.msg)      # "Email sent successfully"
```

### 3. Batch Send Emails (`/api/batch_mail/api/batch_send`)

Send a template email to multiple recipients at once. Note that in batch mode, `attribs` are shared across all recipients:

```python
from billionmail import BillionMailClient

client = BillionMailClient(
    api_key="YOUR_API_KEY",
    base_url="https://mail.your-domain.com",
)

response = client.batch_send(
    recipients=[
        "user1@example.com",
        "user2@example.com",
    ],
    addresser="custom@yourdomain.com",  # Optional
    attribs={
        "promo_code": "VIP2024",
        "username": "Dear User",
    },
)

print(response.success)  # True
print(response.msg)      # "Batch email send request accepted, 2 emails queued"
```

## Error Handling

All API errors inherit from `BillionMailError` and map directly to BillionMail's documented error codes:

| Error Code | Exception Class          | Description                                        |
| ---------- | ------------------------ | -------------------------------------------------- |
| `1001`     | `InvalidAPIKeyError`     | Invalid API key — check if the API key is correct  |
| `1002`     | `IPNotAllowedError`      | IP not allowed — check IP whitelist configuration  |
| `1003`     | `InvalidRecipientError`  | Invalid recipient — check email address format     |
| `1004`     | `TemplateNotFoundError`  | Template does not exist — check the template ID    |
| `1005`     | `SendingFailedError`     | Sending failed — check server error logs           |
| Network/HTTP | `BillionMailHTTPError` | Underlying network failure or non-JSON HTTP error  |

```python
from billionmail import (
    BillionMailClient,
    BillionMailError,
    InvalidAPIKeyError,
    InvalidRecipientError,
    IPNotAllowedError,
    SendingFailedError,
    TemplateNotFoundError,
)

client = BillionMailClient(
    api_key="YOUR_API_KEY",
    base_url="https://mail.your-domain.com",
)

try:
    client.send(recipient="recipient@example.com")
except InvalidAPIKeyError as exc:
    print(f"Authentication failed (code {exc.code}): {exc.message}")
except IPNotAllowedError as exc:
    print(f"Server IP is not whitelisted (code {exc.code}): {exc.message}")
except InvalidRecipientError as exc:
    print(f"Bad recipient address (code {exc.code}): {exc.message}")
except TemplateNotFoundError as exc:
    print(f"Missing template (code {exc.code}): {exc.message}")
except SendingFailedError as exc:
    print(f"Delivery failed (code {exc.code}): {exc.message}")
except BillionMailError as exc:
    print(f"BillionMail error: {exc}")
```

## Advanced Configuration

```python
client = BillionMailClient(
    api_key="YOUR_API_KEY",
    base_url="https://mail.your-domain.com",
    timeout=15.0,       # Default timeout in seconds (default: 30.0)
    verify_ssl=True,    # Set to False for self-signed certificates (equivalent to curl -k)
)
```

## License

MIT