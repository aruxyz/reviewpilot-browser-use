from reviewpilot.browser.browser_use_runner import LLMFactory, build_task_prompt
from reviewpilot.core.config import Journey, Viewport


def test_llm_factory_openai():
    llm = LLMFactory.build("gpt-4.1-mini")
    assert llm.__class__.__name__ == "ChatOpenAI"


def test_llm_factory_anthropic():
    llm = LLMFactory.build("claude-sonnet-4-5")
    assert llm.__class__.__name__ == "ChatAnthropic"


def test_llm_factory_google():
    llm = LLMFactory.build("gemini-2.5-flash")
    assert llm.__class__.__name__ == "ChatGoogle"


def test_llm_factory_browser_use(monkeypatch):
    monkeypatch.setenv("BROWSER_USE_API_KEY", "bu-test-dummy")
    llm = LLMFactory.build("bu-2-0")
    assert llm.__class__.__name__ == "ChatBrowserUse"


def test_llm_factory_falls_back_to_openai():
    llm = LLMFactory.build("unknown-model-name")
    assert llm.__class__.__name__ == "ChatOpenAI"


def test_llm_factory_rejects_empty():
    import pytest

    with pytest.raises(ValueError):
        LLMFactory.build("")


def test_build_task_prompt_includes_safety_rules():
    journey = Journey(name="Homepage", goal="Check the homepage")
    viewport = Viewport(name="mobile", width=390, height=844)
    prompt = build_task_prompt(journey, "https://preview.example.com", viewport, safe_mode=True)
    assert "Do NOT submit any form" in prompt
    assert "https://preview.example.com" in prompt
    assert "mobile" in prompt
    assert "390x844" in prompt
    assert "Homepage" in prompt


def test_build_task_prompt_safe_mode_off():
    journey = Journey(name="Home", goal="Check")
    viewport = Viewport(name="desktop", width=1440, height=900)
    prompt = build_task_prompt(journey, "http://localhost:3000", viewport, safe_mode=False)
    assert "Do NOT submit any form" not in prompt
    assert "Avoid destructive actions" in prompt


def test_build_task_prompt_uses_journey_url_when_provided():
    journey = Journey(name="Login", goal="Check login", url="http://localhost:3000/login")
    viewport = Viewport(name="desktop", width=1440, height=900)
    prompt = build_task_prompt(journey, "http://localhost:3000", viewport, safe_mode=True)
    assert "http://localhost:3000/login" in prompt
