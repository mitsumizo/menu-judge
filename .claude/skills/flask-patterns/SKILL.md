---
name: flask-patterns
description: Flask Webアプリケーションのアーキテクチャパターン、APIデザイン、エラーハンドリングのベストプラクティス
---

# Flask開発パターン

Flask Webアプリケーションのアーキテクチャパターンとベストプラクティス。

## APIデザインパターン

### RESTful API構造

```python
# Blueprintを使用したルーティング
from flask import Blueprint, request, jsonify

menu_bp = Blueprint('menu', __name__, url_prefix='/api')

@menu_bp.route('/analyze', methods=['POST'])
def analyze_menu():
    """メニュー画像を解析するエンドポイント"""
    # 認証チェック
    api_key = request.headers.get('X-API-Key')
    if not api_key:
        return jsonify({'error': 'API key required'}), 401

    # ファイルバリデーション
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400

    file = request.files['image']
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type'}), 400

    # 処理
    result = analyze_image(file, api_key)
    return jsonify(result)
```

### レスポンス形式

```python
# 成功レスポンス
{
    "success": True,
    "data": {
        "dishes": [...]
    }
}

# エラーレスポンス
{
    "success": False,
    "error": "エラーメッセージ"
}
```

## エラーハンドリングパターン

### カスタムエラークラス

```python
class APIError(Exception):
    """API エラーの基底クラス"""
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(message)

class ValidationError(APIError):
    """バリデーションエラー"""
    def __init__(self, message: str):
        super().__init__(message, 400)

class AuthenticationError(APIError):
    """認証エラー"""
    def __init__(self, message: str = "Authentication required"):
        super().__init__(message, 401)
```

### グローバルエラーハンドラー

```python
@app.errorhandler(APIError)
def handle_api_error(error: APIError):
    """APIエラーをJSON形式で返す"""
    return jsonify({
        'success': False,
        'error': error.message
    }), error.status_code

@app.errorhandler(Exception)
def handle_unexpected_error(error: Exception):
    """予期しないエラーを安全に処理"""
    app.logger.exception("Unexpected error occurred")
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500
```

## AIプロバイダー抽象化（Strategy Pattern）

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

@dataclass
class AnalysisResult:
    success: bool
    dishes: list = None
    error: Optional[str] = None
    provider: str = ""

class AIProvider(ABC):
    """AIプロバイダーの基底クラス"""

    @abstractmethod
    def analyze_menu(self, image_data: bytes) -> AnalysisResult:
        """メニュー画像を解析して料理情報を返す"""
        pass

class ClaudeProvider(AIProvider):
    """Claude API実装"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = anthropic.Anthropic(api_key=api_key)

    def analyze_menu(self, image_data: bytes) -> AnalysisResult:
        try:
            response = self._call_api(image_data)
            dishes = self._parse_response(response)
            return AnalysisResult(
                success=True,
                dishes=dishes,
                provider="claude"
            )
        except Exception as e:
            return AnalysisResult(
                success=False,
                error=str(e),
                provider="claude"
            )
```

## ファイルアップロード処理

```python
import os
from werkzeug.utils import secure_filename
from PIL import Image
import io

ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'webp'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

def allowed_file(filename: str) -> bool:
    """許可されたファイル拡張子かチェック"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def validate_image(file) -> bytes:
    """画像ファイルを検証してバイトデータを返す"""
    # ファイル名をサニタイズ
    filename = secure_filename(file.filename)

    if not allowed_file(filename):
        raise ValidationError("Invalid file type. Allowed: jpg, png, webp")

    # ファイルサイズをチェック
    file.seek(0, 2)
    size = file.tell()
    file.seek(0)

    if size > MAX_FILE_SIZE:
        raise ValidationError(f"File too large. Max size: {MAX_FILE_SIZE // 1024 // 1024}MB")

    # 画像として読み込めるか確認
    try:
        image_data = file.read()
        Image.open(io.BytesIO(image_data))
        return image_data
    except Exception:
        raise ValidationError("Invalid image file")
```

## 設定管理

```python
import os

class Config:
    """基底設定"""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key')
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10MB

class DevelopmentConfig(Config):
    """開発環境設定"""
    DEBUG = True

class ProductionConfig(Config):
    """本番環境設定"""
    DEBUG = False

class TestingConfig(Config):
    """テスト環境設定"""
    TESTING = True

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
```

## アプリケーションファクトリパターン

```python
from flask import Flask

def create_app(config_name: str = 'default') -> Flask:
    """アプリケーションファクトリ"""
    app = Flask(__name__)

    # 設定を読み込み
    app.config.from_object(config[config_name])

    # Blueprintを登録
    from app.routes.menu import menu_bp
    app.register_blueprint(menu_bp)

    # エラーハンドラーを登録
    register_error_handlers(app)

    return app
```

## ログ設定

```python
import logging
from logging.handlers import RotatingFileHandler

def setup_logging(app: Flask):
    """ログ設定"""
    if not app.debug:
        # ファイルハンドラー
        file_handler = RotatingFileHandler(
            'logs/app.log',
            maxBytes=10240000,
            backupCount=10
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

    app.logger.setLevel(logging.INFO)
    app.logger.info('Application startup')
```

## セキュリティベストプラクティス

```python
from flask import Flask
from flask_talisman import Talisman

def configure_security(app: Flask):
    """セキュリティ設定"""
    # HTTPSを強制（本番環境）
    if not app.debug:
        Talisman(app, content_security_policy=None)

    # セッション設定
    app.config['SESSION_COOKIE_SECURE'] = True
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
```

**覚えておくこと**: Flaskパターンはスケーラブルで保守しやすいサーバーサイドアプリケーションを実現します。プロジェクトの複雑度に合ったパターンを選択してください。
