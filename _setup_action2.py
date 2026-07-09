import os
import time
import base64
import httpx
from github import Auth, Github

token = os.environ["GH_TOKEN"]
bu_key = os.environ["BU_KEY"]
gh = Github(auth=Auth.Token(token))
repo = gh.get_repo("aruxyz/review-pilot-demo")
headers = {
    "Authorization": f"Bearer {token}",
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
}
api = "https://api.github.com/repos/aruxyz/review-pilot-demo"

print("=== 1. Set BROWSER_USE_API_KEY secret ===")
try:
    repo.create_secret("BROWSER_USE_API_KEY", bu_key)
    print("  Secret set")
except Exception as e:
    print(f"  Secret already set or failed: {e}")

print()
print("=== 2. Get main SHA ===")
main_sha = repo.get_branch("main").commit.sha
print(f"  main SHA: {main_sha}")

print()
print("=== 3. Create blobs for both files ===")

workflow_yaml = r'''name: ReviewPilot

on:
  pull_request:
    types: [opened, synchronize, reopened]

permissions:
  contents: write
  pull-requests: write

jobs:
  review:
    runs-on: ubuntu-latest
    if: github.event.pull_request.head.repo.full_name == github.repository
    timeout-minutes: 25
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install ReviewPilot
        run: |
          pip install "git+https://github.com/aruxyz/reviewpilot-browser-use.git"
          playwright install chromium --with-deps

      - name: Run ReviewPilot
        env:
          BROWSER_USE_API_KEY: ${{ secrets.BROWSER_USE_API_KEY }}
        run: |
          reviewpilot run --max-steps 10

      - name: Upload screenshots to release for inline view
        env:
          GH_TOKEN: ${{ github.token }}
        run: |
          TAG="reviewpilot-evidence-pr-${{ github.event.pull_request.number }}"
          gh release create "$TAG" \
            --title "ReviewPilot evidence PR #${{ github.event.pull_request.number }}" \
            --notes "Auto-generated screenshots from ReviewPilot review." \
            --target main 2>/dev/null || true
          gh release upload "$TAG" reviewpilot-output/screenshots/*.png --clobber

      - name: Post review comment with inline screenshots
        uses: actions/github-script@v7
        with:
          script: |
            const fs = require('fs');
            let body = fs.readFileSync('reviewpilot-output/review.md', 'utf8');
            const owner = context.repo.owner;
            const repo = context.repo.repo;
            const prNumber = context.issue.number;
            const tag = `reviewpilot-evidence-pr-${prNumber}`;
            const baseDownload = `https://github.com/${owner}/${repo}/releases/download/${tag}`;

            body = body.replace(/`([^`]*screenshots[^`]*)`/g, (match, path) => {
              const normalized = path.replace(/\\/g, '/');
              const filename = normalized.split('/').pop();
              return `${match}\n\n![evidence](${baseDownload}/${filename})`;
            });

            const workflowUrl = `${process.env.GITHUB_SERVER_URL}/${owner}/${repo}/actions/runs/${process.env.GITHUB_RUN_ID}`;
            body += `\n\n---\n📷 **Screenshots**: viewable inline above, or [download all artifacts](${workflowUrl})\n`;
            body += `🤖 Posted automatically by GitHub Actions (github-actions[bot])\n`;

            const comments = await github.rest.issues.listComments({
              owner, repo, issue_number: prNumber,
            });
            const existing = comments.data.find(c =>
              c.body.includes('<!-- reviewpilot:v1 -->') &&
              c.user.login === 'github-actions[bot]'
            );

            if (existing) {
              await github.rest.issues.updateComment({
                owner, repo, comment_id: existing.id, body,
              });
              core.info(`Updated comment ${existing.id}`);
            } else {
              const created = await github.rest.issues.createComment({
                owner, repo, issue_number: prNumber, body,
              });
              core.info(`Posted comment ${created.data.id}`);
            }

      - name: Upload full report artifact
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: reviewpilot-report-pr-${{ github.event.pull_request.number }}
          path: reviewpilot-output/
          retention-days: 14
'''

