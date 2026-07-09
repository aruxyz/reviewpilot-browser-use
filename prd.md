Berikut **PRD + human-readable spec** yang bisa langsung kamu pakai sebagai `PRD.md`, `SPEC.md`, atau prompt untuk coding agent. Aku buat dalam bahasa Inggris karena targetnya untuk GitHub/open source dan orang giveaway Browser Use. Konsepnya tetap jelas: **Browser Use adalah base utama**, bukan sekadar tempelan.

---

# ReviewPilot PRD

## Product Name

**ReviewPilot**

## One-liner

**ReviewPilot is an open-source GitHub Action that uses Browser Use to review deployed web apps directly from Pull Requests and leave human-readable QA feedback with screenshots, reasoning, and suggested fixes.**

## Tagline

**AI browser QA for every Pull Request, powered by Browser Use.**

---

# 1. Product Vision

Modern teams already have code review, linting, unit tests, and sometimes E2E tests.

But many bugs still escape because reviewers rarely test the actual running application carefully. A human reviewer may approve a PR without noticing that:

* the mobile layout is broken,
* a CTA is hidden below the fold,
* a form button no longer works,
* a page still loads but the flow feels confusing,
* a visual element disappeared,
* the implementation technically works but does not behave like a user expects.

ReviewPilot exists to close that gap.

It acts like a lightweight AI QA reviewer that opens the deployed preview of a Pull Request, navigates it using **Browser Use**, observes the interface, captures evidence, reasons about user-facing problems, and posts a useful review back to GitHub.

This is not meant to replace Playwright, Cypress, or human QA. It is meant to catch the obvious and painful issues that humans often miss because they do not manually browse every PR.

---

# 2. Why Browser Use Is the Base

ReviewPilot must use **Browser Use as the core browser automation layer**.

Browser Use is responsible for:

* opening and controlling the browser,
* navigating pages,
* interacting with UI elements,
* observing page state,
* executing browser tasks through an LLM-driven agent,
* capturing task results from real browser behavior.

ReviewPilot should not be positioned as a generic Playwright wrapper.

Playwright may be used indirectly only when needed for artifacts such as screenshots, traces, browser context configuration, or infrastructure-level browser setup. The product value must come from the combination of:

```text
Pull Request context
        +
Deploy preview URL
        +
Browser Use autonomous browsing
        +
LLM judging
        +
GitHub PR feedback
```

The key point:

**Browser Use is the browser intelligence engine. ReviewPilot is the PR review product built around it.**

---

# 3. Problem Statement

When frontend or full-stack teams review Pull Requests, they usually focus on code diffs.

This misses a large class of issues because user-facing quality can only be judged by opening the actual application.

Current tools have limitations:

* Code review tools inspect code, not real UX.
* Unit tests do not validate user journeys.
* Traditional E2E tests require developers to write and maintain brittle scripts.
* Visual regression tools often detect pixel differences without explaining whether the difference matters.
* Manual QA is slow and often skipped on small teams.

The result is that broken interfaces are discovered late, often after merge or production deploy.

ReviewPilot solves this by reviewing the running app itself.

---

# 4. Target Users

## Primary Users

**Frontend developers**

They want fast feedback before merging UI changes.

**Full-stack developers**

They want to know whether their backend or frontend changes broke visible user flows.

**Indie hackers and startup teams**

They do not have dedicated QA teams, but still need basic release confidence.

**Open-source maintainers**

They want automated review comments for PRs without manually testing every contribution.

## Secondary Users

**QA engineers**

They can use ReviewPilot as a first-pass reviewer before deeper manual QA.

**Product engineers**

They can validate whether a feature still feels usable from a user perspective.

---

# 5. Core User Story

As a developer, when I open a Pull Request, I want an AI browser reviewer to open my preview deployment, explore the app like a real user, find obvious UX or functional issues, collect screenshots, and comment on the PR, so I can fix user-facing bugs before merge.

---

# 6. Main Workflow

```text
Developer opens a Pull Request
        ↓
GitHub Action starts
        ↓
ReviewPilot reads config
        ↓
ReviewPilot receives preview URL
        ↓
Browser Use opens the deployed app
        ↓
Browser Use explores configured journeys
        ↓
ReviewPilot captures screenshots and page observations
        ↓
LLM judge reviews behavior and evidence
        ↓
ReviewPilot generates Markdown report
        ↓
GitHub bot posts PR review comment
```

---

# 7. MVP Scope

The MVP should be small, polished, and production-ready.

## Must-have

ReviewPilot v1 must include:

1. **CLI**

   * Run locally from terminal.
   * Accept URL and config file.
   * Output Markdown and HTML reports.

2. **GitHub Action**

   * Run automatically on Pull Requests.
   * Post a PR comment with findings.
   * Upload screenshots and report artifacts.

3. **Browser Use integration**

   * Use Browser Use as the main browsing and interaction engine.
   * Allow the user to define goals or journeys in config.
   * Execute browser tasks against a live URL.

