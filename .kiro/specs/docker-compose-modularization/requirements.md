# Docker Compose Modularization 機能要求

## 概要
現在の単一サービス構成のDocker Composeを、機能別に分割されたマルチサービス構成に改修する。公式ビルドイメージを最大限利用することで、メンテナンス性とセキュリティを向上させる。

## 1. 機能別サービス分割 (Functional Service Separation)

### 1.1 n8nサービス (n8n Service)
* **システムは**、n8nのメインアプリケーションを独立したコンテナサービスとして定義**しなければならない (shall)**。
* **システムは**、ワークフローおよび認証情報を永続化するために、ローカルフォルダである`n8n_data`をマウント**しなければならない (shall)**。
* **システムは**、n8nのウェブインターフェースへアクセスするためにポート`5678`を公開**しなければならない (shall)**。

### 1.2 n8n Task RunnerサービスとRedis (n8n Task Runner and Redis Services)
* **システムは**、n8n taskrunnerを独立したコンテナサービスとして定義**しなければならない (shall)**。
* **システムは**、Task Runnerのタスクキュー管理と状態共有のために、Redisを独立したコンテナサービスとして定義**しなければならない (shall)**。
* **カスタムコードまたはツールを必要とするワークフローを実行している間(While)**、**システムは**、それらの実行をtaskrunnerサービスにルーティング**しなければならない (shall)**。
* **システムは**、メインのn8nサービス、taskrunnerサービス、およびRedis間のセキュアな通信チャネルを構成**しなければならない (shall)**。

### 1.3 Playwright MCP と VNC サービス (Playwright MCP and VNC Service)
* **システムは**、Playwright MCPサーバーを独立したコンテナサービスとして定義**しなければならない (shall)**。
* **システムは**、ブラウザプロファイルとセッションデータを永続化するために、ローカルフォルダである`playwright_data`をマウント**しなければならない (shall)**。
* **システムは**、n8nサービスが接続するためにポート`3000`（または設定されたMCPポート）を公開**しなければならない (shall)**。
* **PlaywrightのデバッグにGUIの可視化が必要とされる場合(Where)**、**システムは**、Playwrightコンテナ内蔵のVNCサーバーを有効化し、VNCクライアント接続用にポート（例: `5900` または noVNC用の `8080` など）を公開**しなければならない (shall)**。

## 2. 公式イメージ活用 (Official Image Utilization)

### 2.1 イメージソース (Image Sources)
* **システムは**、メインのn8nサービスに公式の`docker.n8n.io/n8nio/n8n`イメージを使用**しなければならない (shall)**。
* **システムは**、taskrunnerサービスに公式の`docker.n8n.io/n8nio/n8n-task-runners`イメージを使用**しなければならない (shall)**。
* **システムは**、Task Runnerのキュー管理用に公式のRedisイメージを使用**しなければならない (shall)**。
* **システムは**、Playwright MCPサービスのベースとして公式のMicrosoft PlaywrightのUbuntuベースイメージ（例：`mcr.microsoft.com/playwright:v1.40.0-jammy`など）を使用**しなければならない (shall)**。（注：Playwright公式はAlpine Linuxをサポートしていません）

### 2.2 コミュニティノード対応 (Community Nodes Support)
* **カスタムノードまたはコミュニティノードが必要とされる場合(Where)**、**システムは**、可能な限り永続的にベースイメージの構造を変更することなく、公式イメージ上にそれらをインストールするメカニズム（例：初期化スクリプトやカスタムビルドステップ）を提供**しなければならない (shall)**。

## 3. 非機能要求 (Non-Functional Requirements)

### 3.1 メンテナンス性 (Maintainability)
* **システムは**、composeファイル内の各イメージタグを更新することで、n8n、Playwright、およびtaskrunnerの独立したバージョン更新を許可**しなければならない (shall)**。
* **システムは**、サービスごとに環境変数を論理的に分離**しなければならない (shall)**（例：n8n固有の環境変数はn8nサービスへ、Playwright固有の環境変数はPlaywrightサービスへ）。

### 3.2 セキュリティ (Security)
* **システムは**、n8n、taskrunner、Redis、およびPlaywright間の通信専用の内部ブリッジネットワークを構成**しなければならない (shall)**。
* **システムは**、外部からのアクセスをn8nのウェブインターフェース（`5678`）とVNC（`5900`）のみに制限し、MCP、taskrunner、およびRedisのポートは内部に維持**しなければならない (shall)**。

### 3.3 互換性 (Compatibility)
* **単一コンテナ構成から移行する際(When)**、**システムは**、`n8n_data`に保存された既存のワークフローとの互換性を維持**しなければならない (shall)**。
* **システムは**、設定管理用の`.env`ファイルのサポートを継続**しなければならない (shall)**。
* **システムは**、プロジェクトのガイドラインで指定されている通り、`podman compose`と完全に互換性を持た**なければならない (shall)**。