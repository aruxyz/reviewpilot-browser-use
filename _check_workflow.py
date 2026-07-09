import os
import httpx
import base64

h = {
    "Authorization": f"Bearer {os.environ['GH_TOKEN']}",
    "Accept": "application/vnd.github+json",
}
r = httpx.get(
    "https://api.github.com/repos/aruxyz/review-pilot-demo/contents/.github/workflows/reviewpilot.yml?ref=feat/pr2-1783581256",
    headers=h,
)
content = base64.b64decode(r.json()["content"]).decode()
for i, line in enumerate(content.split("\n")[:35], 1):
    print(f"{i:3}: {line}")
