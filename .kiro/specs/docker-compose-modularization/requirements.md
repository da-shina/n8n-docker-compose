# Docker Compose Modularization 機能要求

## 概要
現在の単一サービス構成のDocker Composeを、機能別に分割されたマルチサービス構成に改修する。公式ビルドイメージを最大限利用することで、メンテナンス性とセキュリティを向上させる。

## 用語集 (Glossary)

- **System**: Docker Compose構成全体
- **n8n_Service**: n8nメインアプリケーションコンテナサービス
- **Task_Runner_Service**: n8n taskrunnerコンテナサービス
- **Redis_Service**: Redisキャッシュ/キューコンテナサービス
- **Playwright_Service**: Playwright MCPサーバーコンテナサービス
- **Persistent_Data**: コンテナ再起動後も保持されるべきデータ
- **Service_Dependency**: あるサービスが別のサービスの起動完了を必要とする関係

## 1. 機能別サービス分割 (Functional Service Separation)

### 1.1 n8nサービス (n8n Service)

**ユーザーストーリー:** 開発者として、n8nメインアプリケーションを独立したサービスとして実行したい。そうすることで、他のサービスと分離してメンテナンスできる。

#### 受入基準 (Acceptance Criteria)

1. THE System SHALL n8n_Service を独立したコンテナサービスとして定義すること
2. THE n8n_Service SHALL 公式のn8nイメージを使用すること
3. THE n8n_Service SHALL ワークフローおよび認証情報を永続化すること
4. THE n8n_Service SHALL 外部からウェブインターフェースへのアクセスを提供すること

### 1.2 Task RunnerサービスとRedis (Task Runner and Redis Services)

**ユーザーストーリー:** 開発者として、カスタムコードやツールを実行するタスクを専用のサービスで処理したい。そうすることで、メインのn8nサービスへの影響を最小化できる。

#### 受入基準 (Acceptance Criteria)

1. THE System SHALL Task_Runner_Service を独立したコンテナサービスとして定義すること
2. THE Task_Runner_Service SHALL 公式のn8n task runnerイメージを使用すること
3. THE System SHALL Redis_Service を独立したコンテナサービスとして定義すること
4. THE Redis_Service SHALL 公式のRedisイメージを使用すること
5. WHEN カスタムコードまたはツールを必要とするワークフローを実行する際、THE System SHALL それらの実行をTask_Runner_Serviceにルーティングすること
6. THE System SHALL n8n_Service、Task_Runner_Service、およびRedis_Service間の通信チャネルを構成すること

### 1.3 Playwright MCP と VNC サービス (Playwright MCP and VNC Service)

**ユーザーストーリー:** 開発者として、ブラウザ操作を自動化するPlaywright MCPサーバーを独立したサービスとして実行したい。そうすることで、n8nワークフローからブラウザ操作を利用できる。

#### 受入基準 (Acceptance Criteria)

1. THE System SHALL Playwright_Service を独立したコンテナサービスとして定義すること
2. THE Playwright_Service SHALL 公式のMicrosoft Playwright Ubuntuベースイメージを使用すること
3. THE Playwright_Service SHALL ブラウザプロファイルとセッションデータを永続化すること
4. THE Playwright_Service SHALL n8n_Serviceからの接続を受け入れるためのポートを公開すること
5. WHERE PlaywrightのデバッグにGUIの可視化が必要とされる場合、THE Playwright_Service SHALL VNCサーバーを有効化し、VNCクライアント接続用のポートを公開すること

## 2. セキュリティ要求 (Security Requirements)

### 2.1 Redis通信セキュリティ (Redis Communication Security)

**ユーザーストーリー:** 開発者として、Redisとの通信を暗号化したい。そうすることで、タスクキューのデータを保護できる。

#### 受入基準 (Acceptance Criteria)

