import os
from github import Auth, Github

token = os.environ["GH_TOKEN"]
gh = Github(auth=Auth.Token(token))
repo = gh.get_repo("aruxyz/review-pilot-demo")
pr = repo.get_pull(2)
print(f"PR #{pr.number}: {pr.title}")
print(f"Head branch: {pr.head.ref}")
print(f"Head SHA: {pr.head.sha}")
print(f"State: {pr.state}")
