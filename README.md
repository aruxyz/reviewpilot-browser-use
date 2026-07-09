<div align="center">

# ReviewPilot

AI browser QA for every Pull Request, powered by Browser Use.

ReviewPilot opens your deployed preview, explores your app like a real user, detects obvious UX and functional issues, captures screenshots as evidence, and posts a human-readable review comment back to your Pull Request.

[Quickstart](#quickstart) | [GitHub Action](#github-action) | [Configuration](#configuration) | [Demo](#demo) | [How It Works](#how-it-works)

</div>

---

## Table of Contents

1. [What It Is](#what-it-is)
2. [Why It Exists](#why-it-exists)
3. [What It Is Not](#what-it-is-not)
4. [Quickstart](#quickstart)
5. [GitHub Action](#github-action)
6. [Configuration](#configuration)
7. [CLI Reference](#cli-reference)
8. [How It Works](#how-it-works)
9. [Report Format](#report-format)
10. [Severity Levels](#severity-levels)
11. [Safety](#safety)
12. [Demo](#demo)
13. [Architecture](#architecture)
14. [Troubleshooting](#troubleshooting)
15. [FAQ](#faq)
16. [Comparison With Other Tools](#comparison-with-other-tools)
17. [Contributing](#contributing)
18. [License](#license)

---

## What It Is

ReviewPilot is an open-source CLI and GitHub Action that uses [Browser Use](https://github.com/browser-use/browser-use) as its core browser automation engine. It inspects deployed Pull Request previews, identifies user-facing issues, collects evidence, and generates human-readable QA review comments.

The product value comes from the combination of:

```
Pull Request context
        +
Deploy preview URL
        +
Browser Use autonomous browsing
        +
LLM judgement
        +
GitHub PR feedback
```

Browser Use is the browser intelligence engine. ReviewPilot is the PR review product built around it. Browser Use is not a branding detail or a thin wrapper. It is the reason ReviewPilot can navigate and inspect apps autonomously without you writing brittle selectors or test scripts.

---

## Why It Exists

Modern teams already have code review, linting, unit tests, and sometimes E2E tests. Many bugs still escape because reviewers rarely test the actual running application carefully.

A human reviewer may approve a Pull Request without noticing that:

- the mobile layout is broken,
- a primary CTA is hidden below the fold,
- a form button silently stays disabled,
- a page still loads but the flow feels confusing,
- a visual element disappeared,
- the implementation technically works but does not behave like a user expects.

ReviewPilot closes that gap. It acts like a lightweight AI QA reviewer that opens the deployed preview of a Pull Request, navigates it using Browser Use, observes the interface, captures evidence, reasons about user-facing problems, and posts a useful review back to GitHub.

It does not replace Playwright, Cypress, or human QA. It catches the obvious and painful issues that humans often miss because they do not manually browse every Pull Request.

---

## What It Is Not

ReviewPilot v1 is deliberately narrow. It is **not**:

- a SaaS dashboard,
- a billing platform,
- a user account system,
- a database-backed analytics tool,
- a self-healing selector engine,
- a full Playwright replacement,
- an enterprise permission system,
- a browser farm infrastructure.

It is a high-quality developer tool that should feel like a thoughtful senior QA engineer reviewed your Pull Request, not an unfinished platform.

---

## Quickstart

### 1. Install

```bash
pip install reviewpilot
playwright install chromium
```

ReviewPilot requires Python 3.10 or newer. The `playwright install chromium` command downloads the Chromium binary that Browser Use will drive. This is a one-time download of approximately 150 MB.

### 2. Set an LLM API key

ReviewPilot needs an LLM to drive Browser Use and to judge the results. Set one environment variable:

```bash
# Pick one provider:
export OPENAI_API_KEY=sk-...
# or
export ANTHROPIC_API_KEY=sk-ant-...
# or
export GOOGLE_API_KEY=...
# or
export BROWSER_USE_API_KEY=bu-...
```

The default config uses `gpt-4.1-mini` from OpenAI because it is cheap and fast for QA work. You can switch providers in the config file.

### 3. Initialize config

```bash
reviewpilot init
```

This creates `.reviewpilot.yml` in your current directory with sensible defaults. Edit it to set your app URL, journeys, and viewports.

### 4. Run a review

Start your local dev server in one terminal:

```bash
npm run dev   # or yarn dev, pnpm dev, etc.
```

Run ReviewPilot in another terminal:

```bash
reviewpilot run --url http://localhost:3000
```

Or use your config file:

```bash
reviewpilot run --config .reviewpilot.yml
```

### 5. View the report

```bash
reviewpilot report
```

This opens the HTML report in your default browser. You will also find `review.md`, `review.json`, and a `screenshots/` directory inside `.reviewpilot-output/`.

### 6. Check your environment

If anything feels off, run the doctor command:

```bash
reviewpilot doctor
```

It checks your Python version, installed packages, browser availability, and API keys. It prints a clear pass/fail report.

---

## GitHub Action

ReviewPilot ships as a Docker-based GitHub Action. Add it to a workflow that triggers on Pull Request events, point it at your deploy preview URL, and it will post a review comment on the PR.

### Minimal example

```yaml
# .github/workflows/reviewpilot.yml
name: ReviewPilot

on:
  pull_request:
    types: [opened, synchronize, reopened]

permissions:
  contents: read
  pull-requests: write

jobs:
  review:
    runs-on: ubuntu-latest
    if: github.event.pull_request.head.repo.full_name == github.repository
    steps:
      - uses: actions/checkout@v4

      - name: Wait for preview deploy
        run: |
          echo "Set PREVIEW_URL from your deploy preview (Vercel, Netlify, etc.)"
          # echo "PREVIEW_URL=https://preview-${{ github.event.pull_request.number }}.yourapp.dev" >> $GITHUB_ENV

      - name: Run ReviewPilot
        uses: ./.github/actions/reviewpilot
        with:
          preview-url: ${{ env.PREVIEW_URL }}
          github-token: ${{ github.token }}
          max-steps: '30'
          timeout-seconds: '180'

      - name: Upload report artifacts
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: reviewpilot-report-${{ github.event.pull_request.number }}
          path: reviewpilot-output/
          retention-days: 14
```

### Vercel preview deploy example

If you use Vercel, wire up the preview URL from the Vercel preview deployment:

```yaml
name: ReviewPilot

on:
  deployment_status:

permissions:
  contents: read
  pull-requests: write

jobs:
  review:
    runs-on: ubuntu-latest
    if: github.event.deployment_status.state == 'success' && github.event.deployment.environment == 'Preview'
    steps:
      - uses: actions/checkout@v4
        with:
          ref: ${{ github.event.deployment.ref }}

      - name: Run ReviewPilot on Vercel preview
        uses: ./.github/actions/reviewpilot
        with:
          preview-url: ${{ github.event.deployment_status.target_url }}
          github-token: ${{ github.token }}
```

### Netlify preview deploy example

```yaml
name: ReviewPilot

on:
  pull_request:
    types: [opened, synchronize, reopened]

permissions:
  contents: read
  pull-requests: write

jobs:
  review:
    runs-on: ubuntu-latest
    if: github.event.pull_request.head.repo.full_name == github.repository
    steps:
      - uses: actions/checkout@v4

      - name: Wait for Netlify deploy
        uses: jwalton/gh-find-current-pr@v1
        id: finder

      - name: Get Netlify preview URL
        id: netlify
        run: |
          # Use your Netlify webhook or API to fetch the preview URL
          echo "PREVIEW_URL=https://deploy-preview-${{ steps.finder.outputs.pr }}--yourapp.netlify.app" >> $GITHUB_ENV

      - name: Run ReviewPilot
        uses: ./.github/actions/reviewpilot
        with:
          preview-url: ${{ env.PREVIEW_URL }}
          github-token: ${{ github.token }}
```

### Action inputs

| Input | Default | Description |
|---|---|---|
| `preview-url` | _(required)_ | URL of the deployed preview to review. |
| `github-token` | `${{ github.token }}` | Token for posting PR comments. Use the auto-injected token by default. |
| `config-path` | `.reviewpilot.yml` | Path to your config file, relative to the repo root. |
| `max-steps` | `30` | Maximum browser steps per journey. Caps LLM cost. |
| `timeout-seconds` | `180` | Per-journey timeout in seconds. |

### Action outputs

| Output | Description |
|---|---|
| `status` | Review status: `passed`, `failed`, `errored`, or `skipped`. |
| `findings-count` | Total number of findings across all journeys. |

### Required permissions

The workflow must declare these permissions:

```yaml
permissions:
  contents: read          # to checkout the repo
  pull-requests: write    # to post PR comments and reviews
```

### Fork Pull Requests

Pull Requests from forks cannot post comments because the auto-injected `GITHUB_TOKEN` has read-only permissions on forks. The example workflows above use this guard to skip fork PRs:

```yaml
if: github.event.pull_request.head.repo.full_name == github.repository
```

To support fork PRs, you need a split-workflow pattern using the `workflow_run` trigger. The analysis workflow runs on the fork PR and uploads results as an artifact. A second workflow triggered by `workflow_run` downloads the artifact and posts the comment using the repository's own token. This pattern is documented in the [GitHub Actions security guide](https://docs.github.com/en/actions/security-guides/security-hardening-for-github-actions).

### Comment deduplication

ReviewPilot embeds a hidden marker (`<!-- reviewpilot:v1 -->`) in every comment it posts. On subsequent runs, it finds the existing comment and updates it in place instead of posting a duplicate. This keeps the PR conversation clean even when the preview is redeployed multiple times.

---

## Configuration

ReviewPilot reads its behavior from `.reviewpilot.yml`. Run `reviewpilot init` to create a default config, then edit it.

### Full example with annotations

```yaml
app:
  name: "My App"                    # shown in report headers
  url: "https://preview.example.com" # default target URL

review:
  mode: "pull_request"              # pull_request | local | ci
  max_steps: 30                     # max browser steps per journey
  timeout_seconds: 180              # per-journey wall clock timeout

browser_use:
  enabled: true                     # set false to skip browser runs (debugging)
  task_model: "gpt-4.1-mini"        # model that drives the browser agent
  planner_model: "gpt-4.1-mini"     # optional secondary model for page extraction
  headless: true                    # set false to watch the browser locally
  use_vision: true                  # send screenshots to the LLM (true | false | "auto")

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
    # url: "/login"                 # optional, overrides app.url for this journey
    # viewport: "mobile"            # optional, restricts to one viewport
    # max_steps: 20                 # optional, overrides review.max_steps
    # timeout_seconds: 120          # optional, overrides review.timeout_seconds

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
  markdown: true                    # generate review.md
  html: true                        # generate review.html
  screenshots: true                 # copy screenshots into output dir
  github_comment: false             # set true only inside the action
  output_dir: ".reviewpilot-output" # where artifacts are written

safety:
  safe_mode: true                   # enforce read-only review
  allow_form_submit: false          # do not submit forms
  allow_destructive_actions: false  # do not delete or modify data
  redact_secrets: true              # scrub secrets from reports
```

### Field reference

#### `app`

| Field | Type | Default | Description |
|---|---|---|---|
| `name` | string | `"My App"` | Display name shown in report headers. |
| `url` | string | `"http://localhost:3000"` | Default target URL. Overridden by `--url` or journey `url`. |

#### `review`

| Field | Type | Default | Description |
|---|---|---|---|
| `mode` | string | `"local"` | One of `local`, `pull_request`, `ci`. Affects output formatting. |
| `max_steps` | int | `30` | Maximum browser steps per journey. Range 1 to 500. |
| `timeout_seconds` | int | `180` | Per-journey timeout in seconds. Range 10 to 3600. |

#### `browser_use`

| Field | Type | Default | Description |
|---|---|---|---|
| `enabled` | bool | `true` | Set `false` to skip browser runs (useful for debugging reports). |
| `task_model` | string | `"gpt-4.1-mini"` | LLM that drives the Browser Use agent. |
| `planner_model` | string | `null` | Optional secondary LLM for page extraction. |
| `headless` | bool | `true` | Run browser without UI. Set `false` to watch locally. |
| `use_vision` | bool or `"auto"` | `true` | Send screenshots to the LLM. `"auto"` uses vision only when the model asks. |

#### `viewports`

A list of viewport definitions. Each journey runs on every viewport unless you pin it with the `viewport` field.

| Field | Type | Default | Description |
|---|---|---|---|
| `name` | string | _(required)_ | Human-readable name, shown in reports. |
| `width` | int | _(required)_ | Viewport width in pixels. Range 320 to 3840. |
| `height` | int | _(required)_ | Viewport height in pixels. Range 240 to 2160. |

#### `journeys`

A list of QA goals for the browser agent to execute.

| Field | Type | Default | Description |
|---|---|---|---|
| `name` | string | _(required)_ | Short journey name, shown in reports. |
| `goal` | string | _(required)_ | Natural language instruction for the agent. |
| `url` | string | `null` | Optional URL for this journey. Defaults to `app.url`. |
| `viewport` | string | `null` | Optional viewport name. Defaults to all configured viewports. |
| `max_steps` | int | `null` | Optional override of `review.max_steps`. |
| `timeout_seconds` | int | `null` | Optional override of `review.timeout_seconds`. |

#### `checks`

Boolean toggles for which categories the agent should look for. These are passed to the agent prompt as hints.

| Field | Default | Description |
|---|---|---|
| `ux` | `true` | General usability issues. |
| `broken_links` | `true` | Links that lead to 404 or error pages. |
| `forms` | `true` | Form validation, disabled buttons, unclear errors. |
| `mobile_layout` | `true` | Layout overflow, hidden CTAs, mobile-specific issues. |
| `accessibility_basic` | `true` | Missing labels, contrast, focus indicators. |
| `console_errors` | `true` | JavaScript errors logged to the console. |

#### `output`

| Field | Type | Default | Description |
|---|---|---|---|
| `markdown` | bool | `true` | Generate `review.md`. |
| `html` | bool | `true` | Generate `review.html`. |
| `screenshots` | bool | `true` | Copy screenshots into the output directory. |
| `github_comment` | bool | `false` | Post a comment to the PR. Only relevant inside the action. |
| `output_dir` | string | `".reviewpilot-output"` | Where artifacts are written. |

#### `safety`

| Field | Type | Default | Description |
|---|---|---|---|
| `safe_mode` | bool | `true` | Master switch for safety rules. |
| `allow_form_submit` | bool | `false` | Allow the agent to submit forms. |
| `allow_destructive_actions` | bool | `false` | Allow delete, reset, or other destructive actions. |
| `redact_secrets` | bool | `true` | Scrub API keys, tokens, and passwords from reports. |

### Supported LLM models

Any model supported by Browser Use works. Set the model name in `browser_use.task_model`. The provider prefix in the model name decides which chat class is used.

| Provider | Example models | Env var |
|---|---|---|
| OpenAI | `gpt-4.1-mini`, `gpt-4o`, `gpt-4.1` | `OPENAI_API_KEY` |
| Anthropic | `claude-sonnet-4-5`, `claude-opus-4-1`, `claude-haiku-3-5` | `ANTHROPIC_API_KEY` |
| Google | `gemini-2.5-flash`, `gemini-2.5-pro` | `GOOGLE_API_KEY` |
| Browser Use | `bu-2-0`, `bu-latest` | `BROWSER_USE_API_KEY` |

ReviewPilot maps the model name to the right chat class automatically. If the model name does not match any known prefix, it falls back to `ChatOpenAI` (which works with any OpenAI-compatible endpoint).

### Writing good journey goals

The journey `goal` is the most important field. It is the natural language instruction the Browser Use agent follows. Good goals are specific, observable, and safe.

Good:

```yaml
- name: "Homepage CTA visibility"
  goal: "Open the homepage on mobile and check whether the primary CTA button is visible without scrolling. Report if it is below the fold."
```

Bad (too vague):

```yaml
- name: "Check the homepage"
  goal: "See if the homepage is good."
```

Bad (encourages unsafe actions):

```yaml
- name: "Test checkout"
  goal: "Buy a product to make sure checkout works."
```

ReviewPilot injects safety rules into every prompt. Even with a bad goal, the agent will refuse to submit forms or make purchases in safe mode. But clear goals produce better findings.

---

## CLI Reference

ReviewPilot exposes four commands.

### `reviewpilot init`

Creates a default `.reviewpilot.yml` in the current directory.

```bash
reviewpilot init
reviewpilot init --force   # overwrite existing config
```

### `reviewpilot run`

Runs a review against a URL or config file.

```bash
reviewpilot run --url http://localhost:3000
reviewpilot run --config .reviewpilot.yml
reviewpilot run --url http://localhost:3000 --headed      # watch the browser
reviewpilot run --config .reviewpilot.yml --max-steps 50  # override config
reviewpilot run --config .reviewpilot.yml --output-dir ./reports
```

Exit codes:

| Code | Meaning |
|---|---|
| `0` | Review passed, no findings. |
| `1` | Review failed, findings reported. |
| `2` | Review errored, could not complete. |
| `130` | Interrupted by user (Ctrl+C). |

### `reviewpilot report`

Opens the latest HTML report from the output directory.

```bash
reviewpilot report
reviewpilot report --path .reviewpilot-output
reviewpilot report --no-open   # print paths only, do not open browser
```

### `reviewpilot doctor`

Checks your environment setup: Python version, installed packages, browser availability, and API keys.

```bash
reviewpilot doctor
```

It exits with code `0` if everything passes, `1` if anything fails.

---

## How It Works

ReviewPilot runs a pipeline for every Pull Request:

```
Pull Request opened
        |
        v
GitHub Action starts
        |
        v
ReviewPilot reads .reviewpilot.yml
        |
        v
ReviewPilot receives preview URL from action input
        |
        v
For each journey:
   For each viewport:
      Browser Use opens the deployed app
             |
             v
      Browser Use explores the journey goal autonomously
             |
             v
      Agent captures screenshots, URLs, actions, errors
             |
             v
      LLM judge reviews behavior and evidence
             |
             v
      Judge produces structured findings with severity
        |
        v
ReviewPilot aggregates findings across all journeys
        |
        v
ReviewPilot generates Markdown report (for PR comment)
        |
        v
ReviewPilot generates HTML report (for local review)
        |
        v
ReviewPilot generates JSON report (for programmatic use)
        |
        v
GitHub bot posts or updates the PR review comment
```

### Per-journey flow

For each journey, ReviewPilot:

1. Builds a QA-focused prompt that includes the target URL, viewport, journey goal, and safety rules.
2. Creates a Browser Use `Agent` with the prompt, the configured LLM, and a `Browser` configured for the viewport and headless mode.
3. Calls `agent.run(max_steps=N)` which returns an `AgentHistoryList`.
4. Extracts visited URLs, actions taken, errors, screenshots, and the final result from the history.
5. Passes the observations to an LLM judge that produces structured findings (severity, expected vs actual, why it matters, reproduction steps, suggested fix).
6. Maps the structured findings to ReviewPilot's `Finding` model and attaches them to a `JourneyResult`.
7. Saves screenshots into the output directory for evidence.

### Aggregation

After all journeys complete, ReviewPilot:

1. Aggregates findings across journeys.
2. Computes overall status (`passed`, `failed`, `errored`) based on finding severities and journey statuses.
3. Generates a Markdown report matching the PRD format for GitHub comments.
4. Generates an HTML report with a dark theme for local review.
5. Generates a JSON report for programmatic consumption.
6. If `output.github_comment` is true, posts or updates the PR comment using PyGithub.

---

## Report Format

ReviewPilot generates three report files in the output directory.

### `review.md`

A Markdown report designed for PR comments. Example:

```markdown
<!-- reviewpilot:v1 -->
## ReviewPilot Browser QA Report

Review target: https://preview.example.com
Status: Failed
Journeys reviewed: 3
Issues found: 1 high, 2 medium

### High Priority

#### 1. Primary CTA is hidden below the fold on mobile

Page: `/`
Viewport: mobile

Expected:
The primary CTA should be visible without scrolling.

Actual:
The CTA is pushed below the fold by excessive hero spacing.

Why it matters:
Users may not understand the main action they are supposed to take.

Evidence:
`screenshots/homepage-mobile-01.png`

Suggested fix:
Reduce hero vertical spacing on mobile or move the CTA above the fold.

---

### Passed Checks

- Desktop homepage layout is usable.
- Main navigation links are reachable.
- Login form validation appears understandable.

Generated by ReviewPilot, powered by Browser Use.
```

The hidden `<!-- reviewpilot:v1 -->` marker lets ReviewPilot find and update the existing comment on subsequent runs instead of posting duplicates.

### `review.html`

A dark-themed HTML report with the same content, styled for local review. Open it with `reviewpilot report`.

### `review.json`

A machine-readable JSON dump of the full `ReviewReport` model. Useful for piping into other tools, dashboards, or CI checks.

```json
{
  "app_name": "My App",
  "app_url": "https://preview.example.com",
  "status": "failed",
  "journeys": [
    {
      "name": "Homepage review",
      "goal": "...",
      "viewport": "mobile",
      "status": "failed",
      "findings": [
        {
          "severity": "high",
          "title": "Primary CTA is hidden below the fold on mobile",
          "page": "/",
          "viewport": "mobile",
          "expected": "...",
          "actual": "...",
          "why_it_matters": "...",
          "reproduction_steps": ["..."],
          "evidence": ["screenshots/homepage-mobile-01.png"],
          "suggested_fix": "..."
        }
      ],
      "steps": 12,
      "duration_seconds": 45.3
    }
  ],
  "total_duration_seconds": 45.3
}
```

### `screenshots/`

A directory of PNG screenshots captured by Browser Use during the run. Filenames follow the pattern `{journey-slug}-{viewport}-{index}.png`.

### `manifest.json`

A small metadata file with the run summary (app name, URL, journey count, status, timestamps).

---

## Severity Levels

ReviewPilot uses four severity levels.

| Severity | Description | Examples |
|---|---|---|
| **Critical** | The user cannot complete an important flow. | Login impossible, checkout cannot proceed, main page crashes, navigation completely broken. |
| **High** | The user can continue, but the issue seriously damages usability. | Primary CTA hidden, form validation unclear, mobile layout blocks important actions, key button does nothing. |
| **Medium** | The issue is noticeable but not blocking. | Minor layout overflow, inconsistent spacing, missing empty state, weak visual hierarchy. |
| **Low** | Small polish issues. | Minor copy issue, slight alignment problem, non-critical console warning. |

The overall review status is:

- `passed` if there are no findings,
- `failed` if there are any findings,
- `errored` if any journey itself broke (timeout, agent crash).

High and critical findings are always blocking. Medium and low findings are reported but do not fail the review on their own unless the judge marks the journey as failed.

---

## Safety

Browser agents can interact with real websites, so ReviewPilot is safe by default.

### Safe mode rules

When `safety.safe_mode` is true (the default), the agent prompt includes these rules:

- Do NOT submit any form (read-only review).
- Do NOT create, update, or delete real data.
- Do NOT make purchases or payments.
- Do NOT authenticate with real credentials.
- Do NOT click destructive buttons (delete, remove, reset).
- If a form is present, inspect it but do not submit.

The agent is instructed to observe rather than interact. This means it will not catch issues that only appear after a form submit (for example, a post-submit error message). This is a deliberate tradeoff for safety.

### Secret redaction

When `safety.redact_secrets` is true (the default), ReviewPilot scrubs the following from reports:

- API keys (`sk-...`, `bu-...`, etc.)
- Access tokens
- Passwords
- Cookies
- Authorization headers
- Private environment variables

### Overriding safety

You can disable safe mode in the config:

```yaml
safety:
  safe_mode: false
  allow_form_submit: true
  allow_destructive_actions: true
```

This is strongly discouraged for PR reviews. Only disable safe mode for local testing against a staging environment with fake data.

---

## Demo

ReviewPilot has a dedicated demo app in a separate repository: [aruxyz/review-pilot-demo](https://github.com/aruxyz/review-pilot-demo).

It is a minimal Next.js 14 app with five intentional UX bugs. ReviewPilot should detect several of them when run against the demo.

### The five intentional bugs

1. **Mobile navbar overflow.** The navbar uses a single flex row with `whitespace-nowrap` and no responsive collapse. On viewports 390px or narrower, the links overflow horizontally and cause page-level horizontal scroll.

2. **Login button stays disabled.** The login form has a "Sign In" button with `disabled={true}` hardcoded. Even when the email and password fields are filled, the button never becomes enabled.

3. **Pricing CTA hidden below the fold on mobile.** The homepage hero section uses `py-96` (384px) vertical padding on mobile. The pricing CTA at the bottom of the hero is pushed below the fold and requires scrolling.

4. **Broken footer link.** The footer contains a link to `/nonexistent-page`, a route that does not exist. Clicking it leads to a Next.js 404 page.

5. **Unclear form validation.** The login form shows a generic error message ("Error 001: Invalid input") with no field-level indicators. There are no red borders, no `aria-invalid` attributes, and no helper text under the inputs. The user cannot tell which field is invalid or what is wrong.

### Run the demo

You have two options.

**Option A: Deploy the demo to Vercel, then run ReviewPilot against the URL.**

Clone and deploy the demo repo:

```bash
git clone https://github.com/aruxyz/review-pilot-demo.git
cd review-pilot-demo
npm install
vercel --prod
```

Copy the production URL Vercel gives you (for example `https://review-pilot-demo.vercel.app`).

Run ReviewPilot against it:

```bash
cd ..
reviewpilot run --url https://review-pilot-demo.vercel.app
```

**Option B: Run the demo locally.**

Clone and start the demo app:

```bash
git clone https://github.com/aruxyz/review-pilot-demo.git
cd review-pilot-demo
npm install
npm run dev
```

The app starts on `http://localhost:3000`.

In another terminal, run ReviewPilot against it:

```bash
reviewpilot run --url http://localhost:3000
```

ReviewPilot will open the app in a headless browser, explore the configured journeys on desktop and mobile viewports, and write a report to `.reviewpilot-output/`.

Open the report:

```bash
reviewpilot report
```

You should see findings for several of the five bugs, complete with screenshots and reproduction steps.

### Demo app details

The demo app is a minimal Next.js 14 App Router project with TypeScript and Tailwind CSS. It has four routes:

- `/` (homepage with hero, pricing CTA, footer)
- `/login` (broken login form)
- `/pricing` (pricing section)
- `/_not-found` (Next.js default 404, triggered by the broken footer link)

See the [review-pilot-demo README](https://github.com/aruxyz/review-pilot-demo#readme) for more details on the demo app.

---

## Architecture

```
reviewpilot/
  cli/                          Typer CLI (init, run, report, doctor)
    main.py                     App entrypoint, command dispatch
    commands/
      init.py                   Create default .reviewpilot.yml
      run.py                    Run a review
      report.py                 Open the latest HTML report
      doctor.py                 Check environment setup

  core/                         Domain models and orchestration
    config.py                   ReviewPilotConfig, YAML loading
    result.py                   Finding, JourneyResult, ReviewReport
    severity.py                 Severity enum, ReviewStatus enum
    runner.py                   Orchestrates browser + judge + reports

  browser/                      Browser Use wrapper
    browser_use_runner.py       Agent setup, run, cleanup
    screenshots.py              Copy screenshots into output dir
    artifacts.py                JSON report, manifest persistence

  judge/                        LLM judge
    prompts.py                  Judge prompt builder, severity rubric
    evaluator.py                JudgeEvaluator, JSON parsing, coercion
    schemas.py                  FindingSchema, JourneyJudgement

  github/                       GitHub Action integration
    action.py                   Action entrypoint (reads INPUT_* env vars)
    comments.py                 Post, find, update PR comments
    pr_context.py               PRContext dataclass, env var parsing

  reports/                      Report generators
    markdown.py                 Markdown report for PR comments
    html.py                     HTML report for local review
    templates/
      review.html.j2            Jinja2 template for HTML report

  .github/
    actions/reviewpilot/        Docker action
      action.yml                Action metadata
      Dockerfile                python:3.12-slim + Chromium
    workflows/
      reviewpilot.yml           Example consuming workflow
```

### Tech stack

| Layer | Technology |
|---|---|
| Language | Python 3.10+ |
| Browser automation | [Browser Use](https://github.com/browser-use/browser-use) 0.12+ |
| Browser binary | Chromium via Playwright |
| CLI framework | [Typer](https://typer.tiangolo.com/) |
| Terminal output | [Rich](https://rich.readthedocs.io/) |
| Config and schemas | [Pydantic](https://pydantic.dev/) 2+ |
| HTML reports | [Jinja2](https://jinja.palletsprojects.com/) |
| GitHub API | [PyGithub](https://pygithub.readthedocs.io/) 2+ |
| YAML | [PyYAML](https://pyyaml.org/) |
| Tests | [pytest](https://docs.pytest.org/) |

### Data flow

```
.config -> ReviewPilotConfig
               |
               v
         core.runner.run_review()
               |
               +-> browser.BrowserUseRunner.run_journey()
               |         |
               |         +-> Browser Use Agent.run()
               |         |         |
               |         |         +-> AgentHistoryList
               |         |                   |
               |         +-> dict[str, Any] (raw result)
               |                            |
               +-> judge.JudgeEvaluator.judge()
               |         |
               |         +-> LLM ainvoke()
               |         |         |
               |         |         +-> JSON text
               |         |                   |
               |         +-> JourneyJudgement (parsed)
               |                            |
               +-> JourneyResult (mapped)
               |
               +-> ReviewReport (aggregated)
               |
               +-> reports.markdown.generate_markdown_report()
               +-> reports.html.generate_html_report()
               +-> browser.artifacts.save_json_report()
               |
               +-> github.comments.upsert_pr_comment() (if enabled)
```

---

## Troubleshooting

### `reviewpilot: command not found`

The `reviewpilot` console script may not be on your PATH. Find it with:

```bash
python -m reviewpilot.cli.main --help
```

If that works, your Scripts directory is not on PATH. Add it, or use `python -m reviewpilot.cli.main` instead of `reviewpilot`.

### `ModuleNotFoundError: No module named 'browser_use'`

Browser Use is not installed. Install it:

```bash
pip install browser-use
playwright install chromium
```

### `ValueError: You need to set the BROWSER_USE_API_KEY environment variable`

You set `task_model: "bu-2-0"` (or any `bu-*` model) but did not set `BROWSER_USE_API_KEY`. Either set the env var or switch to a different provider in the config.

### Browser Use agent does nothing or loops

The agent may be stuck on a page it cannot understand. Try:

- Increasing `max_steps` in the config.
- Switching to a stronger model (for example, `gpt-4o` or `claude-sonnet-4-5`).
- Setting `use_vision: true` explicitly if it is currently `"auto"`.
- Running with `--headed` to watch what the agent does.

### No screenshots in the report

Screenshots are only captured when `browser_use.use_vision` is truthy. Set it to `true` in the config:

```yaml
browser_use:
  use_vision: true
```

### The PR comment was not posted

Check the following:

1. `output.github_comment` is `true` in the config (it is `false` by default for local runs).
2. The action was run inside a GitHub Action (check `GITHUB_ACTIONS=true`).
3. The workflow has `permissions: pull-requests: write`.
4. The Pull Request is not from a fork (fork PRs cannot post comments with the default token).

### The agent is too slow or too expensive

Tune these config values:

```yaml
review:
  max_steps: 15            # fewer steps per journey

browser_use:
  task_model: "gpt-4.1-mini"  # cheaper model
  use_vision: false           # skip screenshots (cheaper, less accurate)
```

You can also reduce the number of journeys or viewports in the config.

### The agent submitted a form it should not have

Safe mode should prevent this. If it happens, check that `safety.safe_mode` is `true` and `safety.allow_form_submit` is `false`. If the agent still submitted a form, please open an issue with the journey goal and the URL.

### `reviewpilot doctor` reports a missing API key

Set at least one of these environment variables:

```bash
export OPENAI_API_KEY=sk-...
# or
export ANTHROPIC_API_KEY=sk-ant-...
# or
export GOOGLE_API_KEY=...
# or
export BROWSER_USE_API_KEY=bu-...
```

On Windows PowerShell:

```powershell
$env:OPENAI_API_KEY = "sk-..."
```

---

## FAQ

### Is ReviewPilot free?

Yes. ReviewPilot is open source under the MIT license. You pay only for the LLM API calls that Browser Use makes. A typical review with `gpt-4.1-mini` and 3 journeys on 2 viewports costs less than $0.10.

### Does ReviewPilot replace Playwright or Cypress?

No. ReviewPilot is not an E2E test framework. It is an AI QA reviewer that explores your app like a user. It complements your existing tests by catching issues that scripted tests do not cover.

### Does ReviewPilot store my data?

No. ReviewPilot does not phone home. All artifacts are written to your local `.reviewpilot-output/` directory or to GitHub Action artifacts. The LLM provider you configure receives the page content and screenshots, same as any other Browser Use run.

### Can I use ReviewPilot without a GitHub Action?

Yes. The CLI works standalone. Run `reviewpilot run --url <URL>` against any running web app. The GitHub Action is just a thin wrapper around the CLI.

### Can I use ReviewPilot for production monitoring?

You can, but it is not optimized for that. ReviewPilot is designed for Pull Request previews. For production monitoring, consider a dedicated tool.

### How is ReviewPilot different from Lighthouse?

Lighthouse audits performance, accessibility, and SEO with a fixed set of rules. ReviewPilot explores the app like a user and reports UX issues that rule-based tools cannot catch (broken flows, confusing validation, hidden CTAs). They complement each other.

### How is ReviewPilot different from visual regression tools?

Visual regression tools compare pixels between two snapshots and report differences. They cannot tell whether a difference matters. ReviewPilot understands the page semantically and reports whether a change broke a user flow.

### Can I run ReviewPilot on a specific branch?

Yes. The GitHub Action runs on whatever ref the workflow checks out. For Pull Requests, that is the merge ref by default. You can change it with `actions/checkout@v4` `ref:` input.

### Does ReviewPilot support self-hosted GitHub Enterprise?

Yes. ReviewPilot respects the `GITHUB_API_URL` environment variable, which GitHub Enterprise Server sets automatically. No extra configuration needed.

---

## Comparison With Other Tools

| Tool | What it checks | How it checks | Setup effort |
|---|---|---|---|
| **ReviewPilot** | Running app UX, flows, layout | AI agent browses the app | 5 minutes |
| Playwright / Cypress | Scripted user flows | You write test scripts | Hours to days |
| Lighthouse | Performance, accessibility, SEO | Rule-based audit | 1 minute |
| Visual regression (Percy, Chromatic) | Pixel differences | Snapshot diffing | 30 minutes |
| Manual QA | Anything a human notices | A human clicks around | Unbounded |

ReviewPilot fits between manual QA and scripted E2E tests. It catches what a human would catch, without the human, and without the upfront cost of writing scripts.

---

## Contributing

Contributions are welcome. The project follows these principles:

1. **Useful before impressive.** A small reliable tool is better than a large unstable platform.
2. **Evidence over vague feedback.** Every finding includes screenshots and reproduction steps.
3. **Human-readable by default.** Reports read like a thoughtful QA reviewer wrote them.
4. **Browser Use is meaningful.** It is the core engine, not a branding detail.
5. **Easy to clone and run.** A developer should understand and run the project within five minutes.

### Development setup

```bash
git clone https://github.com/aruxyz/reviewpilot-browser-use.git
cd reviewpilot-browser-use
pip install -e ".[dev]"
playwright install chromium
pytest
```

### Running tests

```bash
pytest tests/ -v
```

The test suite covers config validation, severity ordering, report generation, LLM factory mapping, and prompt building.

### Project structure

See the [Architecture](#architecture) section for the full file layout.

---

## License

MIT. See [LICENSE](LICENSE).
