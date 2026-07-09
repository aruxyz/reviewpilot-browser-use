import os
import httpx

h = {
    "Authorization": f"Bearer {os.environ['GH_TOKEN']}",
    "Accept": "application/vnd.github+json",
}
r = httpx.get(
    "https://api.github.com/repos/aruxyz/review-pilot-demo/actions/runs/29004211086/logs",
    headers=h,
    follow_redirects=True,
)
with open("logs.zip", "wb") as f:
    f.write(r.content)
print("saved", len(r.content))
