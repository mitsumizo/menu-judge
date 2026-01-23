# テスト要件

## 最低テストカバレッジ: 80%

テストタイプ（すべて必須）：
1. **単体テスト** - 個々の関数、ユーティリティ
2. **統合テスト** - APIエンドポイント、外部サービス連携
3. **E2Eテスト** - 重要なユーザーフロー（将来）

## テスト駆動開発

必須ワークフロー：
1. テストを最初に書く（RED）
2. テストを実行 - 失敗するはず
3. 最小限の実装を書く（GREEN）
4. テストを実行 - パスするはず
5. リファクタリング（IMPROVE）
6. カバレッジを検証（80%以上）

## テストの構造

```
tests/
├── __init__.py
├── conftest.py          # 共通のフィクスチャ
├── fixtures/            # テスト用データ
│   └── sample_menu.jpg
├── test_routes.py       # APIエンドポイントのテスト
├── test_services.py     # サービス層のテスト
└── test_models.py       # モデルのテスト
```

## フィクスチャの使用

```python
# conftest.py
import pytest
from app import create_app

@pytest.fixture
def app():
    """テスト用アプリケーションインスタンス"""
    app = create_app('testing')
    yield app

@pytest.fixture
def client(app):
    """テストクライアント"""
    return app.test_client()

@pytest.fixture
def sample_image():
    """テスト用画像データ"""
    with open('tests/fixtures/sample_menu.jpg', 'rb') as f:
        return f.read()
```

## モックの使用

```python
from unittest.mock import Mock, patch

class TestClaudeProvider:
    @patch('app.services.ai.claude_provider.anthropic.Anthropic')
    def test_analyze_menu_success(self, mock_anthropic):
        """APIが正常に呼び出されることを確認"""
        mock_client = Mock()
        mock_anthropic.return_value = mock_client
        mock_client.messages.create.return_value = Mock(
            content=[Mock(text='{"dishes": [{"name": "Test"}]}')]
        )

        provider = ClaudeProvider(api_key="test")
        result = provider.analyze_menu(b"image_data")

        assert result.success is True
        mock_client.messages.create.assert_called_once()
```

## テスト実行

```bash
# すべてのテストを実行
pytest

# カバレッジ付き
pytest --cov=app --cov-report=html

# 特定のテストのみ
pytest tests/test_services.py -v

# 失敗したテストのみ再実行
pytest --lf

# ウォッチモード（pytest-watchを使用）
ptw
```

## テスト失敗のトラブルシューティング

1. **tdd-guide**エージェントを使用
2. テストの分離を確認
3. モックが正しいか検証
4. テストではなく実装を修正（テストが間違っていない限り）

## カバレッジ要件

- **80%最低** - すべてのコード
- **100%必須**:
  - AI解析ロジック
  - 入力バリデーション
  - エラーハンドリング
  - セキュリティ関連コード

## エージェントサポート

- **tdd-guide** - 新機能には積極的に使用、テストファーストを徹底
