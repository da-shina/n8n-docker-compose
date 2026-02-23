# Structure Steering

## Directory Organization
- ルート: Dockerfile、docker-compose.yml、起動スクリプト
- temp/: ワークフロー設計書、開発タスクなど一時ファイル
- .kiro/: 規約、ステアリング、仕様書

## Naming Convention
- ファイル: 英数字とハイフン、アンダースコア
- ワークフロー: 日本語での説明的命名
- 環境変数: UPPER_SNAKE_CASE

## Component Structure
- n8nサービス: ワークフロー実行エンジン
- Playwright: ブラウザ操作コンポーネント
- VNC: GUI操作可視化インターフェース
- 各ツールノード: API連携用のHTTP Requestノード