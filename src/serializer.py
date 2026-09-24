from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


def extract_attachments(message: dict[str, Any]) -> list[dict[str, Any]]:
    files = message.get("files") or []
    attachments: list[dict[str, Any]] = []

    for item in files:
        attachments.append(
            {
                "id": item.get("id"),
                "name": item.get("name"),
                "mimetype": item.get("mimetype"),
                "filetype": item.get("filetype"),
                "size": item.get("size"),
                "url_private": item.get("url_private"),
                "permalink": item.get("permalink"),
            }
        )

    return attachments


def normalize_message(message: dict[str, Any]) -> dict[str, Any]:
    return {
        "ts": message.get("ts"),
        "user": message.get("user"),
        "text": message.get("text"),
        "subtype": message.get("subtype"),
        "thread_ts": message.get("thread_ts"),
        "reply_count": message.get("reply_count", 0),
        "attachments": extract_attachments(message),
    }


def build_export_payload(
    channel_id: str,
    channel_name: str,
    messages: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "meta": {
            "exported_at": datetime.now(timezone.utc).isoformat(),
            "channel_id": channel_id,
            "channel_name": channel_name,
            "message_count": len(messages),
            "range": "all_history",
        },
        "messages": messages,
    }
