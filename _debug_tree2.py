import httpx
import os

headers = {
    "Authorization": f"Bearer {os.environ['GH_TOKEN']}",
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
}
api = "https://api.github.com/repos/aruxyz/review-pilot-demo"

with httpx.Client(timeout=30) as c:
    main_sha = "ae822b3c86ebed8664caf97f70b1afbf542c41d3"
    commit = c.get(f"{api}/git/commits/{main_sha}", headers=headers).json()
    tree_sha = commit["tree"]["sha"]
    print("tree_sha:", tree_sha)

    blob = c.post(f"{api}/git/blobs", headers=headers, json={
        "content": "hello",
        "encoding": "utf-8",
    }).json()
    print("blob:", blob["sha"])

    print("trying tree creation with base_tree=tree_sha...")
    r = c.post(f"{api}/git/trees", headers=headers, json={
        "base_tree": tree_sha,
        "tree": [
            {"path": ".github/workflows/test.yml", "mode": "100644", "type": "blob", "sha": blob["sha"]},
        ],
    })
    print("status:", r.status_code)
    print("body:", r.text[:500])
