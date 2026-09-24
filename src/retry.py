from __future__ import annotations

import time
from typing import Callable, TypeVar

from slack_sdk.errors import SlackApiError

T = TypeVar("T")


def call_with_retry(func: Callable[[], T], max_retries: int = 5, base_sleep: float = 1.0) -> T:
    """Call Slack API with retry for rate limits and transient failures."""
    attempt = 0
    while True:
        try:
            return func()
        except SlackApiError as error:
            status = getattr(error.response, "status_code", None)
            error_code = error.response.get("error") if error.response else "unknown"

            if status == 429:
                retry_after = error.response.headers.get("Retry-After", "1")
                sleep_seconds = max(float(retry_after), 1.0)
                time.sleep(sleep_seconds)
                attempt += 1
                if attempt > max_retries:
                    raise
                continue

            if error_code in {"internal_error", "fatal_error", "request_timeout"}:
                attempt += 1
                if attempt > max_retries:
                    raise
                time.sleep(base_sleep * (2 ** (attempt - 1)))
                continue

            raise
