from datetime import datetime, timezone
from github_client import parse_dt

STATUS_EMOJI = {"Alive": "🟢", "Sleeping": "🟡", "Dying": "🟠", "Dead": "🪦"}


def status_from_idle(days):
    if days < 30:
        return "Alive"
    if days < 90:
        return "Sleeping"
    if days < 180:
        return "Dying"
    return "Dead"


def analyze(repo, dates, paths):
    now = datetime.now(timezone.utc)
    n = len(dates)
    last = dates[-1] if dates else parse_dt(repo["pushed_at"])
    first = dates[0] if dates else parse_dt(repo["created_at"])

    days_idle = (now - last).days
    span = max((last - first).days, 1)
    burst = sum(1 for d in dates if (d - first).days <= 7) / n if n else 0
    max_gap = max(((b - a).days for a, b in zip(dates, dates[1:])), default=0)

    f = {
        "commits": n,
        "days_idle": days_idle,
        "span_days": span,
        "burst_ratio": round(burst, 2),
        "max_gap_days": max_gap,
        "has_readme": any(p.startswith("readme") for p in paths),
        "has_tests": any("test" in p for p in paths),
        "has_ci": any(p.startswith(".github/workflows") for p in paths),
        "has_desc": bool(repo.get("description")),
    }

    # Abandonment risk 0-100 (heuristic; swap for a trained model if time allows)
    risk = min(days_idle / 180, 1) * 45
    risk += burst * 20 if n >= 3 else 0
    risk += 0 if f["has_readme"] else 10
    risk += 0 if f["has_tests"] else 10
    risk += 0 if f["has_ci"] else 5
    risk += 0 if f["has_desc"] else 5
    risk += 5 if n <= 3 else 0

    return {
        "name": repo["name"],
        "url": repo["html_url"],
        "language": repo.get("language") or "-",
        "status": status_from_idle(days_idle),
        "risk": round(min(risk, 100)),
        "features": f,
        "causes": causes_of_death(f),
        "dates": dates,
    }


def causes_of_death(f):
    c = []
    if f["commits"] >= 3 and f["burst_ratio"] >= 0.7:
        c.append("Burst and burn: most work happened in the first week, then momentum vanished")
    if f["commits"] <= 3:
        c.append("Stillborn: only a handful of commits, never got past the first session")
    if not f["has_readme"] or not f["has_desc"]:
        c.append("Never introduced: no README or description, so nobody (including future you) knew what it was")
    if not f["has_tests"]:
        c.append("Untested: no tests, so every change felt risky")
    if f["max_gap_days"] > 60:
        c.append(f"Long coma: a {f['max_gap_days']}-day gap with no commits")
    return c or ["Natural causes: no clear red flags, it just lost priority"]
