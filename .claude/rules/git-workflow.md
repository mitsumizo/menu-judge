# Git ワークフロー

## コミットメッセージ形式

```
<type>: <description>

<optional body>
```

タイプ: feat, fix, refactor, docs, test, chore, perf, ci

例：
- `feat: メニュー画像解析機能を追加`
- `fix: APIキーバリデーションのエラーを修正`
- `refactor: AIプロバイダーの抽象化を改善`
- `docs: README.mdを更新`
- `test: ClaudeProviderの単体テストを追加`

## ブランチ戦略

- `main`: 本番リリース用
- `develop`: 開発用
- `feature/*`: 機能開発
- `fix/*`: バグ修正

## プルリクエストワークフロー

PRを作成する際：
1. 全コミット履歴を分析（最新コミットだけでなく）
2. `git diff [base-branch]...HEAD`ですべての変更を確認
3. 包括的なPRサマリーを作成
4. TODOを含むテストプランを含める
5. 新しいブランチの場合は`-u`フラグでプッシュ

## 機能実装ワークフロー

### 1. まず計画
- **planner**エージェントを使用して実装計画を作成
- 依存関係とリスクを特定
- フェーズに分解

### 2. TDDアプローチ
- **tdd-guide**エージェントを使用
- テストを最初に書く（RED）
- テストをパスさせる実装（GREEN）
- リファクタリング（IMPROVE）
- 80%以上のカバレッジを検証

### 3. コードレビュー
- コードを書いた直後に**code-reviewer**エージェントを使用
- CRITICALとHIGHの問題に対処
- 可能であればMEDIUMの問題も修正

### 4. コミット＆プッシュ
- 詳細なコミットメッセージ
- 従来のコミット形式に従う

## コミット前チェックリスト

- [ ] すべてのテストがパス: `pytest`
- [ ] リントがパス: `flake8 app/`
- [ ] 型チェックがパス: `mypy app/`
- [ ] セキュリティチェック: `/security-check`
- [ ] コードレビュー: `/code-review`

## よくあるGitコマンド

```bash
# ステータス確認
git status

# 変更の確認
git diff

# ステージング
git add <file>
git add -A  # すべての変更

# コミット
git commit -m "feat: 機能説明"

# プッシュ
git push origin <branch>

# ブランチ作成
git checkout -b feature/new-feature

# マージ
git merge develop

# リベース（注意して使用）
git rebase main
```

## 禁止事項

- mainブランチへの直接コミット
- 強制プッシュ（`--force`）を本番ブランチへ
- シークレットをコミット
- ビルドが壊れた状態でプッシュ