1. THE Redis_Service SHALL TLS/SSL暗号化通信をサポートすること
2. THE Redis_Service SHALL 証明書ベースの認証を使用すること
3. THE System SHALL Redis_Serviceへの接続にパスワード認証を要求すること
4. THE System SHALL Redis認証情報を安全に管理すること

### 2.2 ネットワーク分離 (Network Isolation)

**ユーザーストーリー:** 開発者として、サービス間通信を内部ネットワークに制限したい。そうすることで、外部からの不正アクセスを防止できる。

#### 受入基準 (Acceptance Criteria)

1. THE System SHALL サービス間通信専用の内部ネットワークを構成すること
2. THE System SHALL 外部からのアクセスを必要最小限のサービスポートのみに制限すること
3. THE System SHALL 内部サービス（Task_Runner_Service、Redis_Service）のポートを外部に公開しないこと

## 3. データ永続化要求 (Data Persistence Requirements)

### 3.1 サービスデータの永続化 (Service Data Persistence)

**ユーザーストーリー:** 開発者として、コンテナを再起動してもデータが失われないようにしたい。そうすることで、ワークフローや設定を保持できる。

#### 受入基準 (Acceptance Criteria)

1. THE n8n_Service SHALL ワークフロー、認証情報、および設定データを永続化すること
2. THE Playwright_Service SHALL ブラウザプロファイル、セッションデータ、およびキャッシュを永続化すること
3. THE Redis_Service SHALL キューデータおよび状態情報を永続化すること
4. WHEN コンテナを再起動する際、THE System SHALL すべてのPersistent_Dataを保持すること

## 4. サービス依存関係と可用性 (Service Dependencies and Availability)

### 4.1 起動順序制御 (Startup Order Control)

**ユーザーストーリー:** 開発者として、サービスが正しい順序で起動するようにしたい。そうすることで、依存関係のエラーを防止できる。

#### 受入基準 (Acceptance Criteria)

1. WHEN Redis_Serviceが起動していない場合、THE System SHALL Task_Runner_Serviceの起動を待機させること
2. WHEN Redis_Serviceが起動していない場合、THE System SHALL n8n_Serviceの起動を待機させること
3. THE System SHALL 各サービスの準備状態を確認するヘルスチェック機構を提供すること

### 4.2 障害時の復旧 (Failure Recovery)

**ユーザーストーリー:** 開発者として、サービスが障害から自動的に復旧するようにしたい。そうすることで、システムの可用性を維持できる。

#### 受入基準 (Acceptance Criteria)

1. WHEN サービスが予期せず停止した場合、THE System SHALL 自動的にサービスを再起動すること
2. THE System SHALL 各サービスに適切な再起動ポリシーを適用すること
3. IF サービスが繰り返し失敗する場合、THE System SHALL 再起動試行を制限すること

## 5. メンテナンス性と互換性 (Maintainability and Compatibility)

### 5.1 バージョン管理 (Version Management)

**ユーザーストーリー:** 開発者として、各サービスのバージョンを独立して更新したい。そうすることで、柔軟なメンテナンスが可能になる。

#### 受入基準 (Acceptance Criteria)

1. THE System SHALL 各サービスのバージョンを独立して更新可能にすること
2. THE System SHALL 環境変数を各サービスごとに論理的に分離すること
3. WHERE カスタムノードまたはコミュニティノードが必要とされる場合、THE System SHALL 公式イメージの構造を変更せずにそれらをインストールする機構を提供すること

### 5.2 既存環境との互換性 (Compatibility with Existing Environment)

**ユーザーストーリー:** 開発者として、既存のワークフローや設定を引き続き使用したい。そうすることで、移行時のデータ損失を防止できる。

#### 受入基準 (Acceptance Criteria)

1. WHEN 単一コンテナ構成から移行する際、THE System SHALL 既存のワークフローデータとの互換性を維持すること
2. THE System SHALL 環境変数ファイル（.env）による設定管理をサポートすること
3. THE System SHALL podman composeとの完全な互換性を持つこと