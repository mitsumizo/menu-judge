Issue #$ARGUMENTSをGit Worktreeを使って実装してください。

## 実装手順

### 1. 前処理（Worktree作成前）
- 現在のブランチがmain以外の場合は、mainブランチにチェックアウトしてください
- `git checkout main && git pull origin main`で最新のmainブランチを取得してください
- 既存のブランチ`feature/issue-$ARGUMENTS`があれば削除してください

### 2. Worktree作成
- `git worktree add issue-$ARGUMENTS -b feature/issue-$ARGUMENTS`コマンドでWorktreeを作成してください
- Worktreeは`issue-$ARGUMENTS`という命名規則に従ったサブフォルダを作成します

### 3. Worktree環境の設定
- 作成したサブディレクトリ`issue-$ARGUMENTS`に移動してください
- `npx husky install`を実行してHuskyのパスを設定してください
- 必要に応じて`npm install`で依存関係をインストールしてください

### 4. 実装
- Issue内容を確認し、最適なサブエージェントを選択して実装してください
- 実装完了後、必ずテストを実行してください
- `npm run lint`と`npm run typecheck`でコード品質を確認してください

### 5. プルリクエスト作成
- 変更をコミットし、リモートにプッシュしてください
- `gh pr create`コマンドでプルリクエストを作成してください
- PRタイトルは「feat: Issue #$ARGUMENTS [Issue内容の要約]」形式にしてください
