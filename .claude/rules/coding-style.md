# コーディングスタイル

## Python スタイルガイド

### PEP 8準拠
- インデント: 4スペース（タブ禁止）
- 行の長さ: 最大88文字（black準拠）
- 命名規則:
  - 関数/変数: `snake_case`
  - クラス: `PascalCase`
  - 定数: `UPPER_SNAKE_CASE`

### 型ヒント必須（Python 3.13+）

```python
# ❌ 悪い例
def process_image(image_data, max_size):
    ...

# ✅ 良い例
def process_image(image_data: bytes, max_size: int = 10485760) -> dict[str, Any]:
    """
    画像データを処理する。

    Args:
        image_data: 画像のバイナリデータ
        max_size: 最大ファイルサイズ（バイト）

    Returns:
        処理結果を含む辞書

    Raises:
        ValueError: 画像サイズが制限を超える場合
    """
    ...
```

### docstring必須（Google style）

```python
def analyze_menu(self, image_data: bytes) -> AnalysisResult:
    """メニュー画像を解析して料理情報を抽出する。

    Args:
        image_data: メニュー画像のバイナリデータ

    Returns:
        AnalysisResult: 解析結果を含むオブジェクト
            - success: 解析が成功したかどうか
            - dishes: 検出された料理のリスト
            - error: エラーメッセージ（失敗時のみ）

    Raises:
        ValueError: 画像データが無効な場合
        APIError: AI APIの呼び出しに失敗した場合
    """
    ...
```

## ファイル構成

多くの小さなファイル > 少数の大きなファイル：
- 高い凝集度、低い結合度
- 200-400行が典型的、最大800行
- 機能/ドメインごとに整理（型ごとではなく）

## エラーハンドリング

常にエラーを包括的に処理：

```python
try:
    result = self._call_api(image_data)
    return AnalysisResult(success=True, dishes=result)
except anthropic.APIError as e:
    logger.error(f"API call failed: {e}")
    return AnalysisResult(success=False, error="AI service temporarily unavailable")
except Exception as e:
    logger.exception("Unexpected error during analysis")
    return AnalysisResult(success=False, error="Internal error occurred")
```

## イミュータビリティ（CRITICAL）

常に新しいオブジェクトを作成、決してミューテートしない：

```python
# ❌ 間違い: ミューテーション
def update_dish(dish, name):
    dish['name'] = name  # ミューテーション!
    return dish

# ✅ 正しい: イミュータビリティ
def update_dish(dish: dict, name: str) -> dict:
    return {**dish, 'name': name}
```

## コード品質チェックリスト

作業完了前に確認：
- [ ] コードが読みやすく、適切に命名されている
- [ ] 関数が小さい（<50行）
- [ ] ファイルが集中している（<800行）
- [ ] 深いネストがない（>4レベル）
- [ ] 適切なエラーハンドリング
- [ ] print文がない（loggingを使用）
- [ ] ハードコードされた値がない
- [ ] ミューテーションがない（イミュータブルパターンを使用）
- [ ] 型ヒントがある
- [ ] docstringがある
