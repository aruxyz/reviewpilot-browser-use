import os
from github import Auth, Github

gh = Github(auth=Auth.Token(os.environ["GH_TOKEN"]))
repo = gh.get_repo("aruxyz/review-pilot-demo")
main_ref = repo.get_git_ref("heads/main")
main_sha = main_ref.object.sha
print("main_sha:", main_sha)
commit = repo.get_git_commit(main_sha)
print("commit tree:", commit.tree, type(commit.tree).__name__)
tree = repo.get_git_tree(commit.tree.sha)
print("tree sha:", tree.sha, "type:", type(tree).__name__)
print("tree object repr:", repr(tree)[:200])
