"""Exercise the abstract method bodies in app.services.ai.base via super()."""

from app.services.ai.base import AIProvider, AnalysisResult


class _ConcreteProvider(AIProvider):
    @property
    def name(self) -> str:
        # Deliberately invoke the abstract method body to exercise line 52.
        AIProvider.name.fget(self)  # type: ignore[misc]
        return "concrete"

    def analyze_menu(self, image_data: bytes, mime_type: str) -> AnalysisResult:
        # Invoke the abstract method body to exercise line 69.
        AIProvider.analyze_menu(self, image_data, mime_type)
        return AnalysisResult(dishes=[], raw_response="", provider=self.name, processing_time=0.0)


class TestAbstractMethodBodies:
    def test_name_property_body_is_reachable(self):
        provider = _ConcreteProvider(api_key="sk-ant-test")
        assert provider.name == "concrete"

    def test_analyze_menu_body_is_reachable(self):
        provider = _ConcreteProvider(api_key="sk-ant-test")
        result = provider.analyze_menu(b"bytes", "image/png")
        assert result.provider == "concrete"
