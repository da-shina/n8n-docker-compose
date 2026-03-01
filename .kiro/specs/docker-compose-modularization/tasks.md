# Docker Compose Modularization 実装タスク

## 1. 環境変数管理構造の整備 (P)

*   **1.1. 環境変数ファイルの整理** (5.1, 5.2) - [x]
    *   `.env` ファイルからアーキテクチャ固定値（`N8N_RUNNERS_MODE`、`N8N_USER_FOLDER` など）を削除し、機密情報（`N8N_ENCRYPTION_KEY`）とユーザー固有情報（`TZ`、`GENERIC_TIMEZONE`、`REDIS_PASSWORD`）のみを残す。
    *   `.env_sample` ファイルからアーキテクチャ固定値を削除し、機密情報とユーザー固有情報のみを残す。
    *   _Requirements: 5.1, 5.2_

*   **1.2. データ永続化用ディレクトリの作成** (3.1) - [x]
    *   `mkdir` コマンドで `./n8n_data`、`./playwright_data`、`./redis_data` ディレクトリを作成する。
    *   パーミッションを `1000:1000` に設定し、コンテナユーザーが読み書きできるようにする。
    *   _Requirements: 3.1_

*   **1.3. Redis TLS設定ファイルの準備** (2.1) - [x]
    *   `./redis.conf` ファイルにTLS設定（`tls-port 6380`、`tls-auth-clients no`など）を記述する。
    *   `./ssl/redis/` ディレクトリに証明書ファイル（`ca.crt`、`server.crt`、`server.key`）を配置する。
    *   _Requirements: 2.1_

## 2. メッセージキュー (Redis) の実装 (P)

*   **2.1. Redisコンテナの定義** (1.2, 2.1, 3.2) - [x]
    *   `docker-compose.yml` に `redis` サービスを定義し、公式 `redis:7-alpine` イメージを指定する。
    *   `./redis_data` を `/data` にマウントし、起動コマンドで `redis.conf` を読み込む。
    *   `./ssl/redis` をコンテナ内に読み取り専用でマウントし、TLS通信を有効化する。
    *   内部ネットワークに接続し、外部へのポート公開は行わない（`REDIS_TLS_PORT` は内部のみ）。
    *   _Requirements: 1.2, 2.1, 3.2_

*   **2.2. Redis接続設定の統一** (1.2, 2.1) - [x]
    *   n8n ServerおよびTask Runnerの環境変数から重複するRedis接続設定（`N8N_REDIS_HOST`、`N8N_REDIS_PORT` など）を整理する。
    *   `QUEUE_BULL_REDIS_*` と `N8N_REDIS_*` の両方の接頭辞を使用する必要があるか確認し、必要最小限に抑える。
    *   _Requirements: 1.2, 2.1_
    *   **修正履歴**: n8n Serverから`N8N_RUNNERS_CONNECT_TO_URL`を削除し、Task Runnerのボリュームマウントパスを`/home/node/.n8n`に統一した。また、`redis.conf`でAOF永続化を有効化した。

## 3. n8n Server (メイン) の実装

*   **3.1. n8n Serverコンテナの構成変更** (1.1, 1.2, 2.1, 3.1, 3.2)
    *   `docker-compose.yml` に `n8n` サービスを定義し、公式イメージ `docker.n8n.io/n8nio/n8n:stable` を指定する。
    *   `./n8n_data` を `/home/node/.n8n` にマウントし、ワークフローと認証情報を永続化する。
    *   `./playwright_data` を `/home/node/user-data` にマウントし、Playwright関連データを共有する。
    *   キューモードを有効化する環境変数（`EXECUTIONS_MODE=queue`、`QUEUE_BULL_REDIS_HOST=redis` など）を追加する。
    *   ポート `5678` をホストへ公開し、`redis` サービスへの依存関係を `condition: service_healthy` で設定する。
    *   _Requirements: 1.1, 1.2, 2.1, 3.1, 3.2_

## 4. n8n Task Runner の実装 (P)

