from __future__ import annotations

from pathlib import Path
from typing import Any

from browser_use import (
    Agent,
    Browser,
    BrowserProfile,
    ChatAnthropic,
    ChatBrowserUse,
    ChatGoogle,
    ChatOpenAI,
)

from reviewpilot.core.config import BrowserUseConfig, Journey, Viewport


class LLMFactory:
    _MAPPING = {
        "gpt": ChatOpenAI,
        "o1": ChatOpenAI,
        "o3": ChatOpenAI,
        "claude": ChatAnthropic,
        "gemini": ChatGoogle,
        "bu-": ChatBrowserUse,
    }

    @classmethod
    def build(cls, model: str) -> Any:
        if not model:
            raise ValueError("task_model must be a non-empty string")
        for prefix, chat_cls in cls._MAPPING.items():
            if model.startswith(prefix):
                return chat_cls(model=model)
        return ChatOpenAI(model=model)


def build_browser(viewport: Viewport, headless: bool) -> Browser:
    profile = BrowserProfile(
        headless=headless,
        viewport={"width": viewport.width, "height": viewport.height},
        window_size={"width": viewport.width, "height": viewport.height},
        keep_alive=False,
        args=["--disable-blink-features=AutomationControlled"],
    )
    return Browser(browser_profile=profile)


def build_task_prompt(journey: Journey, app_url: str, viewport: Viewport, safe_mode: bool) -> str:
    target_url = journey.url or app_url
    safety_clause = (
        "Safety rules:\n"
        "- Do NOT submit any form (read-only review).\n"
        "- Do NOT create, update, or delete real data.\n"
        "- Do NOT make purchases or payments.\n"
        "- Do NOT authenticate with real credentials.\n"
        "- Do NOT click destructive buttons (delete, remove, reset).\n"
        "- If a form is present, inspect it but do not submit.\n"
        if safe_mode
        else "Safety rules:\n- Avoid destructive actions when possible.\n"
    )
    return (
        f"You are a senior QA engineer reviewing a live web application.\n\n"
        f"Target URL: {target_url}\n"
        f"Viewport: {viewport.name} ({viewport.width}x{viewport.height})\n\n"
        f"Journey: {journey.name}\n"
        f"Goal: {journey.goal}\n\n"
        f"{safety_clause}"
        f"Observation requirements:\n"
        f"- Report broken UI, confusing UX, missing elements, layout overflow.\n"
        f"- Report buttons that are disabled or do nothing when clicked.\n"
        f"- Report forms with unclear validation or missing error indicators.\n"
        f"- Report links that lead to 404 or broken pages.\n"
        f"- Report elements hidden below the fold on small viewports.\n"
        f"- Report any console errors you observe.\n"
        f"- For every issue, note the page URL and a short reproduction hint.\n"
        f"- Capture a screenshot whenever you observe an issue.\n\n"
        f"Return a concise summary of what you found, including which checks passed.\n"
    )


class BrowserUseRunner:
    def __init__(self, config: BrowserUseConfig, output_dir: Path):
        self._config = config
        self._output_dir = output_dir
        self._run_dir = output_dir / "runs"
        self._run_dir.mkdir(parents=True, exist_ok=True)

    async def run_journey(
        self,
        journey: Journey,
        app_url: str,
        viewport: Viewport,
        max_steps: int,
        timeout_seconds: int,
    ) -> dict[str, Any]:
        if not self._config.enabled:
            return {
                "name": journey.name,
                "goal": journey.goal,
                "viewport": viewport.name,
                "status": "skipped",
                "reason": "browser_use.enabled is false",
            }

        task_llm = LLMFactory.build(self._config.task_model)
        planner_llm = (
            LLMFactory.build(self._config.planner_model)
            if self._config.planner_model
            else None
        )

        browser = build_browser(viewport, self._config.headless)
        task = build_task_prompt(journey, app_url, viewport, safe_mode=True)

        journey_slug = journey.name.lower().replace(" ", "-").replace("/", "-")
        conversation_dir = self._run_dir / f"{journey_slug}-{viewport.name}"

        agent_kwargs: dict[str, Any] = dict(
            task=task,
            llm=task_llm,
            browser=browser,
            use_vision=self._config.use_vision,
            max_actions_per_step=5,
            max_failures=3,
            save_conversation_path=str(conversation_dir),
            extend_system_message=(
                "You are reviewing a web app for QA issues. Be precise and evidence-driven. "
                "Prefer observing over interacting. Never submit forms."
            ),
        )
        if planner_llm is not None:
            agent_kwargs["page_extraction_llm"] = planner_llm

        agent = Agent(**agent_kwargs)

        try:
            history = await agent.run(max_steps=max_steps)
        finally:
            try:
                await agent.kill()
            except Exception:
                pass
            try:
                await browser.close()
            except Exception:
                pass

        return {
            "name": journey.name,
            "goal": journey.goal,
            "viewport": viewport.name,
            "final_result": history.final_result() or "",
            "is_done": history.is_done(),
            "is_successful": history.is_successful(),
            "errors": [e for e in history.errors() if e],
            "urls": [u for u in history.urls() if u],
            "actions": history.action_names(),
            "screenshot_paths": [p for p in history.screenshot_paths() if p],
            "steps": history.number_of_steps(),
            "duration_seconds": history.total_duration_seconds(),
            "history_file": str(conversation_dir / "history.json"),
        }
