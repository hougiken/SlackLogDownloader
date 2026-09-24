from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

from .serializer import build_export_payload
from .slack_client import SlackClient, SlackClientError


def get_token() -> str:
    load_dotenv()
    token = os.getenv("SLACK_BOT_TOKEN", "").strip()
    if not token:
        raise ValueError("SLACK_BOT_TOKEN が未設定です。.env を確認してください。")
    if not token.startswith("xoxb-") and not token.startswith("xoxp-"):
        raise ValueError("SLACK_BOT_TOKEN の形式が不正です。xoxb- または xoxp- で始まる値を設定してください。")
    return token


def choose_channel(channels: list[dict[str, object]]) -> dict[str, object]:
    for index, channel in enumerate(channels, 1):
        name = str(channel.get("name", "unknown"))
        channel_type = "private" if channel.get("is_private") else "public"
        print(f"[{index:3}] #{name} ({channel_type})")

    while True:
        raw = input("ダウンロード対象チャンネルの番号を入力してください: ").strip()
        if not raw.isdigit():
            print("数字を入力してください。")
            continue

        choice = int(raw)
        if 1 <= choice <= len(channels):
            return channels[choice - 1]

        print(f"1 から {len(channels)} の範囲で入力してください。")


def save_json(payload: dict[str, object], channel_name: str) -> Path:
    output_dir = Path("output")
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_channel_name = channel_name.replace("/", "_")
    output_path = output_dir / f"{safe_channel_name}_{timestamp}.json"

    with output_path.open("w", encoding="utf-8") as file:
        json.dump(payload, file, ensure_ascii=False, indent=2)

    return output_path


def main() -> int:
    try:
        token = get_token()
        client = SlackClient(token)
        client.verify_auth()

        print("チャンネル一覧を取得しています...")
        channels = client.list_joined_channels()
        if not channels:
            print("取得可能なチャンネルがありません。アプリがチャンネルに参加しているか確認してください。")
            return 1

        selected = choose_channel(channels)
        channel_id = str(selected.get("id"))
        channel_name = str(selected.get("name", "unknown"))

        print(f"#{channel_name} のログを取得しています。件数が多い場合は時間がかかります...")
        messages = client.get_channel_messages_with_threads(channel_id)

        payload = build_export_payload(channel_id=channel_id, channel_name=channel_name, messages=messages)
        output_path = save_json(payload, channel_name)

        print(f"完了: {len(messages)} 件のメッセージを保存しました。")
        print(f"出力ファイル: {output_path}")
        return 0

    except (ValueError, SlackClientError) as error:
        print(f"エラー: {error}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