*   **4.1. Task Runnerコンテナの定義** (1.2, 2.1, 3.1, 3.2)
    *   `docker-compose.yml` に `n8n-task-runner` サービスを定義し、公式イメージ `docker.n8n.io/n8nio/n8n:stable` を指定する。
    *   起動コマンドを `n8n worker` に上書きし、ワーカープロセスとして動作させる。
    *   `./n8n_data` を `/home/node/.n8n` にマウントし、n8n Serverとワークフローデータを共有する。
    *   Redis接続設定をn8n Serverと統一し、TLS通信を有効化する。
    *   ホストへのポート公開は行わず、内部ネットワークのみに接続する。
    *   _Requirements: 1.2, 2.1, 3.1, 3.2_

## 5. Playwright MCP の実装 (P)

*   **5.1. Playwrightコンテナの定義** (1.3, 2.1, 3.1, 3.2)
    *   `docker-compose.yml` に `playwright` サービスを定義し、Ubuntuベースの公式イメージ `mcr.microsoft.com/playwright:v1.40.0-jammy` を指定する。
    *   `./playwright_data` を `/home/pwuser/user-data` にマウントし、ブラウザプロファイルとセッションデータを永続化する。
    *   MCP用ポート `8931` を内部ネットワークで公開し、n8n ServerとTask Runnerからの接続を受け入れる。
    *   `PLAYWRIGHT_SERVER_PORT=8931` を環境変数で設定する。
    *   _Requirements: 1.3, 2.1, 3.1, 3.2_

## 6. VNC Service の統合 (P)

*   **6.1. VNCコンテナの定義** (1.3, 3.2)
    *   `docker-compose.yml` に `vnc` サービスを定義し、ホストのポート `5900` にマッピングする。
    *   Playwrightコンテナと `./playwright_data` を共有し、GUI操作の可視化を可能にする。
    *   `VNC_PASSWORD` を `.env` から読み込むように設定し、セキュアな認証を実現する。
    *   Xvfbと軽量WM（fluxboxなど）を起動する初期化スクリプトを準備する。
    *   _Requirements: 1.3, 3.2_

## 7. 問題修正と検証

*   **7.1. Redisコンテナの権限と永続化設定** (2.1, 3.1)
    *   `redis_data` ディレクトリの所有者を `1000:1000` に変更し、コンテナ内ユーザーが書き込み可能であることを確認する。
    *   `redis.conf` にAOF（`appendonly yes`）とRDB（`save`）の永続化設定を記述する。
    *   `podman compose up -d redis` を実行し、コンテナがhealthy状態で起動することを確認する。
    *   _Requirements: 2.1, 3.1_

*   **7.2. n8n ServerとTask Runnerの連携テスト** (1.2, 4.1, 4.2)
    *   `podman compose up -d` で全サービスを起動し、n8n Web UIにアクセスする。
    *   Queueモードで実行されていることを確認し、Task Runnerがジョブを処理していることをログで検証する。
    *   _Requirements: 1.2, 4.1, 4.2_

*   **7.3. Playwrightコンテナの起動確認** (5.1)
    *   `podman compose ps` で Playwright コンテナがリストされることを確認する。
    *   `podman compose logs playwright` でエラーがないことを確認する。
    *   Playwright MCPエンドポイント（`http://localhost:8931`）に接続できることを検証する。
    *   _Requirements: 5.1_

*   **7.4. 全サービス連携テスト** (1.2, 3.1, 3.2, 4.1)
    *   `podman compose ps` で全サービスがhealthy状態になることを確認する。
    *   n8n Web UIからPlaywrightノードを含むワークフローを実行し、正常に完了することを検証する。
    *   _Requirements: 1.2, 3.1, 3.2, 4.1_

*   **7.5. VNC接続テスト** (1.3, 6.1)
    *   VNCクライアントから `localhost:5900` に接続し、PlaywrightコンテナのGUI画面が表示されることを確認する。
    *   VNC接続時の認証（パスワード）が正常に動作することを検証する。
    *   _Requirements: 1.3, 6.1_
