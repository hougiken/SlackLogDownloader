from __future__ import annotations

from typing import Any

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from .retry import call_with_retry
from .serializer import normalize_message


class SlackClientError(Exception):
    pass


class SlackClient:
    def __init__(self, token: str) -> None:
        self.client = WebClient(token=token)

    def verify_auth(self) -> None:
        try:
            call_with_retry(lambda: self.client.auth_test())
        except SlackApiError as error:
            raise SlackClientError(self._friendly_error(error)) from error

    def list_joined_channels(self) -> list[dict[str, Any]]:
        channels: list[dict[str, Any]] = []
        cursor: str | None = None

        while True:
            try:
                response = call_with_retry(
                    lambda: self.client.conversations_list(
                        types="public_channel,private_channel",
                        exclude_archived=True,
                        limit=200,
                        cursor=cursor,
                    )
                )
            except SlackApiError as error:
                raise SlackClientError(self._friendly_error(error)) from error

            page_channels = response.get("channels", [])
            # joined-only because private channels require app membership.
            channels.extend([c for c in page_channels if c.get("is_member")])

            cursor = response.get("response_metadata", {}).get("next_cursor")
            if not cursor:
                break

        channels.sort(key=lambda x: x.get("name", ""))
        return channels

    def get_channel_messages_with_threads(self, channel_id: str) -> list[dict[str, Any]]:
        messages: list[dict[str, Any]] = []
        cursor: str | None = None

        while True:
            try:
                response = call_with_retry(
                    lambda: self.client.conversations_history(
                        channel=channel_id,
                        limit=200,
                        cursor=cursor,
                    )
                )
            except SlackApiError as error:
                raise SlackClientError(self._friendly_error(error)) from error

            for message in response.get("messages", []):
                normalized = normalize_message(message)
                normalized["replies"] = self._fetch_replies_if_needed(channel_id, message)
                messages.append(normalized)

            cursor = response.get("response_metadata", {}).get("next_cursor")
            if not cursor:
                break

        messages.sort(key=lambda x: x.get("ts") or "")
        return messages

    def _fetch_replies_if_needed(self, channel_id: str, message: dict[str, Any]) -> list[dict[str, Any]]:
        thread_ts = message.get("thread_ts")
        reply_count = message.get("reply_count", 0)
        message_ts = message.get("ts")

        if not thread_ts or reply_count == 0 or thread_ts != message_ts:
            return []

        replies: list[dict[str, Any]] = []
        cursor: str | None = None

        while True:
            try:
                response = call_with_retry(
                    lambda: self.client.conversations_replies(
                        channel=channel_id,
                        ts=thread_ts,
                        limit=200,
                        cursor=cursor,
                    )
                )
            except SlackApiError as error:
                raise SlackClientError(self._friendly_error(error)) from error

            thread_messages = response.get("messages", [])
            for thread_message in thread_messages:
                if thread_message.get("ts") == message_ts:
                    continue
                replies.append(normalize_message(thread_message))

            cursor = response.get("response_metadata", {}).get("next_cursor")
            if not cursor:
                break

        replies.sort(key=lambda x: x.get("ts") or "")
        return replies

    @staticmethod
    def _friendly_error(error: SlackApiError) -> str:
        code = error.response.get("error") if error.response else "unknown"

        mapping = {
            "invalid_auth": "Slackトークンが無効です。SLACK_BOT_TOKENを確認してください。",
            "missing_scope": "Slackトークンのスコープが不足しています。READMEの必要スコープを確認してください。",
            "not_in_channel": "対象チャンネルにアプリが参加していません。Slack側でチャンネルに追加してください。",
            "channel_not_found": "対象チャンネルが見つかりません。",
        }

        return mapping.get(code, f"Slack APIエラー: {code}")
