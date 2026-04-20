"""Cover claude_provider._build_prompt fallback when base prompt lacks '```json'."""

from unittest.mock import patch

from app.services.ai.claude_provider import ClaudeProvider


class TestBuildPromptFallback:
    def test_build_prompt_appends_when_no_json_marker(self):
        provider = ClaudeProvider(api_key="sk-ant-test")
        with patch.object(
            provider.prompt_builder,
            "build_menu_analysis_prompt",
            return_value="a plain prompt without json marker",
        ):
            prompt = provider._build_prompt()
        assert "a plain prompt without json marker" in prompt
        assert "bounding_box" in prompt
        assert prompt.startswith("a plain prompt")

    def test_build_prompt_injects_before_json_marker_when_present(self):
        provider = ClaudeProvider(api_key="sk-ant-test")
        marker_prompt = "preamble\n```json\n{...}\n```"
        with patch.object(
            provider.prompt_builder,
            "build_menu_analysis_prompt",
            return_value=marker_prompt,
        ):
            prompt = provider._build_prompt()
        assert "bounding_box" in prompt
        before_json, after_json = prompt.split("```json", 1)
        assert "bounding_box" in before_json
        assert "{...}" in after_json
