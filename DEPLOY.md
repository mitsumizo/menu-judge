# Menu Judge - Renderデプロイガイド

このガイドでは、Menu JudgeをRenderの無料枠にデプロイする手順を説明します。

## 前提条件

- GitHubアカウント
- Renderアカウント（無料で作成可能）
- Anthropic API キー

## デプロイ手順

### 1. コードをGitHubにプッシュ

```bash
# 変更をコミット
git add .
git commit -m "Add Render deployment files"

# GitHubにプッシュ（リモートリポジトリが設定済みの場合）
git push origin main
```

### 2. Renderでアカウント作成

1. https://render.com にアクセス
2. **Sign Up** をクリック
3. GitHubアカウントで認証

### 3. 新規Web Serviceを作成

1. Renderダッシュボードで **New +** → **Web Service** を選択
2. GitHubリポジトリを接続（初回は権限承認が必要）
3. デプロイするリポジトリ（menu-judge）を選択

### 4. サービス設定

以下の設定を入力：

| 項目 | 設定値 |
|------|--------|
| **Name** | `menu-judge`（任意の名前） |
| **Region** | `Frankfurt (EU Central)` または `Oregon (US West)` |
| **Branch** | `main` |
| **Root Directory** | （空欄） |
| **Runtime** | `Python 3` |
| **Build Command** | `pip install -r requirements.txt && npm install && npm run build` |
| **Start Command** | `gunicorn --bind 0.0.0.0:$PORT 'app:create_app()'` |
| **Instance Type** | `Free` |

### 5. 環境変数の設定

**Environment** セクションで以下を追加：

```
ANTHROPIC_API_KEY=your_anthropic_api_key_here
AI_PROVIDER=claude
ENV=production
FLASK_DEBUG=0
SECRET_KEY=your_random_secret_key_here
```

**SECRET_KEYの生成方法:**
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### 6. デプロイ実行

1. **Create Web Service** をクリック
2. ビルドとデプロイが自動的に開始されます
3. ログでビルドの進行状況を確認
4. デプロイ完了後、URLが発行されます（例: `https://menu-judge.onrender.com`）

## デプロイ後の確認

### アプリケーションにアクセス

```
https://your-app-name.onrender.com
```

### ログの確認

Renderダッシュボード → **Logs** タブでアプリケーションログを確認できます。

### スリープからの復帰

無料プランでは15分間アクセスがないとスリープします。
初回アクセス時は30秒程度かかりますが、その後は通常速度で動作します。

## トラブルシューティング

### ビルドが失敗する

**症状:** `pip install` でエラー

**解決策:**
- `runtime.txt` でPythonバージョンが正しいか確認
- `requirements.txt` の依存関係を確認

### アプリが起動しない

**症状:** `Application failed to start`

**解決策:**
1. **Logs** タブでエラーメッセージを確認
2. 環境変数が正しく設定されているか確認
3. Start Commandが正しいか確認: `gunicorn --bind 0.0.0.0:$PORT 'app:create_app()'`

### 画像アップロードが失敗する

**症状:** 画像アップロード時にエラー

**解決策:**
1. ファイルサイズ制限（10MB）を確認
2. Renderのメモリ制限（無料プランは512MB）を確認
3. ログで詳細なエラーメッセージを確認

### Claude API呼び出しが失敗する

**症状:** "AI analysis failed"

**解決策:**
1. `ANTHROPIC_API_KEY` が正しく設定されているか確認
2. APIキーが有効か確認（https://console.anthropic.com）
3. API利用制限に達していないか確認

## 再デプロイ

コードを更新した場合:

```bash
git add .
git commit -m "Update feature"
git push origin main
```

GitHubにプッシュすると、Renderが自動的に再デプロイします。

## 環境変数の更新

1. Renderダッシュボード → あなたのサービス → **Environment**
2. 変更したい変数を編集
3. **Save Changes** をクリック
4. 自動的に再デプロイされます

## コスト管理

### 無料枠の制限

- **実行時間:** 月750時間まで（31日分）
- **メモリ:** 512MB
- **スリープ:** 15分間アクセスがないとスリープ
- **帯域幅:** 100GB/月

### 旅行期間中の使用

ドイツ旅行中（2週間程度）なら、無料枠で十分です：
- レストランで1日3回使用 × 14日 = 42回
- 1回の解析時間: 約5秒
- 合計使用時間: 約3.5分

スリープを考慮しても、月750時間の制限には余裕で収まります。

## 旅行後の削除

旅行が終わったらサービスを削除してクリーンアップ：

1. Renderダッシュボード → あなたのサービス
2. **Settings** タブ → **Delete Service**
3. サービス名を入力して削除確認

## 参考リンク

- [Render公式ドキュメント](https://docs.render.com/)
- [Python on Render](https://docs.render.com/deploy-flask)
- [Anthropic API ドキュメント](https://docs.anthropic.com/)

## サポート

問題が発生した場合は、以下を確認してください：
1. Renderのログ
2. GitHub Actionsのログ（CI/CDを設定している場合）
3. ブラウザの開発者ツール（コンソールエラー）
