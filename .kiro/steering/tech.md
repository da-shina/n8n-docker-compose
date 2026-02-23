# Tech Steering

## Stack
- Docker/Podman: コンテナ管理
- n8n: ワークフロー自動化
- Playwright: ブラウザ操作自動化
- VNC: GUI操作の可視化
- LangChain: AIエージェント連携
- Google Services: Gemini API、スプレッドシート連携

## Architecture Decisions
- Single Stage Docker Build: ビルド時間短縮とシンプルな構造
- Playwright v1.40.0-jammy: GUI操作対応のためのイメージ選定
- Xvfb + fluxbox + x11vnc: コンテナ内のGUI操作環境構築
- Node.js 22.x: 最新のJavaScriptサポート

## Conventions
- 認証情報はn8n Credentialsで管理
- 環境変数は.envファイルで管理
- コミュニティノードを活用して機能拡張
- Playwright MCP Toolでブラウザ操作を抽象化