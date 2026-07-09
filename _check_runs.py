import os
import httpx

h = {
    "Authorization": f"Bearer {os.environ['GH_TOKEN']}",
    "Accept": "application/vnd.github+json",
}
r = httpx.get(
    "https://api.github.com/repos/aruxyz/review-pilot-demo/actions/runs?per_page=5",
    headers=h,
)
runs = r.json().get("workflow_runs", [])
print(f"Total runs: {len(runs)}")
for run in runs[:5]:
    print(
        f"  - {run['name']} | status: {run['status']} | conclusion: {run['conclusion']} | event: {run['event']} | created: {run['created_at']}"
    )
    print(f"    URL: {run['html_url']}")
