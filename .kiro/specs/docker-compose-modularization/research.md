# Docker Compose Modularization 調査ログ

## 概要
現在の単一サービス構成から、マルチサービス構成へのモジュール化に関する技術調査。
特にTask Runner、Redis、およびPlaywrightの統合と制約事項を対象とする。

## 調査トピック

### トピック 1: n8n Queue Mode (Task Runner)
* **目的**: メインプロセスからワークフロー実行をオフロードするためのアーキテクチャ調査。
* **主な発見**:
  * n8nはメイン（サーバー）プロセスとワーカープロセスの間でRedisをメッセージキューとして使用して通信を行う。
  * `docker.n8n.io/n8nio/n8n` イメージ自体がワーカーとしても動作する。公式の専用イメージとして `docker.n8n.io/n8nio/n8n-task-runners` も指定可能。
  * `EXECUTIONS_MODE=queue` を設定することでキューモードが有効になる。
  * `QUEUE_MESSAGE_PULL_DELAY` などのキュー制御変数や、Task Runner専用の環境変数（`N8N_RUNNERS_MODE` 等）の設定が必要になる場合がある。
* **設計への影響**:
  * n8nコンテナとTask Runnerコンテナで同じベースイメージを利用しつつ、起動コマンドや環境変数で役割を分担する設計とする。

### トピック 2: Redis の設定
* **目的**: n8nのQueue Modeにおけるメッセージブローカーとしての要件の特定。
* **主な発見**:
  * n8nは環境変数（`QUEUE_BULL_REDIS_HOST`, `QUEUE_BULL_REDIS_PORT`など、または`N8N_REDIS_HOST`等）を通じてRedisに接続する。
  * 公式Redisイメージを利用可能だが、プロダクション品質のためにはパスワード設定と永続化（AOF/RDB）が推奨される。
* **設計への影響**:
  * Redisコンテナを独立して立て、内部ブリッジネットワーク経由でn8nおよびTask Runnerからのみアクセス可能にする。

### トピック 3: Playwright DockerイメージとAlpine Linuxの互換性
* **目的**: PlaywrightをAlpineベースのイメージで動作させることができるかの確認。
* **主な発見**:
  * [Playwrightの公式ドキュメント](https://playwright.dev/docs/docker)によれば、「Alpine Linuxおよびmusl標準Cライブラリをベースとする他のディストリビューションはサポートされていません（Alpine Linux and other distributions that are based on the musl standard library are not supported）」。
* **設計への影響**:
  * 要件定義に記載された「Alpineベースイメージ」の使用は不可能であるため、要件定義書を更新し、公式にサポートされているUbuntuベース（例：`jammy`）のイメージを引き続き使用するように設計を変更する。

## アーキテクチャパターンの評価

| パターン | 長所 | 短所 | 決定事項 |
|---------|------|------|----------|
| 単一コンテナ (現状) | 設定がシンプル、リソース消費が少ない | モジュール単位のスケーリング不可、障害が全体に波及 | 廃止 |
| マルチサービス (Queue Mode) | 高可用性、モジュールごとのスケーリング可能 | Redis等追加コンポーネントが必要、設定が複雑 | **採用** |

## リスクと緩和策

* **リスク 1**: Redisの接続エラーによるワークフローの実行停止。
  * **緩和策**: Redisサービスのヘルスチェックを設定し、Task Runnerとn8nサーバーの依存関係（`depends_on` + `condition: service_healthy`）を定義する。
* **リスク 2**: PlaywrightのAlpine非対応問題。
  * **緩和策**: 要件を調整し、公式提供のUbuntuベースイメージを採用する。