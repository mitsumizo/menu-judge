/**
 * Menu Judge - Internationalization (i18n) Utility
 * Provides multilingual support for English and Japanese
 */

// 翻訳データ（サーバーから動的に取得してグローバルに設定）
// window.translations = { en: {...}, ja: {...} }

/**
 * 現在の言語を取得
 * @returns {string} 言語コード ('en' または 'ja')
 */
function getCurrentLanguage() {
    // URLパラメータを優先的にチェック
    const urlParams = new URLSearchParams(window.location.search);
    const urlLang = urlParams.get('lang');
    if (urlLang && ['en', 'ja'].includes(urlLang)) {
        // URLパラメータの言語をlocalStorageに保存
        localStorage.setItem('menu_judge_language', urlLang);
        return urlLang;
    }

    // localStorageから取得
    const saved = localStorage.getItem('menu_judge_language');
    if (saved && ['en', 'ja'].includes(saved)) {
        return saved;
    }

    // デフォルトは英語
    return 'en';
}

/**
 * 言語を設定
 * @param {string} lang - 言語コード ('en' または 'ja')
 */
function setLanguage(lang) {
    if (!['en', 'ja'].includes(lang)) {
        console.error('Unsupported language:', lang);
        return;
    }
    localStorage.setItem('menu_judge_language', lang);
}

/**
 * 翻訳テキストを取得
 * @param {string} key - ドット記法のキー (例: 'ui.hero_title')
 * @param {string} fallback - キーが見つからない場合のフォールバック
 * @returns {string} 翻訳文字列
 */
function t(key, fallback = '') {
    const lang = getCurrentLanguage();
    const translations = window.translations && window.translations[lang];

    if (!translations) {
        console.error('Translations not loaded for language:', lang);
        return fallback || key;
    }

    // ネストしたキーを解決 ('ui.hero_title' -> translations.ui.hero_title)
    const keys = key.split('.');
    let value = translations;

    for (const k of keys) {
        if (value && typeof value === 'object' && k in value) {
            value = value[k];
        } else {
            return fallback || key;
        }
    }

    return value !== null && value !== undefined ? String(value) : (fallback || key);
}

/**
 * 配列の翻訳を取得（主にリスト項目用）
 * @param {string} key - 配列へのキー (例: 'ai_prompt.example_ingredients')
 * @returns {Array} 翻訳された配列（見つからない場合は空配列）
 */
function tArray(key) {
    const lang = getCurrentLanguage();
    const translations = window.translations && window.translations[lang];

    if (!translations) {
        return [];
    }

    const keys = key.split('.');
    let value = translations;

    for (const k of keys) {
        if (value && typeof value === 'object' && k in value) {
            value = value[k];
        } else {
            return [];
        }
    }

    return Array.isArray(value) ? value : [];
}

// グローバルに公開
window.getCurrentLanguage = getCurrentLanguage;
window.setLanguage = setLanguage;
window.t = t;
window.tArray = tArray;

/**
 * 言語切り替えAlpine.jsコンポーネント
 * @returns {Object} Alpine.jsコンポーネントオブジェクト
 */
function languageSwitcher() {
    return {
        currentLanguage: getCurrentLanguage(),

        init() {
            // ページロード時に言語を適用
            this.currentLanguage = getCurrentLanguage();
        },

        /**
         * 言語を切り替える（英語 ⇔ 日本語）
         */
        toggleLanguage() {
            const newLang = this.currentLanguage === 'en' ? 'ja' : 'en';
            this.switchLanguage(newLang);
        },

        /**
         * 指定した言語に切り替える
         * @param {string} lang - 言語コード
         */
        switchLanguage(lang) {
            if (!['en', 'ja'].includes(lang)) {
                console.error('Unsupported language:', lang);
                return;
            }

            // 言語を保存
            setLanguage(lang);
            this.currentLanguage = lang;

            // トースト通知（翻訳を使用）
            if (window.showToast) {
                showToast(t('toast.language_changed'), 'success');
            }

            // ページをリロードして翻訳を適用
            // サーバー側で言語に応じたコンテンツをレンダリングするため
            // URLパラメータで言語を指定
            const url = new URL(window.location.href);
            url.searchParams.set('lang', lang);
            window.location.href = url.toString();
        },

        /**
         * 言語ラベルを取得（表示用）
         * @returns {string} 言語ラベル（'EN' または 'JP'）
         */
        getLanguageLabel() {
            return this.currentLanguage === 'en' ? 'EN' : 'JP';
        },

        /**
         * 言語フラグ絵文字を取得
         * @returns {string} フラグ絵文字
         */
        getLanguageFlag() {
            return this.currentLanguage === 'en' ? '🇺🇸' : '🇯🇵';
        }
    };
}

// グローバルに公開
window.languageSwitcher = languageSwitcher;
