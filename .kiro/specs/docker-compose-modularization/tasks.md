# Docker Compose Modularization 実装タスク

## 1. プロジェクト構造と環境変数設定の準備
*   **1.1. 環境変数管理構造の整備** (3.1, 3.3)
    *   `.env` ファイルからアーキテクチャ固定値（`N8N_RUNNERS_MODE` 等）を削除し、機密情報（`N8N_ENCRYPTION_KEY`）とユーザー固有情報（`TZ`等）のみを残す。
    *   ローカルデータ永続化用のディレクトリ（`./n8n_data`, `./playwright_data`, `./redis_data`）を作成する。
    *   [ ] 必要なディレクトリが適切に作成され、パーミッションが設定されているか確認する。

## 2. メッセージキュー (Redis) の実装 (P)
*   **2.1. Redisコンテナの定義** (1.2, 2.1, 3.2)
    *   `docker-compose.yml` に `redis` サービスを定義し、公式 `redis:7-alpine` イメージを指定する。
    *   `./redis_data` を `/data` にマウントし、AOF（Append Only File）などのデータ永続化設定を起動コマンド（command）で設定する。
    *   内部ネットワークに接続し、外部へのポート公開を行わない。

## 3. n8n Server (メイン) の実装
*   **3.1. n8n Serverコンテナの構成変更** (1.1, 2.1, 3.1, 3.2, 3.3)
    *   `docker-compose.yml` に `n8n` サービスを定義し、公式イメージ `docker.n8n.io/n8nio/n8n` を指定する。
    *   `./n8n_data` を `/home/node/.n8n` にマウントする。
    *   キューモードを有効化する環境変数（`EXECUTIONS_MODE=queue` 等）および Redis 接続設定（`QUEUE_BULL_REDIS_HOST` 等）をハードコードで追加する。
    *   ポート `5678` をホストへ公開し、`redis` サービスへの依存関係 (`depends_on`) を設定する。
    *   [ ] コンテナが起動し、Web UIにアクセスできることを確認する。

## 4. n8n Task Runner の実装 (P)
*   **4.1. Task Runner コンテナの定義** (1.2, 2.1, 3.1, 3.2)
    *   `docker-compose.yml` に `n8n-task-runner` サービスを定義し、公式イメージ `docker.n8n.io/n8nio/n8n` を指定する。
    *   起動コマンドをワーカープロセス用（`n8n worker` 等）に上書きする。
    *   `n8n` Serverと同様の Redis 接続設定および `./n8n_data` のマウントを設定する。
    *   ホストへのポート公開は行わず、内部ネットワークのみに接続する。
    *   [ ] テスト用ワークフローを実行し、ワーカープロセスで処理されるか確認する。

## 5. Playwright MCP の実装 (P)
*   **5.1. Playwrightコンテナの定義** (1.3, 2.1, 3.1, 3.2)
    *   `docker-compose.yml` に `playwright` サービスを定義し、Ubuntuベースの公式イメージ `mcr.microsoft.com/playwright:v1.40.0-jammy` を指定する。
    *   `./playwright_data` をセッションデータ用ディレクトリにマウントする。
    *   内部ネットワークに接続し、MCP用ポート（例:`8931`や`3000`）を公開しないよう設定する（内部でのみ通信可能にする）。

## 6. VNC Service の統合
*   **6.1. VNCコンテナ/サイドカーの定義** (1.4, 3.2)
    *   `docker-compose.yml` に `vnc` サービスを定義し、ホストのポート `5900` にマッピングする。
    *   Playwright コンテナの GUI 操作を可視化できるよう、必要なネットワークルーティングや共有ボリューム設定を構成する。
    *   [ ] VNCクライアントから接続し、Playwrightの動作画面が確認できるかテストする。