import os
import requests
from datetime import datetime

API = "https://api.github.com"


def _headers():
    h = {"Accept": "application/vnd.github+json"}
    token = os.getenv("GITHUB_TOKEN")
    if token:
        h["Authorization"] = f"Bearer {token}"
    return h


def _get(path, params=None):
    r = requests.get(f"{API}{path}", headers=_headers(), params=params, timeout=20)
    if r.status_code == 403 and "rate limit" in r.text.lower():
        raise RuntimeError("GitHub rate limit hit. Set GITHUB_TOKEN env var and retry.")
    if r.status_code in (404, 409):  # not found / empty repo
        return None
    r.raise_for_status()
    return r.json()


def parse_dt(s):
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


def fetch_repos(username, limit=15):
    repos = _get(f"/users/{username}/repos", {"per_page": 100, "type": "owner", "sort": "created"})
    if repos is None:
        raise ValueError(f"GitHub user '{username}' not found")
    repos = [r for r in repos if not r["fork"]]
    return repos[:limit]


def fetch_commit_dates(owner, repo):
    commits = _get(f"/repos/{owner}/{repo}/commits", {"per_page": 100}) or []
    dates = [parse_dt(c["commit"]["author"]["date"]) for c in commits]
    return sorted(dates)


def fetch_files(owner, repo, branch):
    tree = _get(f"/repos/{owner}/{repo}/git/trees/{branch}", {"recursive": "1"})
    if not tree:
        return []
    return [t["path"].lower() for t in tree.get("tree", [])]
