# Gap Analysis: n8n-docker-compose

## 分析サマリー

- **対象プロジェクト**: n8n-playwright-vnc-docker (n8n-docker-compose)
- **分析日付**: 2026-05-03
- **分析者**: Claude Code (Kiro-style SDD)
- **フェーズ**: implementation-complete (事後検証)

### 発見事項

- ✅ **アーキテクチャ**: External Task Runnerパターンが適切に実装済み（n8n + Task Runner + Redis + VNCの4サービス構成）
- ✅ **Task Runner通信**: WebSocket直接接続（Redis経由なし）でn8n Brokerに接続する設計是正确的
- ✅ **環境変数**: `N8N_RUNNERS_MODE=external` によりv2.xでは自動検出される（`N8N_RUNNERS_ENABLED` 不要）
- ⚠️ **[Bug] `.env` ファイルのURI不正**: `ws://n8n-main:5679` → `ws://n8n:5679` に修正必要
- ⚠️ **`.env` Git管理状態**: `.gitignore` で除外されているがコミット済み（実際の運用に影響なし）

---

## 1. 現状調査

### 1.1 コードベース構造

| コンポーネント | パス | 責務 |
|--------------|------|------|
| n8n メインサービス | `docker-compose.yml#n8n` | ワークフロー管理、UI、Task Broker (port 5679) |
| n8n-task-runner | `docker-compose.yml#n8n-task-runner` + `Dockerfile.taskrunner` + `start.sh` | Codeノード実行、Playwright制御、GUI表示 |
| Redis | `docker-compose.yml#redis` + `redis.conf` | QueueモードのBullキュー永続化（AOF有効） |
| VNC | `docker-compose.yml#vnc` + `Dockerfile.vnc` | Xvfb + Fluxbox + x11vnc によるGUI可視化 |

### 1.2 既存パターンと制約

**確認されたパターン**:
- 单一Stage Docker Build（build time短縮）
- dumb-init + start.sh によるプロセスマネジメント
- 外部名前付きボリューム（`n8n-docker-compose_*`）による永続化
- UID/GID 1000:1000 の非特権ユーザー実行

**統合インターフェース**:
- n8n ↔ Task Runner: WebSocket (`ws://n8n:5679`)
- n8n ↔ Redis: TCP (port 6379, TLS無効)
- Task Runner ↔ Playwright MCP: localhost:8931

---

## 2. 要件実現可能性分析

### 2.1 requirements.md との突合

| 要件ID | 内容 | 実装状態 | ギャップ |
|--------|------|----------|----------|
| 1.1 | n8n, Playwright, VNC 3service構成 | ✅ 4service構成（redis追加） | なし |
| 1.2 | シングルステージDockerビルド | ✅ 実装済み | なし |
| 1.3 | .env による設定管理 | ✅ 実装済み | なし |
| 1.4 | Docker volume による永続化 | ✅ 外部名前付きボリューム | なし |
| 2.1 | n8n Webアクセス (port 5678) | ✅ 実装済み | なし |
| 2.2 | n8n-Playwright連携 | ✅ WebSocket接続確認済み | なし |
| 2.3 | Node.js 22.x | ✅ Dockerfile.taskrunner でセットアップ | なし |
| 2.4 | 自動再起動 | ✅ `restart: unless-stopped` | なし |
| 3.1 | Playwright v1.40.0+ | ✅ v1.51.1-jammy 使用 | なし |
| 3.2 | Headless/Headed実行 | ✅ Xvfb + DISPLAY=:99 | なし |
| 3.3 | スクリーンキャプチャ | ✅ Playwright API で実現 | なし |
| 4.1 | VNC可視化 | ✅ x11vnc port 5900 | なし |
| 4.2 | VNCクライアント/Webビューア | ✅ port 5900 公開 | なし |
| 4.3 | リアルタイムブラウザ表示 | ✅ x11vnc + Fluxbox | なし |

### 2.2 特定されたギャップ

#### Gap #1: `.env` ファイルの `N8N_RUNNERS_TASK_BROKER_URI` 不正 [高]

**場所**: `.env:40`
```env
N8N_RUNNERS_TASK_BROKER_URI=ws://n8n-main:5679  # ❌ 誤
```

