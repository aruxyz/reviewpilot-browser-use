import os
import httpx

h = {
    "Authorization": f"Bearer {os.environ['GH_TOKEN']}",
    "Accept": "application/vnd.github+json",
}
r = httpx.post(
    "https://api.github.com/repos/aruxyz/review-pilot-demo/actions/runs/29003277113/cancel",
    headers=h,
)
print("cancel status:", r.status_code)
