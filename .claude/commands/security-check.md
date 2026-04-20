---
description: セキュリティ脆弱性の包括的なスキャンを実行。OWASP Top 10、シークレット、依存関係の脆弱性をチェック。
---

# /security-check コマンド

このコマンドは**security-reviewer**エージェントを呼び出し、セキュリティの包括的なスキャンを実行します。

## このコマンドの機能

1. **シークレットスキャン** - ハードコードされたAPIキー、パスワード、トークンを検出
2. **依存関係チェック** - 脆弱なパッケージを特定
3. **コードスキャン** - OWASP Top 10脆弱性をチェック
4. **設定レビュー** - セキュリティ設定を検証

## 実行されるチェック

```bash
# シークレットのスキャン
grep -r "api_key\|password\|secret\|token" --include="*.py" .

# 依存関係の脆弱性チェック
pip-audit
# または
safety check

# Pythonセキュリティスキャン
bandit -r app/

# .envファイルのチェック
cat .env.example  # 実際のシークレットがないことを確認
```

## チェック項目

### シークレット検出（CRITICAL）
- APIキー（`sk-`, `api_key`, `apikey`）
- パスワード（`password`, `passwd`, `pwd`）
- トークン（`token`, `bearer`, `jwt`）
- データベース接続文字列

### OWASP Top 10
1. インジェクション（SQL, Command, Path）
2. 認証の破綻
3. 機密データの露出
4. アクセス制御の破綻
5. セキュリティの設定ミス
6. XSS（クロスサイトスクリプティング）
7. 既知の脆弱性を持つコンポーネント

### Menu-Judge固有
- 画像アップロードのバリデーション
- APIキーのクライアント側管理
- AI APIレスポンスのサニタイズ
- CORSとCSRF設定

## 使用例

```
User: /security-check

Agent (security-reviewer):
# セキュリティスキャンレポート

## 概要
- **CRITICALの問題**: 0
- **HIGHの問題**: 1
- **MEDIUMの問題**: 2
- **LOWの問題**: 1

## リスクレベル: 🟡 MEDIUM

---

## ⚠️ HIGHの問題

### 1. 依存関係の脆弱性
**パッケージ**: Werkzeug 2.0.0
**CVE**: CVE-2023-XXXXX
**説明**: パストラバーサルの脆弱性

**修正**:
```bash
pip install --upgrade Werkzeug>=2.3.0
```

---

## 💡 MEDIUMの問題

### 2. デバッグモードが有効
**ファイル**: run.py:10
**問題**: 本番環境でデバッグモードが有効になる可能性

```python
# ❌ 悪い例
app.run(debug=True)

# ✅ 良い例
app.run(debug=os.getenv('FLASK_DEBUG', 'false').lower() == 'true')
```

### 3. レート制限の欠如
**ファイル**: app/routes/menu.py
**問題**: /api/analyzeエンドポイントにレート制限がない

**推奨**:
```python
from flask_limiter import Limiter

limiter = Limiter(key_func=get_remote_address)

@app.route('/api/analyze', methods=['POST'])
@limiter.limit("10 per minute")
def analyze():
    ...
```

---

## ✅ パスしたチェック

- [x] ハードコードされたシークレットなし
- [x] 入力バリデーションあり
- [x] XSS対策（Jinja2のautoescapeが有効）
- [x] CSRF保護
- [x] 適切なエラーハンドリング

---

## 推奨アクション

1. **即座に**: Werkzeugをアップグレード
2. **今週中に**: レート制限を実装
3. **将来的に**: Content-Security-Policyヘッダーを追加
```

## 他のコマンドとの統合

- `/code-review`と組み合わせて包括的なレビュー
- コミット前に`/security-check`を実行
- CI/CDパイプラインに統合
