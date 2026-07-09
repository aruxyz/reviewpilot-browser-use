from __future__ import annotations

from reviewpilot.github.pr_context import PRContext

COMMENT_MARKER = "<!-- reviewpilot:v1 -->"


def _make_client(ctx: PRContext):
    from github import Auth, Github

    import os

    base_url = os.environ.get("GITHUB_API_URL", "https://api.github.com")
    return Github(auth=Auth.Token(ctx.token), base_url=base_url)


def post_pr_comment(ctx: PRContext, body: str) -> str:
    gh = _make_client(ctx)
    repo = gh.get_repo(ctx.repository)
    pr = repo.get_pull(ctx.pr_number)
    comment = pr.create_issue_comment(body)
    return comment.html_url


def find_existing_comment_id(ctx: PRContext, marker: str = COMMENT_MARKER) -> int | None:
    gh = _make_client(ctx)
    repo = gh.get_repo(ctx.repository)
    pr = repo.get_pull(ctx.pr_number)
    for comment in pr.get_issue_comments():
        if marker in comment.body:
            return comment.id
    return None


def update_pr_comment(ctx: PRContext, comment_id: int, body: str) -> None:
    gh = _make_client(ctx)
    repo = gh.get_repo(ctx.repository)
    comment = repo.get_issue_comment(comment_id)
    comment.edit(body)


def upsert_pr_comment(ctx: PRContext, body: str) -> str:
    existing_id = find_existing_comment_id(ctx)
    if existing_id is not None:
        update_pr_comment(ctx, existing_id, body)
        gh = _make_client(ctx)
        repo = gh.get_repo(ctx.repository)
        comment = repo.get_issue_comment(existing_id)
        return comment.html_url
    return post_pr_comment(ctx, body)
