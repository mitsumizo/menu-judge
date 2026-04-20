"""Cover app.__init__.create_app OSError handling when directory creation fails."""

from unittest.mock import patch

import pytest

from app import create_app


class TestMkdirFailure:
    def test_instance_path_mkdir_failure_raises_runtime_error(self):
        with patch("app.Path.mkdir", side_effect=OSError("disk full")):
            with pytest.raises(RuntimeError, match="Failed to create required directories"):
                create_app({"TESTING": True, "SECRET_KEY": "test"})
