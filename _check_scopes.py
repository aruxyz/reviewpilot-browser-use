import httpx
import os

r = httpx.get(
    "https://api.github.com/repos/aruxyz/review-pilot-demo",
    headers={
        "Authorization": f"Bearer {os.environ['GH_TOKEN']}",
        "Accept": "application/vnd.github+json",
    },
)
print("X-OAuth-Scopes:", r.headers.get("X-OAuth-Scopes", "NONE"))
print("X-Accepted-OAuth-Scopes:", r.headers.get("X-Accepted-OAuth-Scopes", "NONE"))
print("permissions:", r.json().get("permissions"))
print("status:", r.status_code)
