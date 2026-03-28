# Implementation Plan: n8n-playwright-vnc-docker

## Tasks

- [x] 1. 共有インフラと環境設定の構築
  - .env_sample をベースに、Task Runner 分離構成に必要な環境変数を定義
  - Redis サービスの構成を確認し、タスクキュー用の接続設定を最適化
  - 永続化ボリューム（n8n_data, playwright_data）の定義と権限設定を整理
  - _Requirements: 1.1, 1.3, 1.4_

- [x] 2. n8n-main コンテナの構成と最適化 (P)
  - 公式 n8nio/n8n イメージを使用した n8n-main サービスの定義
  - 外部タスクランナー（External Mode）を利用するための環境変数を設定
  - Redis をタスクブローカーとして使用するための通信設定を実装
  - _Requirements: 1.1, 2.1, 2.2_

- [x] 3. n8n-taskrunner カスタムイメージの作成
- [x] 3.1 Playwright ベースの Task Runner Dockerfile の構築
  - mcr.microsoft.com/playwright:v1.40.0-jammy をベースにした Dockerfile の作成
  - Node.js 22.x および n8n パッケージのインストール
  - Xvfb、fluxbox、x11vnc などの GUI 実行環境のセットアップ
  - _Requirements: 1.2, 2.3, 3.1, 4.1_

- [x] 3.2 起動スクリプト (start.sh) の実装とプロセス制御
  - 仮想ディスプレイ（DISPLAY=:99）の初期化と各 GUI プロセスのバックグラウンド起動
  - VNC サーバー（x11vnc）のパスワード保護とポート公開設定
  - dumb-init を介した n8n worker メインプロセスのライフサイクル管理
  - _Requirements: 3.2, 4.1, 4.3_

- [x] 4. サービス間の統合と連携テスト
- [x] 4.1 (P) ネットワークおよびサービス間通信の検証
  - n8n-main と n8n-taskrunner 間の WebSocket 接続の安定性確認 (Redis/Bull)
  - Redis を介したタスクの受け渡しとキュー処理の正常動作確認
  - _Requirements: 2.2, 2.4_

- [x] 4.2 Playwright & VNC 統合動作の最終検証
  - VNC サーバー（5900ポート）の起動と待機状態を確認
  - n8n-taskrunner 内で Playwright が正常にロード可能であることを確認
  - _Requirements: 3.2, 3.3, 4.2, 4.3_

- [ ] 5. 追加の品質検証テスト
  - 異常系テスト：タスクランナー停止時の再起動およびタスク再試行の挙動確認
  - リソース監視：Playwright 実行時のメモリ消費量と N8N_RUNNERS_MAX_OLD_SPACE_SIZE の整合性確認
  - _Requirements: 2.4_
