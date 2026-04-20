---
description: コミットされていない変更のセキュリティと品質をレビュー。CRITICALまたはHIGHの問題がある場合はコミットをブロック。
---

# /code-review コマンド

このコマンドは**code-reviewer**エージェントを呼び出し、コードの品質とセキュリティを包括的にレビューします。

## このコマンドの機能

1. 変更されたファイルを取得: `git diff --name-only HEAD`
2. 各変更ファイルについてチェック

## チェック項目

### セキュリティ問題（CRITICAL）
- ハードコードされた認証情報、APIキー、トークン
- SQLインジェクション脆弱性
- XSS脆弱性
- 入力バリデーションの欠如
- 安全でない依存関係
- パストラバーサルリスク

### コード品質（HIGH）
- 関数 > 50行
- ファイル > 800行
- ネスト深さ > 4レベル
- エラーハンドリングの欠如
- print文（デバッグ用）
- TODO/FIXMEコメント
- 公開APIのdocstring欠如

### ベストプラクティス（MEDIUM）
- ミューテーションパターン（代わりにイミュータブルを使用）
- 新規コードのテスト不足
- 型ヒントの欠如

## レポート生成

各問題について：
- 重要度: CRITICAL, HIGH, MEDIUM, LOW
- ファイル位置と行番号
- 問題の説明
- 推奨される修正

## 承認基準

- ✅ 承認: CRITICALまたはHIGHの問題なし
- ⚠️ 警告: MEDIUMの問題のみ
- ❌ ブロック: CRITICALまたはHIGHの問題

セキュリティ脆弱性のあるコードは絶対に承認しない！

## 使用例

```
User: /code-review

Agent (code-reviewer):
# コードレビューレポート

## 概要
- **変更ファイル数**: 3
- **CRITICALの問題**: 1
- **HIGHの問題**: 2
- **MEDIUMの問題**: 3

## ❌ CRITICALな問題（必ず修正）

### 1. ハードコードされたAPIキー
**ファイル**: app/services/ai/claude_provider.py:15
**問題**: APIキーがソースコードに直接書かれている

```python
# ❌ 悪い例
api_key = "sk-ant-api03-xxxxx"

# ✅ 良い例
api_key = request.headers.get('X-API-Key')
if not api_key:
    return {"error": "API key required"}, 401
```

## ⚠️ HIGHの問題（修正すべき）

### 2. 入力バリデーションの欠如
**ファイル**: app/routes/menu.py:42
**問題**: ファイルアップロードのバリデーションがない

```python
# ❌ 悪い例
file = request.files['image']
file.save(os.path.join(UPLOAD_FOLDER, file.filename))

# ✅ 良い例
from werkzeug.utils import secure_filename

file = request.files.get('image')
if not file or not allowed_file(file.filename):
    return {"error": "Invalid file"}, 400
filename = secure_filename(file.filename)
```

### 3. エラーハンドリングの欠如
**ファイル**: app/services/ai/claude_provider.py:30
**問題**: API呼び出しがtry-exceptでラップされていない

## 💡 MEDIUMの問題（改善を検討）

### 4. 型ヒントの欠如
**ファイル**: app/services/ai/claude_provider.py:25
**問題**: 関数に型ヒントがない

### 5. docstringの欠如
**ファイル**: app/routes/menu.py:35
**問題**: 公開APIにdocstringがない

---

**結果**: ❌ ブロック
CRITICALとHIGHの問題を修正してから再度レビューしてください。
```

## 他のコマンドとの統合

- `/plan`を使用して何を構築するか計画
- `/tdd`を使用してテストで実装
- `/code-review`を使用して実装をレビュー（このコマンド）
- `/build-fix`を使用してビルドエラーを修正
