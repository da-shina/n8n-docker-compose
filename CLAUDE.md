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

## テストに関する注意

- すべてのテストは相対パスでファイルを読み込むため、**リポジトリのルートから** `python -m pytest tests` を実行すること。
- `test_infra.py::test_env_file_exists` は `.env` の存在を前提とするため、事前に `cp .env_sample .env` が必要。
- 統合テスト（`test_integration.py`）は compose スタックが起動している必要があり、起動していない場合はスキップされる。

## .claude/settings.local.json

フック・権限の許可リストが定義済み。`docker-compose.yml` / `Dockerfile` を Edit するとテストが自動実行され、`.env` の直接編集は促すプロンプトが表示される。
