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