4. **AI judge**

   * Convert Browser Use observations into useful QA findings.
   * Classify findings by severity.
   * Explain what failed and why it matters.

5. **Evidence**

   * Screenshot for every major issue.
   * Page URL.
   * Reproduction steps.
   * Expected vs actual behavior.

6. **Config file**

   * Define app URL.
   * Define journeys.
   * Define viewports.
   * Define review checks.
   * Define output behavior.

7. **Readable reports**

   * Markdown report for PR comments.
   * HTML report for local review.

---

# 8. Non-goals for v1

ReviewPilot v1 should not include:

* SaaS dashboard.
* Billing.
* User accounts.
* Database.
* Complex UI.
* Test history analytics.
* Self-healing selectors.
* Full Playwright replacement.
* Enterprise permission system.
* Browser farm infrastructure.

This project should feel like a high-quality developer tool, not an unfinished SaaS.

---

# 9. Product Principles

## 1. Useful before impressive

The first version should solve a real workflow problem. A small reliable tool is better than a large unstable platform.

## 2. Evidence over vague feedback

Every failure must include proof. A PR comment saying “UX is bad” is not useful. A PR comment saying “The primary CTA is hidden below the fold on mobile, screenshot attached” is useful.

## 3. Human-readable by default

The report should read like a thoughtful QA reviewer wrote it.

## 4. Browser Use must be meaningful

Browser Use should not be used as a branding detail. It should be the core reason the tool can navigate and inspect apps autonomously.

## 5. Easy to clone and run

A developer should understand and run the project within five minutes.

---

# 10. Functional Requirements

## 10.1 CLI

The CLI should expose these commands:

```bash
reviewpilot init
```

Creates a default config file:

```text
.reviewpilot.yml
```

```bash
reviewpilot run --url http://localhost:3000
```

Runs a local review.

```bash
reviewpilot run --config .reviewpilot.yml
```

Runs based on config.

```bash
reviewpilot report
```

Opens or generates the latest report.

```bash
reviewpilot doctor
```

Checks environment setup, Browser Use availability, API keys, browser dependencies, and GitHub configuration.

---

## 10.2 Config File

Example:

```yaml
app:
  name: "Example App"
  url: "https://preview.example.com"

review:
  mode: "pull_request"
  max_steps: 30
  timeout_seconds: 180

browser_use:
  enabled: true
  task_model: "gpt-4.1-mini"
  planner_model: "gpt-4.1-mini"
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
  github_comment: true
```

---

## 10.3 Browser Use Task Execution

For each journey, ReviewPilot should create a Browser Use task.

Example internal task:

```text
You are reviewing a web application as a senior QA engineer.

Use the browser to complete this journey:

Goal:
Open the homepage and check whether the primary navigation, hero section, and main CTA are visible and usable.

Rules:
- Do not modify real user data.
- Do not submit destructive forms.
- Do not make purchases.
- Capture observations about broken UI, confusing UX, missing elements, layout issues, and console errors.
- Provide clear evidence for every issue.
```

Browser Use should execute the task and return:

* visited URLs,
* actions taken,
* observations,
* errors,
* screenshots,
* final result.

---

## 10.4 AI Judge

The AI judge should evaluate the browser result.

It should produce structured findings:

```json
{
  "summary": "The homepage is mostly usable, but the mobile layout has a critical CTA visibility issue.",
  "status": "failed",
  "findings": [
    {
      "severity": "high",
      "title": "Primary CTA is hidden below the fold on mobile",
      "page": "/",
      "viewport": "mobile",
      "expected": "The primary CTA should be visible without excessive scrolling.",
      "actual": "The CTA appears below a large empty hero area and is not visible on initial mobile load.",
      "why_it_matters": "Users may not understand the main action they are supposed to take.",
      "reproduction_steps": [
        "Open homepage on 390x844 viewport",
        "Observe hero section",
        "Check whether the primary CTA is visible"
      ],
      "evidence": ["screenshots/home-mobile-cta-hidden.png"],
      "suggested_fix": "Reduce hero vertical spacing on mobile or move the CTA above the fold."
    }
  ]
}
```

---

## 10.5 GitHub PR Comment

The PR comment should be concise and useful.

Example:

```markdown
## ReviewPilot Browser QA Report

Review target: https://preview.example.com  
Status: Failed  
Journeys reviewed: 3  
Issues found: 2 high, 1 medium

### High Priority

#### 1. Primary CTA is hidden below the fold on mobile

Page: `/`  
Viewport: Mobile 390x844

Expected:
The main CTA should be visible when users land on the homepage.

Actual:
The CTA is pushed below the fold by excessive hero spacing.

Why it matters:
Users may not understand the primary action on the page.

Evidence:
`screenshots/home-mobile-cta-hidden.png`

Suggested fix:
Reduce mobile hero spacing or move the CTA higher.

---

### Passed Checks

- Desktop homepage layout is usable.
- Main navigation links are reachable.
- Login form validation appears understandable.

Generated by ReviewPilot, powered by Browser Use.
```

---

# 11. Severity System

ReviewPilot should use four severity levels.

## Critical