**問題**:
- Docker Composeサービスの名前は `n8n`
- `n8n-main` というホスト名は存在しない
- `.env_sample:40` では正しく `ws://n8n:5679` が設定されている

**影響**:
- `.env` を直接使用した場合、Task Runnerがn8nメインサービスに接続できない
- ただし `.env_sample` をコピーして使用する場合は問題なし

**修正方針**:
```env
N8N_RUNNERS_TASK_BROKER_URI=ws://n8n:5679  # ✅ 正
```

#### Gap #2: `.env` ファイルのGit管理状態 [中]

**問題**:
- `.gitignore` で `.env` が除外指定されているが、実際にはコミットされている
- `git status` が clean でも `.env` の内容が不正

**影響**:
- リポジトリをクローンした開発者が `.env_sample` を `.env` にコピーすれば正常動作
- ただし既存の `.env` コミットが不正な状態を維持している

---

## 3. 実装アプローチオプション

### Option A: 現状維持（Minimal Fix）

**適用場面**: `.env` がgitignoreされ、実際には `.env_sample` から生成される前提

**取るべきアクション**:
- `.env` ファイルを削除し、git管理から除外を継続
- `.env_sample` のドキュメントで「コピーして使用」と明記

**Trade-offs**:
- ✅ 追加コード不要
- ✅ `.env_sample` が正しければ運用に問題なし
- ❌ `.env` が不正な状態でリポジトリに存在し続ける

### Option B: `.env` を修正してgit管理に戻す

**取るべきアクション**:
- `.env` の `n8n-main` を `n8n` に修正
- `.gitignore` から `.env` を移除

**Trade-offs**:
- ✅ 不正なファイルがリポジトリになくなる
- ❌ 機密情報（`N8N_ENCRYPTION_KEY`）がリポジトリに含むリスク
- ❌ `.gitignore` の意図と矛盾

### Option C: Hybrid（推奨）

**取るべきアクション**:
1. `.env` を削除（git管理から完全排除）
2. `.gitignore` を維持
3. `.env_sample` のコメントを強化：「必ずコピーして使用のこと」

**Trade-offs**:
- ✅ セキュリティと運用の両立
- ✅ `.env_sample` が唯一の正解となる
- ❌ `.env` の過去のコミット履歴は残存

---

## 4. 実装複雑度とリスク

### Effort: **S** (1-3日)

**理由**:
- 修正は `.env` ファイルの一行のみ
- 既存のテスト（test_env_config.py）で検証可能
- docker-compose の動作確認のみ

### Risk: **Low**

**理由**:
- `.env_sample` が既に正しい値を提供
- テストインフラが存在する
- コンテナ構成は正常に動作している

---

## 5. 設計に向けた推奨事項

### 5.1 優先アクション

| 優先度 | アクション | 担当 |
|--------|----------|------|
| P0 | `.env` ファイルを削除し、gitignore を維持 | Developer |
| P1 | `.env_sample:40` のコメントに「必須項目」と明記 | Documentation |

### 5.2 Research Needed（設計フェーズ）

なし - 現在の実装は仕様と合致しており、研究は不要

### 5.3 アーキテクチャ確認

**Task Runner WebSocket接続** ✅ 正しい実装:
```
n8n-task-runner --ws://n8n:5679--> n8n (Broker port 5679)
```

**Redis Queue接続** ✅ 正しい実装:
```
n8n --TCP 6379--> Redis (Queueストレージのみ、Task Runnerは直接接続しない)
```

---

## 6. 結論

**実装状況**: 要件に対して適切に実装済み

**唯一のバグ**: `.env` ファイルの `N8N_RUNNERS_TASK_BROKER_URI=ws://n8n-main:5679` が不正（`n8n` が正しい）

**推奨**: Option C（`.env` 削除 + `.gitignore` 維持）を実施し、`.env_sample` を唯一のテンプレートとして運用

---

## 7. 参照

- 要件: `.kiro/specs/n8n-docker-conpose/requirements.md`
- 設計: `.kiro/specs/n8n-docker-conpose/design.md`
- Research: `.kiro/specs/n8n-docker-conpose/research.md`
- タスク: `.kiro/specs/n8n-docker-conpose/tasks.md`
- Gap Analysis Framework: `.kiro/settings/rules/gap-analysis.md`