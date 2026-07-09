import os
import time
from github import Auth, Github

token = os.environ["GH_TOKEN"]
gh = Github(auth=Auth.Token(token))
repo = gh.get_repo("aruxyz/review-pilot-demo")

print("=== Create PR #2 ===")
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
