# CLAUDE.md

このファイルは、Claude Code (claude.ai/code) がこのリポジトリのコードを扱う際のガイダンスを提供します。

## リポジトリ概要

n8n（ワークフロー自動化プラットフォーム）を、Code ノード用の外部タスクランナー (`n8nio/runners`) と、別々の Playwright ブラウザコンテナ (`n8n-task-runner`) とともに構成する Docker/Podman Compose プロジェクト。キュー用の Redis も含む。

## コマンド

### コンテナ管理

```bash
# 初回実行: .env を作成し、必要な秘密情報を入力する
cp .env_sample .env

# すべてのサービスを起動
podman-compose up -d

# Dockerfile 変更後に再ビルドして起動
podman-compose up -d --build

# ログを表示（すべてまたは特定サービス）
podman-compose logs -f
podman-compose logs -f n8n-runners
podman-compose logs -f n8n-task-runner

# サービスを停止
podman-compose down
```

### テスト

テストはリポジトリのルートから実行する（テストは相対パスでファイルを読み込む）。

```bash
# すべてのテストを実行
python -m pytest tests

# 特定のテストファイルを実行
python -m pytest tests/test_env_config.py

# 単一のテストを実行
python -m pytest tests/test_env_config.py::test_env_sample_has_runner_settings -v
```

`tests/check_python.py` は参考情報（Python 環境の確認）であり、テスト対象ではない。

## アーキテクチャ

### サービス構成（docker-compose.yml）

- **n8n** (`docker.io/n8nio/n8n:${N8N_VERSION}`): ポート 5678 で UI とワークフロー実行。Code ノードは外部タスクランナーに委譲 (`N8N_RUNNERS_MODE=external`)。
- **n8n-runners** (`docker.io/n8nio/runners:${N8N_VERSION}`): 公式外部タスクランナーサイドカー。JavaScript / Python の Code ノードを隔離プロセスで実行。タスクブローカーは n8n のポート 5679 (`ws://n8n:5679`)。
- **n8n-task-runner** (`Dockerfile.taskrunner` ビルド): Playwright ブラウザ + VNC。`http://n8n-task-runner:8931/mcp` で Playwright MCP を提供（エイリアス `playwright` も可）。VNC はポート 5900。
- **redis** (`docker.io/library/redis:7-alpine`): キューストア。キューモード未有効のため現在未使用。将来のキュー モードには PostgreSQL も必要（n8n は SQLite でキュー モード未サポート）。

### 主なファイル

- `docker-compose.yml`: サービス定義・ネットワーク・ボリューム・ヘルスチェック
- `Dockerfile.taskrunner`: Playwright/VNC ブラウザイメージのビルド。`@playwright/mcp` と一致する Chromium を `PLAYWRIGHT_BROWSERS_PATH` にインストール
- `start.sh`: ブラウザコンテナのエントリポイント。Xvfb、Fluxbox、x11vnc、Playwright MCP を起動し `exec sleep infinity` で生かす
- `redis.conf`: Redis 設定（AOF 有効、`maxmemory-policy noeviction`）
- `.env` / `.env_sample`: 環境変数と必須の秘密情報（`.env` は未コミット）

### ネットワーキング

- サービス間は Docker ブリッジネットワーク経由（ホストネットワークではない）
- n8n → Playwright MCP: `http://n8n-task-runner:8931/mcp`（`playwright` エイリアスも可）
- MCP は認証がないため `127.0.0.1:8931` にのみ公開（ホスト外非公開）
- VNC はポート 5900 で公開、常に `VNC_PASSWORD` が必要
- タスクブローカーは Docker ネットワーク内のみポート 5679 をリッスン
- `host.docker.internal:host-gateway` でホストマシンにマップ

### ボリューム（名前付きボリューム）

すべての永続データは名前付きボリューム。Compose 初回起動時に作成：

- `n8n-docker-compose_n8n_data`: n8n のユーザーデータとワークフロー (`/home/node/.n8n`)
- `n8n-docker-compose_playwright_data`: ブラウザプロファイル（クッキー、ログイン）(`/home/pwuser/user-data`)
- `n8n-docker-compose_redis_data`: Redis の永続データ（AOF）(`/data`）

## 設定

必須の秘密情報（空の場合スタックは起動を拒否）：

- `N8N_ENCRYPTION_KEY`: 保存された認証情報の暗号化キー（`openssl rand -hex 32`）
- `N8N_RUNNERS_AUTH_TOKEN`: n8n と n8n-runners 間の共有シークレット（`openssl rand -hex 32`）
- `REDIS_PASSWORD`: Redis 認証パスワード（`openssl rand -hex 32`）
- `VNC_PASSWORD`: VNC アクセスパスワード（VNC プロトコルの制限で最大 8 文字）

バージョニング：

- `N8N_VERSION` は n8n と n8n-runners の両方のイメージで使用。一致していなければならない。
- イメージは `docker.io` を直接指定（`docker.n8n.io` プロキシ経由の匿名レート制限を回避）。

キューモード：

- キュー モードは未有効。Redis 設定は将来のセットアップのため保持。

## テストに関する注意

- すべてのテストは相対パスでファイルを読み込むため、**リポジトリのルートから** `python -m pytest tests` を実行すること。
- `test_infra.py::test_env_file_exists` は `.env` の存在を前提とするため、事前に `cp .env_sample .env` が必要。
- 統合テスト（`test_integration.py`）は compose スタックが起動している必要があり、起動していない場合はスキップされる。

## .claude/settings.local.json

フック・権限の許可リストが定義済み。`docker-compose.yml` / `Dockerfile` を Edit するとテストが自動実行され、`.env` の直接編集は促すプロンプトが表示される。
