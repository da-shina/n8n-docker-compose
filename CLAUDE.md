# CLAUDE.md

このファイルは、Claude Code (claude.ai/code) がこのリポジトリのコードを扱う際のガイダンスを提供します。

## Commands

### Container Management
```bash
# 初回実行: .env を作成し、必要な秘密情報を入力する
cp .env_sample .env

# すべてのサービスを起動する
podman-compose up -d

# 再ビルドして起動する（Dockerfile 変更後）
podman-compose up -d --build

# ログを表示する（すべてまたは特定のサービス）
podman-compose logs -f
podman-compose logs -f n8n-runners

# サービスを停止する
podman-compose down
```

### Testing
```bash
# リポジトリのルートからすべてのテストを実行する（テストは相対パスでファイルを読み込む）
python -m pytest tests

# 特定のテストファイルを実行する
python -m pytest tests/test_env_config.py

# 単一のテストを実行する
python -m pytest tests/test_env_config.py::test_env_sample_has_runner_settings -v
```

## Architecture

このプロジェクトは n8n（ワークフロー自動化プラットフォーム）を、Code ノード用の外部タスクランナーと、別々の Playwright ブラウザとともに実行します。

### Services
- **n8n**: ポート 5678 のメイン n8n インスタンス。UI とワークフロー実行を担う。
- **n8n-runners**: 公式の外部タスクランナーサイドカー（`n8nio/runners`）。JavaScript と Python の Code ノードを隔離プロセスで実行する。
- **n8n-task-runner**: 仮想ディスプレイを備えた Playwright ブラウザ。ポート 8931 で Playwright MCP を実行し、ポート 5900 で x11vnc を実行する。
- **redis**: キューストア。キュー モードが有効になるまで使用されない。

### Key Files
- `docker-compose.yml`: サービス定義と設定
- `start.sh`: ブラウザのエントリポイント。Xvfb、Fluxbox、x11vnc、Playwright MCP を起動する
- `Dockerfile.taskrunner`: Playwright/VNC ブラウザイメージをビルドする。`@playwright/mcp` と一致する Chromium を `PLAYWRIGHT_BROWSERS_PATH` にインストールする
- `redis.conf`: Redis 設定（パスワードは `REDIS_PASSWORD` から渡される）
- `.env` / `.env_sample`: 環境変数と必要な秘密情報

### Networking
- サービス間の通信は Docker ネットワーク経由（ホスト ネットワークではない）
- n8n は `http://n8n-task-runner:8931/mcp` で Playwright MCP に到達する（`playwright` エイリアスも使用可能）
- MCP は認証がないため `127.0.0.1:8931` にのみ公開する
- VNC はポート 5900 で公開され、常に `VNC_PASSWORD` を必要とする
- タスク ブローカーは Docker ネットワーク内でのみポート 5679 をリッスンする
- `host.docker.internal:host-gateway` はホスト マシンにマップする

### Volumes (Named Volumes)
すべての永続データは名前付きボリュームを使用する。Compose は初回起動時に作成する：
- `n8n-docker-compose_n8n_data`: n8n のユーザ データとワークフロー
- `n8n-docker-compose_playwright_data`: ブラウザ プロファイル（クッキー、ログイン）
- `n8n-docker-compose_redis_data`: Redis の永続データ（AOF）

## Configuration

Required secrets（スタックはこれらが空の場合に起動を拒否する）:
- `N8N_ENCRYPTION_KEY`: 保存された認証情報の暗号化キー
- `N8N_RUNNERS_AUTH_TOKEN`: n8n と n8n-runners 間の共有シークレット
- `REDIS_PASSWORD`: Redis の認証パスワード
- `VNC_PASSWORD`: VNC アクセス パスワード（VNC は最大 8 文字を受け付ける）

Versioning:
- `N8N_VERSION` は n8n と n8n-runners の両方のイメージで使用される。一致していなければならない。

Queue mode:
- キュー モードは有効になっていない。Redis 設定は将来のセットアップのために保持されているが、それには PostgreSQL も必要となる（n8n は SQLite でキュー モードをサポートしていない）。
