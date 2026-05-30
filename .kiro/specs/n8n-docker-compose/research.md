# Research & Design Decisions: n8n-playwright-vnc-docker

## Summary
- **Feature**: n8n-playwright-vnc-docker
- **Discovery Scope**: Extension / Refactoring (Task Runner Architecture)
- **Key Findings**:
  - n8n v1.111.0+ の External Task Runner mode が公式推奨アーキテクチャ
  - `N8N_RUNNERS_AUTH_TOKEN` と `N8N_RUNNERS_TASK_BROKER_URI` が必須環境変数
  - RedisはQueueモード用、Task RunnerはWebSocketでn8n-mainに直接接続
  - Playwright v1.51.1-jammy へ更新が必要（v1.40.0はセキュリティリスク）

## Research Log

### n8n External Task Runner Architecture
- **Context**: n8nのTask Runner構成に関する最新情報
- **Sources**:
  - [n8n Task Runners Documentation](https://docs.n8n.io/hosting/configuration/task-runners/)
  - [Task Runner Environment Variables](https://docs.n8n.io/hosting/configuration/environment-variables/task-runners/)
- **Findings**:
  - External modeでは、Task RunnerはWebSocketでn8nのTask Brokerに接続（Redisは経由しない）
  - `N8N_RUNNERS_ENABLED=true` - n8n-main側でランナーを有効化
  - `N8N_RUNNERS_AUTH_TOKEN` - 共有シークレット（ランナー認証用）
  - `N8N_RUNNERS_BROKER_LISTEN_ADDRESS=0.0.0.0` - 外部接続許可
  - `N8N_RUNNERS_TASK_BROKER_URI` - Task Broker URI（デフォルト: http://127.0.0.1:5679）
  - n8n v1.111.0+ が必要
- **Implications**:
  - 設計書のアーキテクチャ図は修正が必要（Redis間接接続から直接WebSocketに）
  - 環境変数の記載漏れを補完

### n8n.io/runners Image vs Custom Image
- **Context**: n8n公式の`n8nio/runners`イメージとカスタムイメージの比較
- **Sources**:
  - [n8nio/runners - Docker Hub](https://hub.docker.com/r/n8nio/runners)
  - [n8n PR #12017 - Runner broker URI rename](https://github.com/n8n-io/n8n/pull/12017)
- **Findings**:
  - `n8nio/runners` は公式サポートのTask Runner専用イメージ
  - `N8N_RUNNERS_AUTH_TOKEN_FILE` はサポートされていない（ファイルマウント不可）
  - v1.111.0で`N8N_RUNNERS_TASK_BROKER_URI`へ環境変数がrename
- **Implications**:
  - カスタムイメージ作成は許可された構成だが、公式イメージの利用も検討可能

### Playwright Version Update
- **Context**: Playwrightイメージの最新バージョン確認
- **Sources**:
  - [Playwright Releases](https://playwright.dev/versions)
  - [GitHub Issue - :latest tag issue](https://github.com/microsoft/playwright/issues/32483)
- **Findings**:
  - v1.40.0 (2024年リリース) は非常に古い、セキュリティパッチ未適用
  - v1.51.1-jammy が最新のJammyベースイメージ
  - `:latest` タグは信頼できない（v1.46.1を指す問題あり）
  - Jammy（Ubuntu 22.04）ベースの安定版
- **Implications**:
  - Dockerfile.vnc: `v1.40.0-jammy` → `v1.51.1-jammy`
  - docker-compose.yml playwrightサービス: `v1.40.0-jammy` → `v1.51.1-jammy`
  - Dockerfile.taskrunner: `v1.49.0-jammy` → `v1.51.1-jammy` に統一

### Redis Role Clarification
- **Context**: Redisの役割とTask Runnerとの関係
- **Sources**: n8n Task Runners Documentation
- **Findings**:
  - RedisはBullキューのストレージ、Task RequesterとWorker間のキューモード用
  - Task Runnerはn8nのTask Broker（WebSocket, port 5679）に直接接続
  - 図の `Task Runner ↔ Redis` は誤り、正しくは `Task Runner ↔ n8n-main (WebSocket)`
- **Implications**:
  - アーキテクチャ図の修正が必要
  - Redisは Queue mode のWorker用、Task Runner用ではない

### Single Container Process Management
- **Context**: 複数のプロセス（n8n, Xvfb, VNC）を1つのコンテナで安定稼働させる方法
- **Findings**: `dumb-init` をエントリポイントとし、`start.sh` 内でバックグラウンド実行を制御
- **Implications**: 既存の `start.sh` を拡張し、n8nの起動も管理下に置く

## Architecture Pattern Evaluation

| Option | Description | Strengths | Risks / Limitations | Notes |
|--------|-------------|-----------|---------------------|-------|
| n8nio/runners | 公式Task Runnerイメージ | 安定性、公式サポート | カスタムGUI環境の追加が困難 | GUI不要なTask Runner用 |
| Custom Image (Current) | Playwrightベースのカスタムイメージ | Playwright/VNC統合が可能 | 自前でプロセス管理が必要 | GUI操作が必要な本プロジェクトに適する |

## Design Decisions

### Decision: Redisの役割を明確化
- **Context**: 設計書でのRedisの誤った使用
- **Selected Approach**: RedisはQueueモードのWorker用キューストア、Task Runnerはn8n-mainに直接WebSocket接続
- **Rationale**: n8n公式のTask Runner architectureに準拠
- **Trade-offs**: 設計書の図を修正、ドキュメント更新が必要

### Decision: 環境変数を完全化
- **Context**: 設計書での必須環境変数の記載漏れ
- **Selected Approach**: `N8N_RUNNERS_ENABLED`, `N8N_RUNNERS_AUTH_TOKEN`, `N8N_RUNNERS_TASK_BROKER_URI` を追加
- **Rationale**: 外部モードでTask Runnerが起動するために必須
- **Trade-offs**: 設計書とDocker Composeの環境変数を完全化

### Decision: Playwrightバージョン更新
- **Context**: v1.40.0のセキュリティリスク
- **Selected Approach**: v1.51.1-jammyに統一
- **Rationale**: セキュリティパッチ適用、最新ブラウザサポート
- **Trade-offs**: 既存構成の更新が必要

### Decision: 統合コンテナ構成の維持
- **Context**: 最小構成での運用要件
- **Selected Approach**: Playwright/VNCを含む単一コンテナ構成を維持
- **Rationale**: ユーザーの「最小限」要件に合致、デバッグしやすい
- **Trade-offs**: コンテナが肥大化するが、全体のコンテナ数は少ない

## Risks & Mitigations
- **Redis接続誤認**: 設計書のアーキテクチャ図を修正、直接WebSocket接続に変更
- **環境変数漏れ**: 必須環境変数を完全化、設定ミスで起動失敗しないように
- **Playwrightバージョン**: v1.51.1-jammyに更新、セキュリティリスク解消
- **プロセス死活監視**: `dumb-init` と `start.sh` 内での適切なシグナル処理で対応
- **メモリ不足**: `NODE_OPTIONS` によるヒープサイズの制限
