"""Tests for template rendering."""

from datetime import datetime


def test_base_template_renders_with_title(app):
    """Test that base template renders with custom title."""
    with app.test_request_context():
        from flask import render_template_string

        template = """
        {% extends "base.html" %}
        {% block title %}Test Title{% endblock %}
        {% block content %}Test Content{% endblock %}
        """
        rendered = render_template_string(template)

        assert "Test Title" in rendered
        assert "Test Content" in rendered


def test_base_template_has_required_elements(app):
    """Test that base template contains required HTML elements."""
    with app.test_request_context():
        from flask import render_template_string

        template = """
        {% extends "base.html" %}
        {% block content %}{% endblock %}
        """
        rendered = render_template_string(template)

        # Check for required meta tags
        assert '<meta charset="UTF-8">' in rendered
        assert '<meta name="viewport"' in rendered

        # Check for required CSS
        assert 'css/app.css' in rendered

        # Check for required JS libraries (local files, not CDN)
        assert 'js/vendor/htmx.min.js' in rendered
        assert 'js/vendor/alpinejs.min.js' in rendered
        assert 'unpkg.com' not in rendered  # Ensure no CDN usage

        # Check for required structural elements
        assert '<header' in rendered
        assert '<main' in rendered
        assert '<footer' in rendered

        # Check for toast container
        assert 'id="toast-container"' in rendered

        # Check for custom app.js
        assert 'js/app.js' in rendered


def test_base_template_has_dark_mode(app):
    """Test that base template has dark mode class."""
    with app.test_request_context():
        from flask import render_template_string

        template = """
        {% extends "base.html" %}
        {% block content %}{% endblock %}
        """
        rendered = render_template_string(template)

        assert 'class="dark"' in rendered


def test_base_template_has_flexbox_layout(app):
    """Test that base template uses flexbox layout for footer positioning."""
    with app.test_request_context():
        from flask import render_template_string

        template = """
        {% extends "base.html" %}
        {% block content %}{% endblock %}
        """
        rendered = render_template_string(template)

        # Check for flexbox classes
        assert 'flex flex-col' in rendered
        assert 'flex-grow' in rendered


def test_base_template_footer_year_is_dynamic(app):
    """Test that footer year is dynamically generated."""
    with app.test_request_context():
        from flask import render_template_string

        template = """
        {% extends "base.html" %}
        {% block content %}{% endblock %}
        """
        rendered = render_template_string(template)

        current_year = str(datetime.now().year)
        assert f"&copy; {current_year}" in rendered


def test_base_template_menu_judge_branding(app):
    """Test that Menu Judge branding is present."""
    with app.test_request_context():
        from flask import render_template_string

        template = """
        {% extends "base.html" %}
        {% block content %}{% endblock %}
        """
        rendered = render_template_string(template)

        assert "Menu Judge" in rendered


def test_base_template_blocks_are_extendable(app):
    """Test that all template blocks can be extended."""
    with app.test_request_context():
        from flask import render_template_string

        template = """
        {% extends "base.html" %}
        {% block title %}Custom Title{% endblock %}
        {% block head %}<meta name="custom" content="test">{% endblock %}
        {% block content %}<div id="test-content">Test</div>{% endblock %}
        {% block scripts %}<script>console.log('test');</script>{% endblock %}
        """
        rendered = render_template_string(template)

        assert "Custom Title" in rendered
        assert '<meta name="custom" content="test">' in rendered
        assert '<div id="test-content">Test</div>' in rendered
        assert "console.log('test')" in rendered
