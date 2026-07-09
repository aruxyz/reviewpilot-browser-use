from reviewpilot.core.config import ReviewPilotConfig
from reviewpilot.core.severity import Severity


def test_default_config_validates():
    config = ReviewPilotConfig()
    assert config.app.name == "My App"
    assert config.app.url == "http://localhost:3000"
    assert len(config.viewports) == 2
    assert config.viewports[0].name == "desktop"
    assert config.viewports[1].name == "mobile"
    assert config.review.max_steps == 30
    assert config.safety.safe_mode is True


def test_config_from_yaml_string():
    yaml = """
app:
  name: "Test App"
  url: "https://preview.test.com"
review:
  max_steps: 50
  timeout_seconds: 300
browser_use:
  task_model: "claude-sonnet-4-5"
  headless: false
journeys:
  - name: "Home"
    goal: "Check homepage"
    viewport: "mobile"
"""
    config = ReviewPilotConfig.from_yaml_string(yaml)
    assert config.app.name == "Test App"
    assert config.app.url == "https://preview.test.com"
    assert config.review.max_steps == 50
    assert config.browser_use.task_model == "claude-sonnet-4-5"
    assert config.browser_use.headless is False
    assert len(config.journeys) == 1
    assert config.journeys[0].viewport == "mobile"


def test_config_rejects_unknown_viewport_in_journey():
    import pytest

    yaml = """
viewports:
  - name: "desktop"
    width: 1280
    height: 720
journeys:
  - name: "Home"
    goal: "Check"
    viewport: "nonexistent"
"""
    with pytest.raises(Exception):
        ReviewPilotConfig.from_yaml_string(yaml)


def test_config_to_yaml_roundtrip():
    config = ReviewPilotConfig()
    config.app.name = "Roundtrip App"
    yaml_text = config.to_yaml()
    assert "Roundtrip App" in yaml_text
    config2 = ReviewPilotConfig.from_yaml_string(yaml_text)
    assert config2.app.name == "Roundtrip App"
