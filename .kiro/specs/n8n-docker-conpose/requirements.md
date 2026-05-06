# Requirements Document

## Introduction
このドキュメントは、n8n、Playwright、およびVNCを統合した最小限のDocker構成を構築するための要件を定義します。このシステムは、GUIベースのブラウザ操作を含む高度なワークフロー自動化を実現することを目的としています。

## Requirements

### Requirement 1: 最小限のDocker環境の構成
**Objective:** 開発者として、必要最小限のサービス構成でDocker環境を構築したい。これにより、リソース消費を抑えつつ保守性を向上させることができる。

#### Acceptance Criteria
1. The Docker Compose system shall include n8n, Playwright, and VNC services as the core components.
2. The system shall use a single-stage Docker build to ensure a simple and maintainable container structure.
3. The system shall manage configuration and secrets through a `.env` file to separate environment settings from the code.
4. The system shall store persistent data for n8n and Playwright in dedicated Docker volumes.

### Requirement 2: n8n ワークフローエンジンの統合
**Objective:** 自動化担当者として、n8nを利用してワークフローを実行したい。これにより、複雑なタスクの自動化が可能になる。

#### Acceptance Criteria
1. The n8n service shall be accessible via a web browser at a configured port (default 5678).
2. The n8n service shall support integration with Playwright for browser automation tasks.
3. The n8n service shall be configured with Node.js 22.x or higher to support modern JavaScript features.
4. If the n8n service fails to start, then the Docker system shall attempt to restart it automatically.

### Requirement 3: Playwright によるブラウザ操作の自動化
**Objective:** 自動化担当者として、Playwrightを使用してブラウザ操作を自動化したい。これにより、GUIベースのWebサイト操作が可能になる。

#### Acceptance Criteria
1. While executing a workflow, the system shall provide Playwright version 1.40.0-jammy or compatible for browser automation.
2. The Playwright environment shall support headless and headed execution modes.
3. When requested by a workflow, the Playwright service shall capture screenshots or videos of the browser session.

### Requirement 4: VNC による GUI 操作の可視化
**Objective:** 開発者として、VNCを介してコンテナ内のブラウザ操作をリアルタイムで確認したい。これにより、デバッグや動作確認が容易になる。

#### Acceptance Criteria
1. The system shall provide a VNC interface (using Xvfb, fluxbox, and x11vnc) to visualize browser operations.
2. The VNC service shall be accessible via a standard VNC client or a web-based VNC viewer.
3. When the Playwright browser is running in headed mode, the VNC service shall display the browser window in real-time.
