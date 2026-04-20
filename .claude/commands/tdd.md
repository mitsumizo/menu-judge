---
description: テスト駆動開発ワークフローを実行。インターフェースを定義し、テストを最初に生成し、最小限のコードを実装。80%以上のカバレッジを確保。
---

# /tdd コマンド

このコマンドは**tdd-guide**エージェントを呼び出し、テスト駆動開発の方法論を徹底します。

## このコマンドの機能

1. **インターフェースの定義** - 型/インターフェースを最初に定義
2. **テストを最初に生成** - 失敗するテストを書く（RED）
3. **最小限のコードを実装** - パスするために必要なだけ書く（GREEN）
4. **リファクタリング** - テストをグリーンに保ちながらコードを改善（REFACTOR）
5. **カバレッジの検証** - 80%以上のテストカバレッジを確保

## 使用するタイミング

`/tdd`を使用するのは：
- 新しい機能を実装するとき
- 新しい関数/コンポーネントを追加するとき
- バグを修正するとき（まずバグを再現するテストを書く）
- 既存のコードをリファクタリングするとき
- 重要なビジネスロジックを構築するとき

## TDDサイクル

```
RED → GREEN → REFACTOR → REPEAT

RED:      失敗するテストを書く
GREEN:    パスする最小限のコードを書く
REFACTOR: コードを改善、テストをパスさせ続ける
REPEAT:   次の機能/シナリオ
```

## 使用例

```
User: /tdd メニュー画像から料理を解析する関数が必要

Agent (tdd-guide):
# TDDセッション: メニュー画像解析

## ステップ1: インターフェースの定義（SCAFFOLD）

```python
# app/models/dish.py
from dataclasses import dataclass
from typing import Optional

@dataclass
class Dish:
    original_name: str
    japanese_name: str
    description: str
    spiciness: int  # 1-5
    sweetness: int  # 1-5
    ingredients: list[str]
    allergens: list[str]
    category: str
```

## ステップ2: 失敗するテストを書く（RED）

```python
# tests/test_services.py
import pytest
from app.services.ai import ClaudeProvider

class TestClaudeProvider:
    def test_analyze_menu_returns_dishes(self, mocker):
        """有効な画像から料理リストを返す"""
        # モックレスポンス
        mock_response = {
            "dishes": [{
                "original_name": "Pad Thai",
                "japanese_name": "パッタイ",
                "description": "タイ風焼きそば",
                "spiciness": 2,
                "sweetness": 3,
                "ingredients": ["米麺", "エビ", "卵"],
                "allergens": ["甲殻類", "卵"],
                "category": "main"
            }]
        }
        mocker.patch.object(
            ClaudeProvider,
            '_call_api',
            return_value=mock_response
        )

        provider = ClaudeProvider(api_key="test-key")
        result = provider.analyze_menu(b"image_bytes")

        assert result.success is True
        assert len(result.dishes) == 1
        assert result.dishes[0].original_name == "Pad Thai"

    def test_analyze_menu_handles_empty_response(self, mocker):
        """空のレスポンスを適切に処理する"""
        mocker.patch.object(
            ClaudeProvider,
            '_call_api',
            return_value={"dishes": []}
        )

        provider = ClaudeProvider(api_key="test-key")
        result = provider.analyze_menu(b"image_bytes")

        assert result.success is True
        assert result.dishes == []

    def test_analyze_menu_handles_api_error(self, mocker):
        """APIエラーを適切に処理する"""
        mocker.patch.object(
            ClaudeProvider,
            '_call_api',
            side_effect=Exception("API Error")
        )

        provider = ClaudeProvider(api_key="test-key")
        result = provider.analyze_menu(b"image_bytes")

        assert result.success is False
        assert "API Error" in result.error
```

## ステップ3: テスト実行 - 失敗を確認

```bash
pytest tests/test_services.py -v

FAILED tests/test_services.py::TestClaudeProvider::test_analyze_menu_returns_dishes
    ModuleNotFoundError: No module named 'app.services.ai'
```

✅ テストは期待通り失敗。実装を開始。

## ステップ4: 最小限の実装（GREEN）

```python
# app/services/ai/claude_provider.py
from dataclasses import dataclass
from typing import Optional
import anthropic

@dataclass
class AnalysisResult:
    success: bool
    dishes: list = None
    error: Optional[str] = None
    provider: str = "claude"

class ClaudeProvider:
    def __init__(self, api_key: str):
        self.api_key = api_key

    def analyze_menu(self, image_data: bytes) -> AnalysisResult:
        try:
            response = self._call_api(image_data)
            dishes = [Dish(**d) for d in response.get("dishes", [])]
            return AnalysisResult(success=True, dishes=dishes)
        except Exception as e:
            return AnalysisResult(success=False, error=str(e))

    def _call_api(self, image_data: bytes) -> dict:
        # 実際のAPI呼び出し実装
        pass
```

## ステップ5: テスト実行 - 成功を確認

```bash
pytest tests/test_services.py -v

PASSED tests/test_services.py::TestClaudeProvider::test_analyze_menu_returns_dishes
PASSED tests/test_services.py::TestClaudeProvider::test_analyze_menu_handles_empty_response
PASSED tests/test_services.py::TestClaudeProvider::test_analyze_menu_handles_api_error
```

✅ すべてのテストがパス！
```

## TDDベストプラクティス

**DO:**
- ✅ 実装の前にテストを書く
- ✅ 各変更後にテストを実行して失敗/成功を確認
- ✅ テストをパスさせる最小限のコードを書く
- ✅ テストがグリーンになった後にのみリファクタリング
- ✅ エッジケースとエラーシナリオを追加
- ✅ 80%以上のカバレッジを目指す（重要なコードは100%）

**DON'T:**
- ❌ テストの前に実装を書く
- ❌ 各変更後のテスト実行をスキップ
- ❌ 一度に多くのコードを書く
- ❌ 失敗するテストを無視する
- ❌ 実装の詳細をテストする（振る舞いをテスト）

## カバレッジ要件

- **80%最低** - すべてのコード
- **100%必須**:
  - AI解析ロジック
  - 入力バリデーション
  - エラーハンドリング
  - セキュリティ関連コード

## 他のコマンドとの統合

- `/plan`を使用して何を構築するか理解
- `/tdd`を使用してテストで実装
- `/build-fix`を使用してビルドエラーが発生した場合
- `/code-review`を使用して実装をレビュー
