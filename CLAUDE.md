# Menu Judge - プロジェクト仕様書

## プロジェクト概要

海外レストランのメニュー画像から料理の詳細情報を取得・表示するWebアプリケーション。
単純な翻訳ではなく、料理の特徴（辛さ、甘さ、材料等）を一覧表示し、将来的にはユーザーの好みに基づいた推薦機能を提供する。

## ユースケース

1. ユーザーがレストランでメニュー表の写真を撮影
2. Webアプリに画像をアップロード
3. AIがメニューから各料理を認識・解析
4. 料理ごとに詳細情報を表示
5. （将来）ユーザーの好みに合った料理を推薦

## 技術スタック

- **Backend**: Python 3.13+, Flask
- **AI**: マルチプロバイダー対応（環境変数で切り替え）
  - Claude API (Anthropic)
  - OpenAI GPT-4V
  - Google Gemini
- **Frontend**:
  - Jinja2テンプレート
  - Tailwind CSS（モダンなスタイリング）
  - HTMX（ページリロードなしの動的更新）
  - Alpine.js（軽量リアクティブUI）
- **検索**: Web検索API（追加情報取得用）

## UI/UXデザイン方針

### デザインコンセプト
- **ミニマル**: 必要な情報のみを表示、余白を活かしたデザイン
- **ダークモード対応**: 目に優しい配色
- **モバイルファースト**: スマホでの使用を最優先
- **直感的操作**: ドラッグ&ドロップ、タップで詳細表示

### カラーパレット
```
Primary:    #3B82F6 (Blue)
Secondary:  #10B981 (Green)
Accent:     #F59E0B (Amber)
Background: #0F172A (Slate 900)
Surface:    #1E293B (Slate 800)
Text:       #F8FAFC (Slate 50)
```

### コンポーネント
- **カード**: 角丸、シャドウ、ホバーエフェクト
- **ボタン**: グラデーション、押下フィードバック
- **ローディング**: スケルトンUI、プログレスインジケータ
- **通知**: トースト形式

### アニメーション
- ページ遷移: フェード
- カード表示: スライドイン
- ローディング: パルス/スピナー

## アーキテクチャ

```
┌─────────────────────────────────────┐
│           Browser                   │
│  ┌─────────┬─────────┬───────────┐  │
│  │Tailwind │  HTMX   │ Alpine.js │  │
│  │  CSS    │ (AJAX)  │(Reactive) │  │
│  └─────────┴─────────┴───────────┘  │
└──────────────┬──────────────────────┘
               │ HTML Fragments
               ▼
┌─────────────────────────────────────┐
│         Flask + Jinja2              │
│  ┌─────────────┐ ┌────────────────┐ │
│  │   Routes    │ │   Templates    │ │
│  │  (API)      │ │  (Partials)    │ │
│  └─────────────┘ └────────────────┘ │
└──────────────┬──────────────────────┘
               │
       ┌───────┴───────┐
       ▼               ▼
┌─────────────┐ ┌─────────────┐
│ Claude API  │ │ Web Search  │
│  (Vision)   │ │  (Optional) │
└─────────────┘ └─────────────┘
```

## 機能要件

### Phase 1: MVP（最小実行可能製品）

- [ ] 画像入力機能
  - **カメラ撮影（優先）**: その場で撮影してすぐ解析
  - ファイルアップロード: ドラッグ&ドロップ対応（フォールバック）
  - 対応形式: JPEG, PNG, WebP
  - 最大ファイルサイズ: 10MB

- [ ] 画像解析機能（Claude API）
  - メニュー画像から料理を識別
  - 各料理について以下を抽出:
    - 料理名（原語）
    - 料理名（日本語訳）
    - 料理の説明
    - 辛さレベル（1-5段階）
    - 甘さレベル（1-5段階）
    - 主な材料リスト
    - アレルギー情報（可能な場合）
    - 推定価格帯

- [ ] 結果表示機能
  - カード形式で各料理を表示
  - アイコンで辛さ・甘さを視覚化
  - 材料はタグ形式で表示

### Phase 2: 情報拡充

- [ ] Web検索連携
  - 料理名でWeb検索を実行
  - 画像・レビュー情報を追加取得
- [ ] 類似料理の提案
- [ ] 料理のカテゴリ分類（前菜、メイン、デザート等）

### Phase 3: パーソナライズ

- [ ] ユーザー認証（メール/OAuth）
- [ ] 好み登録機能
  - 好きな材料/嫌いな材料
  - 辛さの許容範囲
  - アレルギー情報
  - 食事制限（ベジタリアン等）
- [ ] 好みに基づく推薦表示
- [ ] 履歴保存・お気に入り機能

## ディレクトリ構成

