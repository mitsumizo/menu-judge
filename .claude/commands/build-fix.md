---
description: Pythonのシンタックスエラーとビルドエラーを段階的に修正
---

# /build-fix コマンド

Pythonのシンタックスエラーとビルドエラーを段階的に修正します。

## 動作手順

1. ビルド/チェックを実行:
   ```bash
   python -m py_compile app/**/*.py
   # または
   python -m pytest --collect-only
   # または
   flask run --debug
   ```

2. エラー出力を解析:
   - ファイル別にグループ化
   - 重要度順にソート

3. 各エラーについて:
   - エラーのコンテキストを表示（前後5行）
   - 問題を説明
   - 修正を提案
   - 修正を適用
   - ビルドを再実行
   - エラーが解決されたことを確認

4. 停止条件:
   - 修正が新しいエラーを導入した場合
   - 3回試行後も同じエラーが続く場合
   - ユーザーが一時停止を要求した場合

5. サマリーを表示:
   - 修正されたエラー
   - 残りのエラー
   - 新しく導入されたエラー

安全のために一度に1つのエラーを修正！

## 使用例

```
User: /build-fix

Agent:
# ビルドエラー修正セッション

## ビルドを実行中...

```bash
python -m py_compile app/services/ai/claude_provider.py
```

## エラー検出: 2件

### エラー1: SyntaxError
**ファイル**: app/services/ai/claude_provider.py:25
**エラー**: unexpected indent

**コンテキスト**:
```python
23:     def analyze_menu(self, image_data: bytes):
24:         try:
25:             response = self._call_api(image_data)
26:               dishes = self._parse_response(response)  # ← インデントエラー
27:             return AnalysisResult(success=True, dishes=dishes)
```

**問題**: 26行目のインデントが不正
**修正**: インデントを調整

**適用中...**

### 再ビルド...

```bash
python -m py_compile app/services/ai/claude_provider.py
```

✅ エラー1が解決されました

### エラー2: ImportError
**ファイル**: app/services/ai/__init__.py:3
**エラー**: cannot import name 'GeminiProvider' from 'app.services.ai.gemini_provider'

**コンテキスト**:
```python
1: from .base import AIProvider
2: from .claude_provider import ClaudeProvider
3: from .gemini_provider import GeminiProvider  # ← 存在しないモジュール
```

**問題**: gemini_providerモジュールがまだ実装されていない
**修正**: インポートをコメントアウト（または実装）

**適用中...**

### 再ビルド...

✅ エラー2が解決されました

---

## サマリー

- **修正されたエラー**: 2
- **残りのエラー**: 0
- **新しいエラー**: 0

✅ ビルド成功！
```

## Python固有のチェック

```bash
# シンタックスチェック
python -m py_compile app/**/*.py

# 型チェック（mypyがインストールされている場合）
mypy app/

# Lintチェック
flake8 app/

# テストの収集（実行なし）
pytest --collect-only
```

## よくあるPythonエラー

### IndentationError
```python
# ❌ 悪い例
def func():
    if True:
      return 1  # タブとスペースの混在

# ✅ 良い例
def func():
    if True:
        return 1  # 一貫したインデント
```

### ImportError
```python
# ❌ 悪い例
from app.services import NonExistentModule

# ✅ 良い例
try:
    from app.services import OptionalModule
except ImportError:
    OptionalModule = None
```

### TypeError
```python
# ❌ 悪い例
def greet(name):
    return "Hello, " + name

greet(123)  # TypeError: can only concatenate str

# ✅ 良い例
def greet(name: str) -> str:
    return f"Hello, {name}"
```

## 他のコマンドとの統合

- `/plan`を使用して実装を計画
- `/tdd`を使用してテストで実装
- `/build-fix`を使用してビルドエラーを修正（このコマンド）
- `/code-review`を使用して実装をレビュー
