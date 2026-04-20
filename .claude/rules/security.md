# セキュリティガイドライン

## 必須セキュリティチェック

コミット前に必ず確認：
- [ ] ハードコードされたシークレットがない（APIキー、パスワード、トークン）
- [ ] すべてのユーザー入力がバリデーションされている
- [ ] SQLインジェクション対策（パラメータ化されたクエリ）
- [ ] XSS対策（HTMLのサニタイズ）
- [ ] CSRF保護が有効
- [ ] 認証/認可が検証されている
- [ ] レート制限がすべてのエンドポイントに設定されている
- [ ] エラーメッセージが機密データを漏らさない

## シークレット管理

```python
# ❌ 絶対にダメ: ハードコードされたシークレット
api_key = "sk-ant-api03-xxxxx"

# ✅ 正しい方法: ヘッダーから取得（Menu-Judgeの方式）
api_key = request.headers.get('X-API-Key')
if not api_key:
    return {"error": "API key required"}, 401

# ✅ 正しい方法: 環境変数（サーバー側シークレットの場合）
from os import environ
secret_key = environ.get('SECRET_KEY')
if not secret_key:
    raise ValueError('SECRET_KEY not configured')
```

## 入力バリデーション

```python
# ファイルアップロードの検証
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'webp'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

def allowed_file(filename: str) -> bool:
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def validate_image(file) -> bool:
    if not file or not file.filename:
        return False
    if not allowed_file(file.filename):
        return False
    file.seek(0, 2)  # ファイル末尾に移動
    size = file.tell()
    file.seek(0)  # 先頭に戻る
    return size <= MAX_FILE_SIZE
```

## Menu-Judge固有のセキュリティ

### APIキーの扱い
- クライアント側のlocalStorageに保存
- リクエストごとにX-API-Keyヘッダーで送信
- サーバーはAPIキーを保存しない
- ログにAPIキーを出力しない

### 画像アップロード
- ファイル拡張子を検証（.jpg, .png, .webp）
- MIMEタイプを検証
- ファイルサイズを制限（10MB）
- secure_filename()でファイル名をサニタイズ
- 一時ファイルは処理後に削除

## セキュリティ対応プロトコル

セキュリティ問題が見つかった場合：
1. 即座に停止
2. **security-reviewer**エージェントを使用
3. CRITICALな問題を続行前に修正
4. 露出したシークレットをローテート
5. 類似の問題がないかコードベース全体をレビュー
