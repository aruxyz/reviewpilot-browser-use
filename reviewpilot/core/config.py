from pathlib import Path
from typing import Any, Literal

import yaml
from pydantic import BaseModel, Field, model_validator


class Viewport(BaseModel):
    name: str
    width: int = Field(ge=320, le=3840)
    height: int = Field(ge=240, le=2160)


class Journey(BaseModel):
    name: str
    goal: str
    url: str | None = None
    viewport: str | None = None
    max_steps: int | None = None
    timeout_seconds: int | None = None


class ChecksConfig(BaseModel):
    ux: bool = True
    broken_links: bool = True
    forms: bool = True
    mobile_layout: bool = True
    accessibility_basic: bool = True
    console_errors: bool = True


class OutputConfig(BaseModel):
    markdown: bool = True
    html: bool = True
    screenshots: bool = True
    github_comment: bool = False
    output_dir: str = ".reviewpilot-output"


class SafetyConfig(BaseModel):
    safe_mode: bool = True
    allow_form_submit: bool = False
    allow_destructive_actions: bool = False
    redact_secrets: bool = True


class BrowserUseConfig(BaseModel):
    enabled: bool = True
    task_model: str = "bu-latest"
    planner_model: str | None = None
    headless: bool = True
    use_vision: bool | Literal["auto"] = True
    save_conversation_path: str | None = None


class ReviewConfig(BaseModel):
    mode: Literal["pull_request", "local", "ci"] = "local"
    max_steps: int = Field(default=30, ge=1, le=500)
    timeout_seconds: int = Field(default=180, ge=10, le=3600)


class AppConfig(BaseModel):
    name: str = "ReviewPilot Demo"
    url: str = "https://review-pilot-demo.vercel.app"


class ReviewPilotConfig(BaseModel):
    app: AppConfig = Field(default_factory=AppConfig)
    review: ReviewConfig = Field(default_factory=ReviewConfig)
    browser_use: BrowserUseConfig = Field(default_factory=BrowserUseConfig)
    viewports: list[Viewport] = Field(
        default_factory=lambda: [
            Viewport(name="desktop", width=1440, height=900),
            Viewport(name="mobile", width=390, height=844),
        ]
    )
    journeys: list[Journey] = Field(default_factory=list)
    checks: ChecksConfig = Field(default_factory=ChecksConfig)
    output: OutputConfig = Field(default_factory=OutputConfig)
    safety: SafetyConfig = Field(default_factory=SafetyConfig)

    @model_validator(mode="after")
    def _ensure_journey_defaults(self) -> "ReviewPilotConfig":
        viewport_names = {v.name for v in self.viewports}
        for journey in self.journeys:
            if journey.viewport is not None and journey.viewport not in viewport_names:
                raise ValueError(
                    f"Journey '{journey.name}' references unknown viewport '{journey.viewport}'."
                )
        return self

    @property
    def output_path(self) -> Path:
        return Path(self.output.output_dir)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ReviewPilotConfig":
        return cls.model_validate(data)

    @classmethod
    def from_yaml_file(cls, path: Path | str) -> "ReviewPilotConfig":
        path_obj = Path(path)
        if not path_obj.exists():
            raise FileNotFoundError(f"Config file not found: {path_obj}")
        with open(path_obj, "r", encoding="utf-8") as fh:
            data = yaml.safe_load(fh) or {}
        return cls.from_dict(data)

    @classmethod
    def from_yaml_string(cls, text: str) -> "ReviewPilotConfig":
        data = yaml.safe_load(text) or {}
        return cls.from_dict(data)

    def to_yaml(self) -> str:
        return yaml.safe_dump(self.model_dump(mode="json"), sort_keys=False, allow_unicode=True)


DEFAULT_CONFIG_YAML = """\
app:
  name: "ReviewPilot Demo"
  url: "https://review-pilot-demo.vercel.app"

review:
  mode: "local"
  max_steps: 30
  timeout_seconds: 180

browser_use:
  enabled: true
  task_model: "bu-latest"
  planner_model: "bu-latest"
  headless: true

viewports:
  - name: "desktop"
    width: 1440
    height: 900
  - name: "mobile"
    width: 390
    height: 844

journeys:
  - name: "Homepage review"
    goal: "Open the homepage and check whether the primary navigation, hero section, and main CTA are visible and usable."

  - name: "Login flow"
    goal: "Open the login page, inspect the form, test basic validation behavior, and verify that the user can understand what to do."

  - name: "Navigation flow"
    goal: "Explore the main navigation and check whether important links are reachable and not broken."

checks:
  ux: true
  broken_links: true
  forms: true
  mobile_layout: true
  accessibility_basic: true
  console_errors: true

output:
  markdown: true
  html: true
  screenshots: true
  github_comment: false
  output_dir: ".reviewpilot-output"

safety:
  safe_mode: true
  allow_form_submit: false
  allow_destructive_actions: false
  redact_secrets: true
"""
