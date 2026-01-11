/**
 * Menu Judge - Custom JavaScript
 * Provides interactive features in conjunction with Alpine.js
 */

// Toast notification constants
const TOAST_ANIMATION_DELAY = 10;  // Delay before animation starts (milliseconds)
const TOAST_FADE_DURATION = 300;   // Fade out animation duration (milliseconds)
const TOAST_DEFAULT_DURATION = 3000; // Default display duration (milliseconds)

/**
 * Display toast notification
 * @param {string} message - Message to display
 * @param {string} type - Message type (success, error, info, warning)
 * @param {number} duration - Display duration (milliseconds)
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
                showToast(t('toast.multiple_files'), 'warning');
                return;
            }

            if (files.length === 1) {
                const file = files[0];

                // 早期にファイルサイズをチェック（パフォーマンス向上）
                if (file.size > MAX_FILE_SIZE) {
                    showToast(t('toast.file_too_large'), 'error');
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
                showToast(t('toast.unsupported_format'), 'error');
                return;
            }

            // ファイルサイズのバリデーション
            if (file.size > MAX_FILE_SIZE) {
                showToast(t('toast.file_too_large'), 'error');
                return;
            }

            // ファイルを保存
            this.file = file;

            // プレビュー生成
            this.generatePreview(file);

            showToast(t('toast.image_loaded'), 'success');
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
                showToast(t('toast.no_file'), 'error');
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
                    showToast(t('toast.analysis_complete'), 'success');
                    // 結果を表示（HTMXまたはAlpine.jsで処理）
                    // この部分は後で実装
                } else {
                    showToast(data.error || t('toast.analysis_failed'), 'error');
                }
            })
            .catch(error => {
                this.isUploading = false;
                // ネットワークエラー（オフライン、タイムアウト、CORS等）とAPIエラーを区別
                if (error instanceof TypeError) {
                    showToast(t('toast.network_error'), 'error');
                } else {
                    showToast(error.message || t('toast.server_error'), 'error');
                }
            });
        }
    };
}

// グローバルに公開
window.uploadZone = uploadZone;

/**
 * APIキー設定管理のAlpine.jsコンポーネント
 * @returns {Object} Alpine.jsコンポーネントオブジェクト
 */
function apiKeyManager() {
    return {
        // モーダル表示状態
        showModal: false,

        // APIキー
        apiKey: '',

        // APIキー入力フィールド（マスク用）
        apiKeyInput: '',

        // APIキーの表示/非表示
        showApiKey: false,

        // 初期化
        init() {
            // localStorageからAPIキーを読み込み
            this.apiKey = this.getStoredApiKey();

            // APIキーが未設定の場合、モーダルを表示
            if (!this.apiKey) {
                this.showModal = true;
            }

            // HTMX リクエストにAPIキーを追加
            this.setupHtmxHeaders();

            // HTMXエラーハンドリング
            this.setupErrorHandling();
        },

        /**
         * localStorageからAPIキーを取得
         * @returns {string} APIキー（未設定の場合は空文字列）
         */
        getStoredApiKey() {
            try {
                return localStorage.getItem('menu_judge_api_key') || '';
            } catch (e) {
                console.error('Failed to load API key from localStorage:', e);
                return '';
            }
        },

        /**
         * APIキーをlocalStorageに保存
         * @param {string} key - 保存するAPIキー
         */
        saveApiKey(key) {
            try {
                if (key && key.trim()) {
                    localStorage.setItem('menu_judge_api_key', key.trim());
                    this.apiKey = key.trim();
                    showToast(t('toast.api_key_saved'), 'success');
                    this.closeModal();
                    this.setupHtmxHeaders();
                } else {
                    showToast(t('toast.api_key_required'), 'error');
                }
            } catch (e) {
                console.error('Failed to save API key:', e);
                showToast(t('toast.failed_to_save'), 'error');
            }
        },

        /**
         * APIキーをlocalStorageから削除
         */
        deleteApiKey() {
            if (confirm(t('api_key_modal.delete_confirm'))) {
                try {
                    localStorage.removeItem('menu_judge_api_key');
                    this.apiKey = '';
                    this.apiKeyInput = '';
                    showToast(t('toast.api_key_deleted'), 'success');
                    this.showModal = true;
                } catch (e) {
                    console.error('Failed to delete API key:', e);
                    showToast(t('toast.failed_to_delete'), 'error');
                }
            }
        },

        /**
         * モーダルを開く
         */
        openModal() {
            this.apiKeyInput = this.apiKey;
            this.showModal = true;
        },

        /**
         * モーダルを閉じる
         */
        closeModal() {
            // APIキーが未設定の場合は警告を表示
            if (!this.apiKey) {
                showToast(t('toast.api_key_setup'), 'warning', 5000);
            }
            this.showModal = false;
            this.apiKeyInput = '';
            this.showApiKey = false;
        },

        /**
         * HTMXリクエストヘッダーにAPIキーを追加
         */
        setupHtmxHeaders() {
            // HTMXのグローバル設定でヘッダーを追加
            document.body.addEventListener('htmx:configRequest', (event) => {
                if (this.apiKey) {
                    event.detail.headers['X-API-Key'] = this.apiKey;
                }
                // Add language header
                const language = getCurrentLanguage();
                event.detail.headers['X-Language'] = language;
            });
        },

        /**
         * HTMXエラーハンドリングを設定
         */
        setupErrorHandling() {
            // HTTPレスポンスエラーの処理
            document.body.addEventListener('htmx:responseError', (event) => {
                const status = event.detail.xhr.status;
                const errorCode = event.detail.xhr.getResponseHeader('X-Error-Code');

                // 401エラー（認証エラー）またはAPIキーエラーの場合
                if (status === 401 || errorCode === 'NO_API_KEY') {
                    showToast(t('toast.api_key_invalid'), 'error', 5000);
                    this.showModal = true;
                }
                // その他のエラー
                else if (status >= 400) {
                    try {
                        const response = JSON.parse(event.detail.xhr.responseText);
                        showToast(response.error || `エラーが発生しました (${status})`, 'error');
                    } catch (e) {
                        showToast(`エラーが発生しました (${status})`, 'error');
                    }
                }
            });

            // ネットワークエラー（タイムアウト、オフライン等）の処理
            document.body.addEventListener('htmx:sendError', (event) => {
                showToast(t('toast.network_error_server'), 'error');
            });
        }
    };
}

// グローバルに公開
window.apiKeyManager = apiKeyManager;
