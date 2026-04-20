"""AI prompt builder for multilingual support."""

import json
from app.translations.loader import TranslationLoader


class PromptBuilder:
    """多言語対応AIプロンプトビルダー

    選択された言語に応じて、適切なプロンプトを生成します。
    AIの回答も同じ言語で出力されるようにプロンプトを構成します。
    """

    def __init__(self, language: str = 'en'):
        """初期化

        Args:
            language: 言語コード ('en' または 'ja')

        Raises:
            ValueError: サポートされていない言語の場合
        """
        self.language = language
        self.translations = TranslationLoader.load(language)

    def build_menu_analysis_prompt(self) -> str:
        """メニュー解析用プロンプトを構築

        Returns:
            str: 言語に応じたプロンプト文字列
        """
        t = self.translations['ai_prompt']

        # 言語に応じた例を生成
        example_json = self._get_example_json()

        # プロンプトを構築
        prompt = f"""{t['system_message']}

For each dish, include the following information:
- {t['field_original_name']}
- {t['field_translated_name']}
- {t['field_description']}
- {t['field_spiciness']}
- {t['field_sweetness']}
- {t['field_ingredients']}
- {t['field_allergens']}
- {t['field_category']}

{t['output_format_intro']}
```json
{example_json}
```

{t['notes']}"""

        return prompt

    def _get_example_json(self) -> str:
        """言語に応じたJSON例を生成

        Returns:
            str: JSON例文字列
        """
        t = self.translations['ai_prompt']

        example = {
            "dishes": [
                {
                    "original_name": "Pad Thai",
                    "translated_name": t['example_dish_name'],
                    "description": t['example_description'],
                    "spiciness": 2,
                    "sweetness": 3,
                    "ingredients": t['example_ingredients'],
                    "allergens": t['example_allergens'],
                    "category": "main"
                }
            ]
        }

        # JSON文字列に変換（インデントあり、非ASCII文字をエスケープしない）
        return json.dumps(example, ensure_ascii=False, indent=2)
