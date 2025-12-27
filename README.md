# Menu Judge

海外レストランのメニュー画像から料理の詳細情報を取得するWebアプリケーション

## 概要

旅行先でメニューを見ても何の料理かわからない...そんな問題を解決します。

メニューの写真を撮るだけで:
- 料理名を日本語に翻訳
- 辛さ・甘さレベルを表示
- 材料・アレルギー情報を確認
- （将来）あなたの好みに合った料理を推薦

## 技術スタック

- **Backend**: Python 3.11+, Flask
- **AI**: Claude API (Vision)
- **Frontend**: HTML/CSS/JavaScript

## セットアップ

```bash
# リポジトリをクローン
git clone https://github.com/mitsumizo/menu-judge.git
cd menu-judge

# Python仮想環境作成
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Python依存関係インストール
pip install -r requirements.txt

# フロントエンド依存関係インストール
npm install

# フロントエンドアセットをビルド
npm run build

# 環境変数設定
cp .env.example .env
# .envファイルにANTHROPIC_API_KEYを設定

# 開発サーバー起動
python run.py
```

### 開発時のビルド

フロントエンドのコードを変更した場合：

```bash
# CSSの再ビルド（Tailwind）
npm run build:css

# JSライブラリの再コピー
npm run build:js

# 全てをビルド
npm run build

# CSSの変更を監視（自動再ビルド）
npm run watch:css
```

## 使い方

1. ブラウザで `http://localhost:5000` を開く
2. メニュー画像をアップロード
3. 解析結果を確認

## ライセンス

MIT
