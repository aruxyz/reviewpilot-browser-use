import os
import httpx

h = {
    "Authorization": f"Bearer {os.environ['GH_TOKEN']}",
    "Accept": "application/vnd.github+json",
}
r = httpx.get(
    "https://api.github.com/repos/aruxyz/review-pilot-demo/actions/runs/29000923518/logs",
    headers=h,
    follow_redirects=False,
)
print("logs status:", r.status_code)
location = r.headers.get("location", "none")
print("location:", location[:150])

if r.status_code == 302:
    logs_url = location
    print("Downloading logs...")
    r2 = httpx.get(logs_url, follow_redirects=True)
    with open("logs.zip", "wb") as f:
        f.write(r2.content)
    print(f"Saved logs.zip ({len(r2.content)} bytes)")
