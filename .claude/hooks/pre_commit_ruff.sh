#!/bin/bash
# Git commit前のRuffチェック（Claude Code hooks用）

# git commitコマンドかチェック
input_data=$(cat)
command=$(echo "$input_data" | jq -r '.tool_input.command // empty')

# git commitでない場合はスキップ
if [[ ! "$command" =~ ^git[[:space:]]+commit ]]; then
    exit 0
fi

cd "$CLAUDE_PROJECT_DIR"

# Pythonファイルが変更されているかチェック
changed_python_files=$(git diff --cached --name-only --diff-filter=ACM | grep '\.py$' || true)

if [ -z "$changed_python_files" ]; then
    # Pythonファイルの変更がない場合はスキップ
    exit 0
fi

echo "🔍 Ruffでコード品質をチェック中..." >&2

# Ruffが利用可能かチェック
if ! command -v ruff &> /dev/null; then
    echo "⚠️  Ruffがインストールされていません。pip install ruff を実行してください。" >&2
    exit 0
fi

# ステージング済みのPythonファイルをチェック
ruff_errors=0
for file in $changed_python_files; do
    if [ -f "$file" ]; then
        echo "  チェック中: $file" >&2
        if ! ruff check "$file" --fix; then
            ruff_errors=1
        fi
        # フォーマットも実行
        ruff format "$file"
    fi
done

# 修正があった場合は変更を再ステージング
if [ $ruff_errors -eq 0 ]; then
    for file in $changed_python_files; do
        if [ -f "$file" ]; then
            git add "$file"
        fi
    done
    echo "✅ Ruffチェック完了" >&2
else
    echo "" >&2
    echo "❌ Ruffでエラーが検出されました。" >&2
    echo "修正後、再度git addしてコミットしてください。" >&2
    exit 2  # コミットをブロック
fi

exit 0
