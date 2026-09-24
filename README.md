# Slack Log Downloader

Slackのチャンネル一覧を取得し、選択したチャンネルのチャットログをJSONでダウンロードするCLIツールです。

## 機能

- 公開/非公開（参加済み）チャンネル一覧の取得
- 対象チャンネルの選択
- 全期間のメッセージ取得（ページング対応）
- スレッド返信の取得
- 添付ファイルURLの抽出
- JSON保存

## 前提

- Python 3.10+
- Slack Appのトークン（推奨: Bot Token `xoxb-...`）

## 必要スコープ（最低限）

- `channels:read`
- `groups:read`
- `channels:history`
- `groups:history`

補足:
- Botが参加していない非公開チャンネルは取得できません。
- ユーザープロファイル展開は初期版では行わないため、`users:read` は不要です。

## セットアップ

1. 依存をインストール

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. 環境変数を設定

```bash
cp .env.example .env
# .env の SLACK_BOT_TOKEN を実値に更新
```

## 実行

```bash
python -m src.main
```

実行後にチャンネル一覧が表示され、番号選択すると `output/` にJSONが保存されます。

## 出力形式

出力JSONには以下を含みます。

- 実行メタ情報（日時、チャンネル名/ID、件数）
- メッセージ本文
- スレッド返信（`replies`）
- 添付情報（`attachments`）

## エラーの例

- `invalid_auth`: トークン誤り/無効
- `missing_scope`: 必要スコープ不足
- `not_in_channel`: 非公開チャンネルで未参加
- `ratelimited`: レート制限（自動リトライ）

## テスト

```bash
pytest
```
