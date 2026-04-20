# LLM振る舞いガイドライン（Karpathy原則）

Andrej Karpathy氏の[LLMコーディングに関する観察](https://x.com/karpathy/status/2015883857489522876)から導出された4原則。
コードを書く前／書いている最中／レビュー時に常に意識する。

**トレードオフ**: これらは「速度」より「慎重さ」を優先する。自明な変更には判断を使ってよい。

## 1. Think Before Coding（実装前に考える）

**勝手に仮定しない。迷いを隠さない。トレードオフを明示する。**

実装前に必ず：
- **仮定を明示する** — 不確実なら推測せずに質問する
- **複数の解釈がありうるなら提示する** — 黙って一つに決めない
- **よりシンプルな方法があるなら言う** — 適切ならユーザーを押し返す
- **不明点があれば止まる** — 何が曖昧かを名指しして質問する

### ❌ 悪い例: 仮定を隠して実装

```
ユーザー: "メニュー画像のエクスポート機能を追加して"
→ 勝手にJSON形式を選び、全料理を対象にし、ファイル出力を実装
```

### ✅ 良い例: 仮定を明示

```
エクスポート機能について、以下を確認させてくれ：

1. 対象: 解析済みの全料理？ 選択した料理のみ？
2. 形式: JSON / CSV / PDF のどれ？
3. 出力先: ブラウザダウンロード？ APIレスポンス？
4. 含める項目: 翻訳・材料・アレルギー情報すべて？

シンプルな案: 解析結果画面に「JSONダウンロード」ボタンを追加。
どれが近い？
```

## 2. Simplicity First（シンプルさを最優先）

**問題を解く最小限のコードだけ書く。投機的な実装はしない。**

- 依頼範囲を超えた機能は追加しない
- 一度しか使わないコードに抽象化を入れない
- 頼まれていない「柔軟性」「設定可能性」を入れない
- 起こりえないシナリオのエラーハンドリングを入れない
- 200行書いたが50行で済むなら書き直す

**判定基準**: シニアエンジニアが「これ過剰設計では？」と言うか？ Yesなら簡略化する。

### ❌ 悪い例: 過剰な抽象化

```python
# 依頼: "料理の辛さレベルを1-5でフォーマットする関数"
class SpicinessFormatterStrategy(ABC):
    @abstractmethod
    def format(self, level: int) -> str: ...

class EmojiSpicinessFormatter(SpicinessFormatterStrategy): ...
class TextSpicinessFormatter(SpicinessFormatterStrategy): ...

class SpicinessFormatterFactory:
    def create(self, type: str) -> SpicinessFormatterStrategy: ...
```

### ✅ 良い例: 必要十分

```python
def format_spiciness(level: int) -> str:
    """辛さレベルを絵文字で表示（1-5）。"""
    return "🌶️" * level
```

**いつ複雑さを足すか**: 実際に複数のフォーマッタが必要になった時。

## 3. Surgical Changes（外科的変更）

**必要な場所だけ触る。自分が生み出した散らかりだけ片付ける。**

既存コードを編集する時：
- 周辺のコード・コメント・フォーマットを「ついでに改善」しない
- 壊れていないものをリファクタしない
- 自分ならこう書くと思っても既存スタイルに合わせる
- 無関係なデッドコードに気付いたら **削除せず指摘する**

自分の変更がオーファンを生んだ時：
- 自分の変更で未使用になったimport/変数/関数は削除する
- 事前から存在していたデッドコードは依頼されない限り削除しない

**判定基準**: 変更された全行がユーザーの依頼に直接トレースできるか？

### ❌ 悪い例: 便乗リファクタ

```diff
依頼: "validate_image()でPDFファイルも弾くようにして"

  def validate_image(file):
-     # チェックファイル
+     """画像ファイルの検証。"""
+     if file is None:
+         return False
      if not file.filename:
          return False
-     if not allowed_file(file.filename):
+     # PDFも弾く
+     ext = file.filename.rsplit('.', 1)[1].lower()
+     if ext not in ALLOWED_EXTENSIONS or ext == 'pdf':
          return False
-     file.seek(0, 2)
-     size = file.tell()
-     file.seek(0)
+     size = _get_file_size(file)
      return size <= MAX_FILE_SIZE
```

問題: docstringの追加、None判定の追加、ヘルパー抽出など **依頼と無関係な変更が多数混入**。

### ✅ 良い例: 依頼箇所のみ変更

```diff
  def validate_image(file):
      # チェックファイル
      if not file.filename:
          return False
      if not allowed_file(file.filename):
          return False
+     if file.filename.rsplit('.', 1)[1].lower() == 'pdf':
+         return False
      file.seek(0, 2)
```

## 4. Goal-Driven Execution（ゴール駆動実行）

**成功条件を定義する。検証できるまでループする。**

命令形のタスクを、検証可能なゴールに変換する：

| Before | After |
|---|---|
| "バリデーションを追加して" | "不正入力のテストを書いて、それをパスさせる" |
| "バグを直して" | "再現テストを書いて、それをパスさせる" |
| "Xをリファクタして" | "変更前後で既存テストがパスすることを保証する" |

複数ステップのタスクは、ステップごとの検証を明示する：

```
1. [ステップ] → 検証: [チェック方法]
2. [ステップ] → 検証: [チェック方法]
3. [ステップ] → 検証: [チェック方法]
```

### ✅ 良い例: レート制限追加の計画

```
レート制限追加の計画:

1. /api/analyze に基本的なin-memoryレート制限（1分10回）
   検証: pytest で 11回目が 429 を返すテスト

2. flask-limiter に置換（複数サーバー対応は後回し）
   検証: 既存のmenu解析テストが壊れていないこと

3. レート制限値を環境変数化
   検証: .env.example 更新、テストで値が反映されることを確認

ステップ1から着手する？
```

強い成功条件があれば独立にループできる。弱い条件（"動くようにして"）は質問が増え続ける。

---

## 動作確認チェックリスト

このガイドラインが機能している時の兆候：
- [ ] diffに不要な変更が混ざっていない（依頼範囲のみ）
- [ ] 過剰設計による書き直しが減っている
- [ ] 実装後ではなく、実装前に確認質問が出る
- [ ] PRが小さく、クリーンで、「ついでに」要素がない

## 関連ドキュメント

- `.claude/rules/coding-style.md` — Pythonの書き方（PEP8、型ヒント、docstring）
- `.claude/rules/git-workflow.md` — ブランチ戦略とコミットメッセージ
- `.claude/rules/testing.md` — TDDとテスト要件

このファイルは **どう振る舞うか**、上記ファイルは **どう書くか** を扱う。両方を満たすこと。
