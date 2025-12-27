# 不要なWorktreeの削除

不要になったGit Worktreeを安全に削除するためのコマンドです。

## 手順

1. **Worktreeの一覧確認**
   - まず `git worktree list` を実行し、現在存在するWorktreeの一覧を確認してください。

2. **削除対象の特定**
   - 引数 `$ARGUMENTS` が指定されている場合:
     - 入力をIssue番号とみなし、ディレクトリ名 `issue-$ARGUMENTS` を探してください。
     - 見つからない場合は、入力された文字列そのものをパスとして扱ってください。
   - 引数がない場合:
     - ユーザーに削除したいWorktreeを指定するよう求めてください。
   - **注意**: メインのWorktree（bare repoでない場合、`.git`ディレクトリを持つルート）は絶対に削除しないでください。

3. **Worktreeの削除実行**
   - 特定したパスに対して `git worktree remove <worktree-path>` を実行してください。
   - もし「未マージの変更がある」等のエラーが出た場合は、ユーザーに強制削除して良いか確認し、許可されれば `git worktree remove --force <worktree-path>` を実行してください。

4. **ローカルブランチの削除（デフォルト実行）**
   - Worktreeに関連付けられていたブランチ（例: `feature/issue-$ARGUMENTS`）をデフォルトで削除してください。
   - `git branch -d <branch-name>` を実行してください。
   - マージされていない場合でも、リモートにプッシュ済みであれば削除して問題ありません。
   - **注意**: リモートブランチはPR用に残しておくため削除しないでください。

5. **mainブランチに戻る**
   - `git checkout main` を実行して、mainブランチに戻ってください。

6. **後処理**
   - `git worktree prune` を実行して、無効なWorktree情報をクリーンアップしてください。
   - 最後に `git worktree list` を実行して、削除が完了したことを示してください。
