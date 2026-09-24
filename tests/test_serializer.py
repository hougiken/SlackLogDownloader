from src.serializer import build_export_payload, extract_attachments, normalize_message


def test_extract_attachments_from_files() -> None:
    message = {
        "files": [
            {
                "id": "F123",
                "name": "report.txt",
                "mimetype": "text/plain",
                "filetype": "text",
                "size": 10,
                "url_private": "https://example/private",
                "permalink": "https://example/permalink",
            }
        ]
    }

    attachments = extract_attachments(message)
    assert len(attachments) == 1
    assert attachments[0]["id"] == "F123"
    assert attachments[0]["url_private"] == "https://example/private"


def test_normalize_message_shape() -> None:
    message = {
        "ts": "1000.1",
        "user": "U123",
        "text": "hello",
        "thread_ts": "1000.1",
        "reply_count": 2,
        "files": [],
    }

    normalized = normalize_message(message)
    assert normalized["ts"] == "1000.1"
    assert normalized["reply_count"] == 2
    assert normalized["attachments"] == []


def test_build_export_payload_contains_meta() -> None:
    payload = build_export_payload("C123", "general", [{"ts": "1.0"}])
    assert payload["meta"]["channel_id"] == "C123"
    assert payload["meta"]["channel_name"] == "general"
    assert payload["meta"]["message_count"] == 1
    assert payload["messages"][0]["ts"] == "1.0"
