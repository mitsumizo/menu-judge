"""Coverage for app.__init__ — language query-param fallback paths."""


class TestLanguageFallback:
    def test_invalid_lang_query_falls_back_to_english(self, client):
        """Hits inject_translation_helper + translation_function (lang='fr' → 'en')."""
        response = client.get("/?lang=fr")
        assert response.status_code == 200

    def test_valid_ja_lang_accepted(self, client):
        response = client.get("/?lang=ja")
        assert response.status_code == 200

    def test_no_lang_param_defaults_to_english(self, client):
        response = client.get("/")
        assert response.status_code == 200