```
menu-judge/
├── .github/
│   └── workflows/
│       ├── claude.yml              # Issue/PRコメント対応
│       └── claude-code-review.yml  # PR自動レビュー
├── app/
│   ├── __init__.py          # Flask アプリケーション初期化
│   ├── routes/
│   │   ├── __init__.py
│   │   └── menu.py          # メニュー解析エンドポイント
│   ├── services/
│   │   ├── __init__.py
│   │   ├── ai/                      # AIプロバイダー抽象化
│   │   │   ├── __init__.py
│   │   │   ├── base.py              # 基底クラス（インターフェース）
│   │   │   ├── claude_provider.py   # Claude API実装
│   │   │   ├── openai_provider.py   # OpenAI GPT-4V実装
│   │   │   ├── gemini_provider.py   # Google Gemini実装
│   │   │   └── factory.py           # プロバイダーファクトリ
│   │   └── search_service.py    # Web検索連携
│   ├── models/
│   │   ├── __init__.py
│   │   └── dish.py           # 料理データモデル
│   ├── templates/
│   │   ├── base.html         # ベーステンプレート（Tailwind/HTMX/Alpine読込）
│   │   ├── index.html        # メイン画面
│   │   ├── components/       # 再利用可能なコンポーネント
│   │   │   ├── dish_card.html
│   │   │   ├── upload_zone.html
│   │   │   └── loading.html
│   │   └── partials/         # HTMX用の部分テンプレート
│   │       ├── dish_list.html
│   │       └── error.html
│   └── static/
│       ├── css/
│       │   └── app.css       # Tailwind出力 + カスタムスタイル
│       ├── js/
│       │   └── app.js        # Alpine.jsコンポーネント
│       └── images/
├── tests/
│   ├── __init__.py
│   ├── test_routes.py
│   └── test_services.py
├── .env.example              # 環境変数サンプル
├── .gitignore
├── CLAUDE.md                 # このファイル
├── README.md
├── requirements.txt
├── tailwind.config.js        # Tailwind設定
├── package.json              # npm依存関係（Tailwind CLI用）
└── run.py                    # エントリーポイント
```

## 環境変数

```
# AIプロバイダー設定
AI_PROVIDER=claude                    # claude | openai | gemini

# API Keys（使用するプロバイダーのみ必須）
ANTHROPIC_API_KEY=your_api_key_here   # Claude API用
OPENAI_API_KEY=your_api_key_here      # OpenAI用
GOOGLE_API_KEY=your_api_key_here      # Gemini用

# Flask設定
# Note: FLASK_ENV is deprecated in Flask 2.3.0+
ENV=development
FLASK_DEBUG=1
SECRET_KEY=your_secret_key

# アップロード設定
MAX_UPLOAD_SIZE=10485760
```

## AIプロバイダー設計

### インターフェース（Strategy Pattern）

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass

@dataclass
class AnalysisResult:
    dishes: list[dict]
    raw_response: str
    provider: str

class AIProvider(ABC):
    """AIプロバイダーの基底クラス"""

    @abstractmethod
    def analyze_menu(self, image_data: bytes) -> AnalysisResult:
        """メニュー画像を解析して料理情報を返す"""
        pass

class AIProviderFactory:
    """環境変数に基づいてプロバイダーを生成"""

    @staticmethod
    def create() -> AIProvider:
        provider = os.getenv("AI_PROVIDER", "claude")
        if provider == "claude":
            return ClaudeProvider()
        elif provider == "openai":
            return OpenAIProvider()
        elif provider == "gemini":
            return GeminiProvider()
        raise ValueError(f"Unknown provider: {provider}")
```

## APIエンドポイント

### POST /api/analyze

メニュー画像を解析する

**Request:**
- Content-Type: multipart/form-data
- Body: image (file)

**Response:**
```json
{
  "success": true,
  "dishes": [
    {
      "original_name": "Pad Thai",
      "japanese_name": "パッタイ",
      "description": "米麺を使ったタイ風焼きそば",
      "spiciness": 2,
      "sweetness": 3,
      "ingredients": ["米麺", "エビ", "卵", "もやし", "ピーナッツ"],
      "allergens": ["甲殻類", "卵", "ナッツ"],
      "category": "main",
      "price_range": "$$"
    }
  ]
}
```

## 開発ガイドライン

### コーディング規約

- Python: PEP 8準拠
- 型ヒント必須
- docstring必須（Google style）
- テストカバレッジ: 80%以上を目標

### コミットメッセージ

```
<type>: <subject>

<body>

Types: feat, fix, docs, style, refactor, test, chore
```

### ブランチ戦略

- main: 本番リリース用
- develop: 開発用
- feature/*: 機能開発
- fix/*: バグ修正

## テスト

```bash
# テスト実行
pytest

# カバレッジ付き
pytest --cov=app --cov-report=html

# 特定のテストのみ
pytest tests/test_services.py -v
```

## 起動方法

```bash
# 仮想環境作成
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 依存関係インストール
pip install -r requirements.txt

# 環境変数設定
cp .env.example .env
# .envファイルを編集してAPI_KEYを設定

# 開発サーバー起動
python run.py
```

## GitHub Actions（Claude Code連携）

IssueやPRでClaude Codeが自動的に対応します。

### ワークフロー

| ファイル | トリガー | 動作 |
|---------|---------|------|
| `claude.yml` | `@claude` メンション | Issue/PRコメントに応答 |
| `claude-code-review.yml` | PR作成/更新 | 自動コードレビュー |

### 使い方

#### Issue/PRコメント
`@claude` をメンションして指示を出す

```markdown
@claude このIssueの実装方法を提案してください
```

#### 自動レビュー
PRを作成・更新すると自動でコードレビューが実行される

### セットアップ

GitHub Appインストール済み（`CLAUDE_CODE_OAUTH_TOKEN` 自動設定）

## 注意事項

- APIキーは絶対にコミットしない
- 画像は一時保存後に削除する
- ユーザーデータのプライバシーに配慮する
