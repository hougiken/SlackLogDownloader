from src.main import choose_channel


def test_choose_channel_returns_selected_item(monkeypatch) -> None:
    channels = [
        {"id": "C1", "name": "general", "is_private": False},
        {"id": "C2", "name": "random", "is_private": True},
    ]

    monkeypatch.setattr("builtins.input", lambda _: "2")
    selected = choose_channel(channels)

    assert selected["id"] == "C2"


def test_choose_channel_retries_on_invalid(monkeypatch) -> None:
    channels = [{"id": "C1", "name": "general", "is_private": False}]
    answers = iter(["abc", "9", "1"])

    monkeypatch.setattr("builtins.input", lambda _: next(answers))
    selected = choose_channel(channels)

    assert selected["id"] == "C1"
