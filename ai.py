import os
import requests

MODEL = "claude-sonnet-5-5"


def _fallback(name, features, causes):
    f = features
    text = f"**{name}** went quiet after {f['commits']} commits and has been idle for {f['days_idle']} days. "
    text += "Main suspects: " + "; ".join(c.split(":")[0].lower() for c in causes) + ". "
    text += "Revive it: add a README and one small test, then ship one tiny commit this week."
    return text


def ai_autopsy(name, features, causes):
    key = os.getenv("ANTHROPIC_API_KEY", "")
    if not key.startswith("sk-ant-"):
        return _fallback(name, features, causes)
    prompt = (
        f"You are a witty but kind coroner for abandoned GitHub repos. Repo: {name}.\n"
        f"Stats: {features}\nRule-based findings: {causes}\n"
        "Write: (1) a 2-sentence autopsy of why it died, (2) one concrete step to revive it "
        "this week. Max 80 words, no fluff."
    )
    try:
        r = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={"x-api-key": key, "anthropic-version": "2023-06-01", "content-type": "application/json"},
            json={"model": MODEL, "max_tokens": 300, "messages": [{"role": "user", "content": prompt}]},
            timeout=30,
        )
        r.raise_for_status()
        return r.json()["content"][0]["text"]
    except Exception:
        return _fallback(name, features, causes)
