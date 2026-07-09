import httpx
import os

headers = {
    "Authorization": f"Bearer {os.environ['GH_TOKEN']}",
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
}
api = "https://api.github.com/repos/aruxyz/review-pilot-demo"

with httpx.Client(timeout=30) as c:
    print("=== Try create_file for .github/workflows/reviewpilot.yml ===")
    r = c.put(f"{api}/contents/.github/workflows/reviewpilot.yml", headers=headers, json={
        "message": "Add ReviewPilot workflow",
        "content": "aGVsbG8=",  # "hello" base64
        "branch": "main",
    })
    print("status:", r.status_code)
    print("body:", r.text[:500])
