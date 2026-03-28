# Research & Design Decisions: n8n-playwright-vnc-docker

## Summary
- **Feature**: n8n-playwright-vnc-docker
- **Discovery Scope**: Extension / Refactoring (Service Integration)
- **Key Findings**:
  - `Dockerfile.taskrunner` の構成が最も要件に近く、これをベースイメージとして採用することで構築を簡素化可能。
  - VNCとn8nを同一コンテナで動かす際、環境変数 `DISPLAY=:99` の共有が不可欠。
  - PlaywrightのHeadedモード実行には Xvfb が必須であり、`start.sh` によるライフサイクル管理が重要。

## Research Log

### Node.js 22.x on Playwright Jammy
- **Context**: n8nの動作に必要なNode.jsバージョンの確認。
- **Findings**: `mcr.microsoft.com/playwright:v1.40.0-jammy` は Ubuntu 22.04 ベースであり、NodeSource経由で Node.js 22.x をインストール可能。
- **Implications**: `Dockerfile` 内でのインストール手順を統一し、n8nの最新機能をサポートする。

### Single Container Process Management
- **Context**: 複数のプロセス（n8n, Xvfb, VNC）を1つのコンテナで安定稼働させる方法。
- **Findings**: `dumb-init` をエントリポイントとし、`start.sh` 内でバックグラウンド実行を制御する手法が一般的。
- **Implications**: 既存の `start.sh` を拡張し、n8nの起動も管理下に置く。

## Architecture Pattern Evaluation

| Option | Description | Strengths | Risks / Limitations | Notes |
|--------|-------------|-----------|---------------------|-------|
| Unified Container | n8n, Playwright, VNCを1つに統合 | 最小構成、リソース効率高 | コンテナが肥大化、プロセス管理が複雑 | 本プロジェクトの「最小限」要件に合致 |
| Multi-Container (Current) | 各サービスを分離 | 責務が明確、スケーラビリティ高 | ネットワーク設定が複雑、オーバーヘッド大 | 現状の構成 |

## Design Decisions

### Decision: 統合コンテナ（Unified Container）への移行
- **Context**: 最小限の構成で運用したいという要件（1.1）。
- **Selected Approach**: `Dockerfile.taskrunner` をベースに `n8n` 本体と VNC 環境を統合した単一イメージを作成。
- **Rationale**: サービスの依存関係（特に Playwright と GUI 環境の密結合）を解決しやすく、デプロイが容易。
- **Trade-offs**: コンテナイメージのサイズは大きくなるが、全体のコンテナ数は減少する。

### Decision: Redisの存続
- **Context**: キュー管理の安定性。
- **Selected Approach**: Redisは個別のコンテナとして維持。
- **Rationale**: ステアリングに Bull キューの利用が明記されており、データ永続化とスケーラビリティの観点から分離が望ましい。

## Risks & Mitigations
- プロセス死活監視の欠如 — `dumb-init` と `start.sh` 内での適切なシグナル処理で対応。
- メモリ不足 — `NODE_OPTIONS` によるヒープサイズの制限。