config_yaml = '''app:
  name: "ReviewPilot Demo"
  url: "https://review-pilot-demo.vercel.app"

review:
  mode: "pull_request"
  max_steps: 10
  timeout_seconds: 120

browser_use:
  enabled: true
  task_model: "bu-latest"
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
    goal: "Open the homepage and check whether the primary navigation, hero section, and main CTA are visible and usable. Check for layout overflow on mobile."
  - name: "Login flow"
    goal: "Open the login page, inspect the form, test basic validation behavior, and verify whether the Sign In button becomes enabled when valid input is entered."
  - name: "Navigation flow"
    goal: "Explore the main navigation and footer links. Check whether important links are reachable and not broken."

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
  output_dir: "reviewpilot-output"

safety:
  safe_mode: true
  allow_form_submit: false
  allow_destructive_actions: false
  redact_secrets: true
'''

with httpx.Client(timeout=30) as client:
    print("  Creating blob for workflow...")
    r = client.post(f"{api}/git/blobs", headers=headers, json={
        "content": workflow_yaml,
        "encoding": "utf-8",
    })
    r.raise_for_status()
    workflow_blob_sha = r.json()["sha"]
    print(f"    workflow blob: {workflow_blob_sha}")

    print("  Creating blob for config...")
    r = client.post(f"{api}/git/blobs", headers=headers, json={
        "content": config_yaml,
        "encoding": "utf-8",
    })
    r.raise_for_status()
    config_blob_sha = r.json()["sha"]
    print(f"    config blob: {config_blob_sha}")

    print()
    print("=== 4. Create tree ===")
    r = client.post(f"{api}/git/trees", headers=headers, json={
        "base_tree": main_sha,
        "tree": [
            {"path": ".github/workflows/reviewpilot.yml", "mode": "100644", "type": "blob", "sha": workflow_blob_sha},
            {"path": ".reviewpilot.yml", "mode": "100644", "type": "blob", "sha": config_blob_sha},
        ],
    })
    r.raise_for_status()
    new_tree_sha = r.json()["sha"]
    print(f"  Tree SHA: {new_tree_sha}")

    print()
    print("=== 5. Create commit ===")
    r = client.post(f"{api}/git/commits", headers=headers, json={
        "message": "Add ReviewPilot workflow and config",
        "tree": new_tree_sha,
        "parents": [main_sha],
    })
    r.raise_for_status()
    new_commit_sha = r.json()["sha"]
    print(f"  Commit SHA: {new_commit_sha}")

    print()
    print("=== 6. Update main ref ===")
    r = client.patch(f"{api}/git/refs/heads/main", headers=headers, json={"sha": new_commit_sha})
    r.raise_for_status()
    print("  main updated")

print()
print("=== 7. Create PR #2 ===")
time.sleep(2)
main_sha = repo.get_branch("main").commit.sha
branch_name = f"feat/pr2-{int(time.time())}"
repo.create_git_ref(ref=f"refs/heads/{branch_name}", sha=main_sha)
print(f"  Branch: {branch_name}")

readme = repo.get_contents("README.md", ref="main")
original = readme.decoded_content.decode("utf-8")
addition = "\n\n## Contributing\n\nContributions welcome. Please open an issue first to discuss what you would like to change.\n"
new_content = original + addition
repo.update_file("README.md", "Add contributing section", new_content, readme.sha, branch=branch_name)
print("  README updated on branch")

pr = repo.create_pull(
    title="Add contributing section to README",
    body="Adding a contributing section to the README.\n\nReviewPilot will automatically review the deployed preview and post a QA comment.",
    base="main",
    head=branch_name,
)
print(f"  PR #{pr.number}: {pr.html_url}")
print(f"  Head SHA: {pr.head.sha}")
print()
print("=== DONE. Workflow should trigger now. ===")
