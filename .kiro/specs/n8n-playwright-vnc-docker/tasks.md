# Implementation Plan: n8n-playwright-vnc-docker

## Tasks

- [ ] 1. 共有インフラと環境設定の構築
- [ ] 1.1 (P) .env_sample ファイルの更新と環境変数定義
  - n8n外部タスクランナー向けの環境変数を追加（N8N_RUNNERS_ENABLED, AUTH_TOKEN, BROKER_LISTEN_ADDRESS）
  - Task Runner接続用URIと認証トークンの定義
  - Redis接続設定とキューモードパラメータの整理
  - _Requirements: 1.3_

- [ ] 1.2 (P) 永続化ボリュームの定義と権限設定
  - n8n_data, playwright_data, redis_dataボリュームの定義を整理
  - ユーザーID 1000:1000の権限設定を確認
  - _Requirements: 1.4_

- [ ] 2. n8n-main コンテナの設定更新
- [ ] 2.1 (P) n8n-main サービスの外部タスクランナーモード設定
  - N8N_RUNNERS_ENABLED=true を設定
  - N8N_RUNNERS_MODE=external を設定
  - N8N_RUNNERS_AUTH_TOKEN を共有シークレットとして設定
  - N8N_RUNNERS_BROKER_LISTEN_ADDRESS=0.0.0.0 を設定
  - _Requirements: 2.2_

- [ ] 2.2 (P) n8n-main サービスのRedis接続設定確認
  - QUEUE_BULL_REDIS_HOST, PORTを適切に設定
  - Redis TLS設定を無効化
  - _Requirements: 2.2_

- [ ] 3. n8n-taskrunner カスタムイメージの作成
- [ ] 3.1 (P) PlaywrightベースのTask Runner Dockerfileの更新
  - mcr.microsoft.com/playwright:v1.51.1-jammy をベースイメージに更新
  - Node.js 22.x および n8n パッケージのインストール
  - Xvfb、fluxbox、x11vnc などのGUI実行環境のセットアップ
  - _Requirements: 1.2, 3.1_

- [ ] 3.2 (P) 起動スクリプト (start.sh) の更新
  - 仮想ディスプレイ（DISPLAY=:99）の初期化と各GUIプロセスのバックグラウンド起動
  - VNCサーバー（x11vnc）のパスワード保護とポート公開設定
  - dumb-init を介した n8n worker メインプロセスのライフサイクル管理
  - _Requirements: 3.2, 4.1, 4.2, 4.3_

- [ ] 4. n8n-taskrunner サービスの設定
- [ ] 4.1 (P) n8n-taskrunner サービスのDocker Compose設定
  - Dockerfile.taskrunner をビルドソースに指定
  - 必須環境変数を設定（N8N_RUNNERS_MODE, AUTH_TOKEN, TASK_BROKER_URI）
  - ボリュームマウントを適切に設定
  - _Requirements: 1.1, 2.2_

- [ ] 4.2 (P) Task Runnerの認証と接続設定
  - N8N_RUNNERS_TASK_BROKER_URI=ws://n8n-main:5679 を設定
  - 共有認証トークンをn8n-mainと一致させる
  - _Requirements: 2.2_

- [ ] 5. PlaywrightとVNC統合の検証
- [ ] 5.1 (P) Playwright実行環境の検証
  - Task Runnerコンテナ内でPlaywrightが正常に実行できることを確認
  - Headless/Headedモードの切り替え機能を検証
  - _Requirements: 3.1, 3.2_

- [ ] 5.2 (P) VNCによるGUI操作可視化の検証
  - VNCサーバー（5900ポート）の起動と待機状態を確認
  - ブラウザ操作がVNC経由でリアルタイム表示されることを確認
  - _Requirements: 4.1, 4.2, 4.3_

- [ ] 6. サービス間の統合と連携テスト
- [ ] 6.1 (P) n8n-main と Task Runner 間の通信検証
  - WebSocket接続の確立を確認
  - タスクの正常な配送と実行を確認
  - _Requirements: 2.2_

- [ ] 6.2 (P) ワークフロー実行とPlaywright連携の検証
  - n8n UIからPlaywrightを使用するワークフローを実行
  - 正常にブラウザ操作が実行されることを確認
  - _Requirements: 2.2, 3.1_

- [ ] 7. セキュリティと堅牢性の強化
- [ ] 7.1 (P) Task Runnerのセキュリティ設定
  - 不要な権限を削減
  - メモリ制限（N8N_RUNNERS_MAX_OLD_SPACE_SIZE）を設定
  - _Requirements: 2.4_

- [ ] 7.2 (P) コンテナの堅牢性設定
  - restart: unless-stopped を設定
  - ヘルスチェックの実装を検討
  - _Requirements: 2.4_

- [ ] 8. ドキュメントとテストの整備
- [ ] 8.1 (P) READMEの更新
  - 外部タスクランナー構成の説明を追加
  - 新しい環境変数の説明を追加
  - _Requirements: 1.1_

- [ ] 8.2 (P) 動作確認手順の作成
  - VNC接続手順のドキュメント化
  - Playwright操作の検証手順の作成
  - _Requirements: 4.1, 4.2, 4.3_
