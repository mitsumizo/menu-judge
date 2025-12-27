/**
 * Menu Judge - カスタムJavaScript
 * Alpine.jsと連携してインタラクティブな機能を提供
 */

// Toast通知の定数
const TOAST_ANIMATION_DELAY = 10;  // アニメーション開始までの遅延（ミリ秒）
const TOAST_FADE_DURATION = 300;   // フェードアウトのアニメーション時間（ミリ秒）
const TOAST_DEFAULT_DURATION = 3000; // デフォルトの表示時間（ミリ秒）

/**
 * Toast通知を表示する
 * @param {string} message - 表示するメッセージ
 * @param {string} type - メッセージタイプ (success, error, info, warning)
 * @param {number} duration - 表示時間（ミリ秒）
 */
function showToast(message, type = 'info', duration = TOAST_DEFAULT_DURATION) {
    const container = document.getElementById('toast-container');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = `toast toast-${type} mb-2 p-4 rounded-lg shadow-lg transform transition-all duration-300 ease-in-out`;

    // タイプ別のスタイル設定
    const typeStyles = {
        success: 'bg-secondary text-white',
        error: 'bg-red-600 text-white',
        info: 'bg-primary text-white',
        warning: 'bg-accent text-white'
    };

    toast.className += ` ${typeStyles[type] || typeStyles.info}`;
    toast.textContent = message;

    // ARIA属性でアクセシビリティ向上
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', type === 'error' ? 'assertive' : 'polite');

    // 初期状態（非表示）
    toast.style.opacity = '0';
    toast.style.transform = 'translateX(100%)';

    container.appendChild(toast);

    // アニメーションで表示
    setTimeout(() => {
        toast.style.opacity = '1';
        toast.style.transform = 'translateX(0)';
    }, TOAST_ANIMATION_DELAY);

    // 指定時間後に非表示にして削除
    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(100%)';

        setTimeout(() => {
            // 親要素が存在する場合のみ削除（メモリリーク防止）
            if (toast.parentElement) {
                container.removeChild(toast);
            }
        }, TOAST_FADE_DURATION);
    }, duration);
}

// グローバルに公開
window.showToast = showToast;

// ファイルサイズの定数（10MB）
const MAX_FILE_SIZE = 10 * 1024 * 1024;

// 許可される画像形式
const ALLOWED_IMAGE_TYPES = ['image/jpeg', 'image/png', 'image/webp'];

/**
 * 画像アップロードゾーンのAlpine.jsコンポーネント
 * @returns {Object} Alpine.jsコンポーネントオブジェクト
 */
function uploadZone() {
    return {
        isDragging: false,
        file: null,
        preview: null,
        isUploading: false,

        /**
         * ファイル選択イベントハンドラ
         * @param {Event} event - ファイル選択イベント
         */
        handleFileSelect(event) {
            const file = event.target.files[0];
            if (file) {
                this.processFile(file);
            }
        },

        /**
         * ドロップイベントハンドラ
         * @param {DragEvent} event - ドロップイベント
         */
        handleDrop(event) {
            this.isDragging = false;
            const files = event.dataTransfer.files;

            // 複数ファイルのドロップをチェック
            if (files.length > 1) {
                showToast('一度に処理できる画像は1枚です', 'warning');
                return;
            }

            if (files.length === 1) {
                const file = files[0];

                // 早期にファイルサイズをチェック（パフォーマンス向上）
                if (file.size > MAX_FILE_SIZE) {
                    showToast('ファイルサイズが大きすぎます。10MB以下の画像を選択してください。', 'error');
                    return;
                }

                this.processFile(file);
            }
        },

        /**
         * ファイルを処理する（バリデーション・プレビュー生成）
         * @param {File} file - 処理するファイル
         */
        processFile(file) {
            // ファイルタイプのバリデーション
            if (!ALLOWED_IMAGE_TYPES.includes(file.type)) {
                showToast(
                    '対応していない画像形式です。JPEG、PNG、WebPのいずれかを選択してください。',
                    'error'
                );
                return;
            }

            // ファイルサイズのバリデーション
            if (file.size > MAX_FILE_SIZE) {
                showToast(
                    'ファイルサイズが大きすぎます。10MB以下の画像を選択してください。',
                    'error'
                );
                return;
            }

            // ファイルを保存
            this.file = file;

            // プレビュー生成
            this.generatePreview(file);

            showToast('画像を読み込みました', 'success');
        },

        /**
         * プレビュー画像を生成する
         * @param {File} file - プレビューを生成するファイル
         */
        generatePreview(file) {
            // 以前のプレビューURLを解放（メモリリーク防止）
            if (this.preview) {
                URL.revokeObjectURL(this.preview);
            }

            // URL.createObjectURLを使用（大きな画像でもメモリ効率が良い）
            this.preview = URL.createObjectURL(file);
        },

        /**
         * ファイルをクリアする
         */
        clearFile() {
            // ファイル入力をリセット（同じファイルを再選択できるようにする）
            const fileInputs = this.$el.querySelectorAll('input[type="file"]');
            fileInputs.forEach(input => input.value = '');

            // プレビューURLを解放（メモリリーク防止）
            if (this.preview) {
                URL.revokeObjectURL(this.preview);
            }

            this.file = null;
            this.preview = null;
            this.isUploading = false;
        },

        /**
         * ファイルをアップロードして解析を開始する
         */
        uploadFile() {
            if (!this.file) {
                showToast('ファイルが選択されていません', 'error');
                return;
            }

            this.isUploading = true;

            const formData = new FormData();
            formData.append('image', this.file);

            // CSRFトークンを取得
            const csrfToken = document.querySelector('meta[name="csrf-token"]')?.content;

            // HTMX経由でアップロード（hx-post属性を使用する場合）
            // または、Fetch APIを使用してアップロード
            fetch('/api/analyze', {
                method: 'POST',
                headers: csrfToken ? { 'X-CSRF-Token': csrfToken } : {},
                body: formData
            })
            .then(async response => {
                if (!response.ok) {
                    const errorData = await response.json().catch(() => ({}));
                    throw new Error(errorData.error || `サーバーエラー: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                this.isUploading = false;
                if (data.success) {
                    showToast('解析が完了しました', 'success');
                    // 結果を表示（HTMXまたはAlpine.jsで処理）
                    // この部分は後で実装
                } else {
                    showToast(data.error || '解析に失敗しました', 'error');
                }
            })
            .catch(error => {
                this.isUploading = false;
                // ネットワークエラー（オフライン、タイムアウト、CORS等）とAPIエラーを区別
                if (error instanceof TypeError) {
                    showToast('ネットワークエラー: 接続を確認してください', 'error');
                } else {
                    showToast(error.message || 'エラーが発生しました', 'error');
                }
            });
        }
    };
}

// グローバルに公開
window.uploadZone = uploadZone;
