"""エンドツーエンドの統合テスト"""

from io import BytesIO
from unittest.mock import patch


class TestMenuAnalysisFlow:
    """メニュー解析の一連のフローをテスト"""

    def test_full_analysis_flow_json(self, client, real_menu_image, mock_analysis_result):
        """JSON応答での完全フロー"""
        # 1. トップページにアクセス
        response = client.get("/")
        assert response.status_code == 200

        # 2. 画像をアップロードして解析
        # ファクトリーからモックプロバイダーを返すようにパッチ
        with patch("app.services.ai.factory.AIProviderFactory.create") as mock_factory:
            mock_provider = mock_factory.return_value
            mock_provider.analyze_menu.return_value = mock_analysis_result

            response = client.post(
                "/api/analyze",
                data={"image": (BytesIO(real_menu_image), "menu.jpg")},
                content_type="multipart/form-data",
            )

        # 3. 結果を検証
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert len(data["dishes"]) > 0
        assert "processing_time" in data

    def test_full_analysis_flow_htmx(self, client, real_menu_image, mock_analysis_result):
        """HTMX応答での完全フロー"""
        # ファクトリーからモックプロバイダーを返すようにパッチ
        with patch("app.services.ai.factory.AIProviderFactory.create") as mock_factory:
            mock_provider = mock_factory.return_value
            mock_provider.analyze_menu.return_value = mock_analysis_result

            response = client.post(
                "/api/analyze",
                data={"image": (BytesIO(real_menu_image), "menu.jpg")},
                headers={"HX-Request": "true"},
                content_type="multipart/form-data",
            )

        assert response.status_code == 200
        assert b"dish-card" in response.data
        # Note: '解析結果' may not appear in the HTML, so we check for the card presence instead

    def test_error_recovery(self, client, real_menu_image, mock_analysis_result):
        """エラーからの復旧テスト"""
        # 1. エラーを発生させる（画像なしでリクエスト）
        response = client.post("/api/analyze")
        assert response.status_code == 400

        # 2. 正しい画像で再試行
        # ファクトリーからモックプロバイダーを返すようにパッチ
        with patch("app.services.ai.factory.AIProviderFactory.create") as mock_factory:
            mock_provider = mock_factory.return_value
            mock_provider.analyze_menu.return_value = mock_analysis_result

            response = client.post(
                "/api/analyze",
                data={"image": (BytesIO(real_menu_image), "menu.jpg")},
                content_type="multipart/form-data",
            )

        assert response.status_code == 200


class TestMultipleProviders:
    """複数プロバイダーのテスト"""

    @patch.dict("os.environ", {"AI_PROVIDER": "claude", "ANTHROPIC_API_KEY": "test-key"})
    def test_claude_provider_selection(self, client):
        """Claudeプロバイダーが選択される"""
        from app.services.ai.factory import AIProviderFactory

        provider = AIProviderFactory.create()
        assert provider.name == "claude"

    @patch.dict("os.environ", {"AI_PROVIDER": "invalid"})
    def test_invalid_provider_error(self, client, real_menu_image):
        """無効なプロバイダーでエラー"""
        response = client.post(
            "/api/analyze",
            data={"image": (BytesIO(real_menu_image), "menu.jpg")},
            content_type="multipart/form-data",
        )
        assert response.status_code == 500