The user cannot complete an important flow.

Examples:

* Login is impossible.
* Checkout cannot proceed.
* Main page crashes.
* Navigation is completely broken.

## High

The user can continue, but the issue seriously damages usability.

Examples:

* Primary CTA hidden.
* Form validation unclear.
* Mobile layout blocks important actions.
* Key button does nothing.

## Medium

The issue is noticeable but not blocking.

Examples:

* Minor layout overflow.
* Inconsistent spacing.
* Missing empty state.
* Weak visual hierarchy.

## Low

Small polish issues.

Examples:

* Minor copy issue.
* Slight alignment problem.
* Non-critical console warning.

---

# 12. Architecture

```text
reviewpilot/
  cli/
    main.py
    commands/
      init.py
      run.py
      report.py
      doctor.py

  core/
    config.py
    runner.py
    journey.py
    result.py
    severity.py

  browser/
    browser_use_runner.py
    screenshots.py
    artifacts.py

  judge/
    prompts.py
    evaluator.py
    schemas.py

  github/
    action.py
    comments.py
    pr_context.py

  reports/
    markdown.py
    html.py
    templates/

  examples/
    nextjs/
    react/
    static-site/

  .github/
    actions/
      reviewpilot/
        action.yml
```

---

# 13. Suggested Tech Stack

Use Python because Browser Use is Python-first.

Recommended stack:

* Python
* Browser Use
* Typer for CLI
* Rich for terminal output
* Pydantic for config and schemas
* Jinja2 for HTML reports
* PyGithub or GitHub REST API for PR comments
* Docker for reproducible runtime
* pytest for unit tests

---

# 14. Security Requirements

Because browser agents can interact with real websites, ReviewPilot must be safe by default.

## Rules

ReviewPilot must not:

* submit payment forms,
* delete user data,
* send real emails,
* publish content,
* change account settings,
* perform destructive admin actions,
* expose secrets in reports.

## Safe mode

Default mode should be safe.

```yaml
safety:
  safe_mode: true
  allow_form_submit: false
  allow_destructive_actions: false
  redact_secrets: true
```

## Secret redaction

Reports must redact:

* API keys,
* access tokens,
* passwords,
* cookies,
* authorization headers,
* private environment variables.

---

# 15. Acceptance Criteria

ReviewPilot v1 is complete when:

1. A developer can clone the repo and run:

```bash
pip install -e .
reviewpilot init
reviewpilot run --url http://localhost:3000
```

2. The tool uses Browser Use to open and inspect a real website.

3. The tool generates a Markdown report.

4. The tool generates an HTML report.

5. The tool captures screenshots for issues.

6. The GitHub Action can run on a Pull Request.

7. The GitHub Action can post a PR comment.

8. The README includes a five-minute quickstart.

9. The example project works out of the box.

10. The project clearly explains that it is powered by Browser Use.

---

# 16. README Positioning

The README should open with this:

```markdown
# ReviewPilot

AI browser QA for every Pull Request, powered by Browser Use.

ReviewPilot opens your deployed preview, explores your app like a user, detects obvious UX and functional issues, captures evidence, and leaves a human-readable review comment on your Pull Request.

It is not another E2E framework.

It is an AI QA reviewer for the running application.
```

---

# 17. Demo Scenario

Use a simple demo app with intentional bugs.

Example bugs:

* Mobile navbar overflows.
* Login button stays disabled.
* Pricing CTA is hidden below the fold.
* Broken footer link.
* Form validation message is unclear.

Then show ReviewPilot detecting them.

Demo flow:

```text
Open PR
        ↓
GitHub Action runs
        ↓
ReviewPilot opens preview URL
        ↓
Browser Use explores app
        ↓
ReviewPilot posts comment with screenshots
```

This demo is important because people need to understand the value in less than one minute.

---

# 18. MVP Build Plan

## Day 1

Build CLI skeleton, config parser, and project structure.

## Day 2

Integrate Browser Use runner and execute one journey against a URL.

## Day 3

Add AI judge and structured findings.

## Day 4

Add Markdown report and screenshot artifacts.

## Day 5

Add GitHub Action and PR comment posting.

## Day 6

Add HTML report, example app, and documentation.

## Day 7

Polish README, record GIF demo, test clean install.

---

# 19. What Makes This Worth Starring

ReviewPilot is not valuable because it uses AI.

It is valuable because it gives developers something they already want:

**a second pair of eyes on every Pull Request.**

A real developer would star this if:

* it is easy to install,
* it works on their existing preview deployments,
* the reports are not noisy,
* it catches real issues,
* it saves manual QA time,
* it shows clear evidence.

---

# 20. Final Product Definition

ReviewPilot is a production-ready open-source GitHub Action and CLI that uses Browser Use as its core browser automation engine to inspect deployed Pull Request previews, identify user-facing issues, collect evidence, and generate human-readable QA review comments.

The first version should be narrow, reliable, and polished.

The goal is not to build a massive testing platform.

The goal is to build the cleanest possible example of how Browser Use can become part of a real developer workflow.
