import os
import httpx

h = {
    "Authorization": f"Bearer {os.environ['GH_TOKEN']}",
    "Accept": "application/vnd.github+json",
}
r = httpx.get(
    "https://api.github.com/repos/aruxyz/review-pilot-demo/actions/runs/29003442184",
    headers=h,
)
run = r.json()
print(f"Status: {run['status']} | Conclusion: {run['conclusion']}")

r2 = httpx.get(run["jobs_url"], headers=h)
for job in r2.json().get("jobs", []):
    print(f"  Job: {job['name']} | status: {job['status']} | conclusion: {job['conclusion']}")
    for step in job.get("steps", []):
        print(f"    {step['name']}: {step['status']}/{step['conclusion']}")
