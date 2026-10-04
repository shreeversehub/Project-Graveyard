# 🪦 Project Graveyard

> *We tell developers why their projects die, before the next one does.*

Every developer has a graveyard of abandoned repos, and nobody knows why they died. **Project Graveyard** takes any GitHub username, digs through the commit history, and shows which projects are dead, why they died, and which living repo is most likely to be abandoned next.

Built for **LovHack Season 3: The Next Build** 🚀

🔗 **Live demo:** _add your Streamlit link here_
🎥 **Demo video:** _add your video link here_

---

## ✨ Features

- 🟢🟡🟠🪦 **Repo status:** every repo is classified as Alive, Sleeping, Dying, or Dead based on days since the last commit
- 📈 **Commit timeline:** one chart showing when each repo was active and when it went quiet
- ⚠️ **Abandonment risk score (0-100):** ranks which living repos are most likely to be abandoned next
- 🔍 **Cause of death:** rule-based autopsy (burst-and-burn, stillborn, no README, no tests, long coma)
- 🔬 **AI autopsy (optional):** a short, friendly explanation plus one concrete step to revive the repo. Works without an API key through a built-in fallback
- 📊 **Graveyard rate:** the share of your repos that are dead

---

## 🔄 How It Works

1. **Fetch:** pull the user's public, non-fork repos from the GitHub REST API (latest 15)
2. **Collect:** for each repo, read the last 100 commit dates and the file tree
3. **Extract features:** days idle, commit count, first-week burst ratio, longest gap, and presence of README, tests, CI, and description
4. **Score:** classify status and compute the abandonment risk from weighted signals
5. **Diagnose:** match the features against cause-of-death rules
6. **Display:** timeline, risk bars, tombstones, and a summary table in Streamlit

---

## 🧮 Risk Score

The abandonment risk is a **transparent, weighted heuristic** (0-100):

| Signal | Max weight |
|---|---|
| Days since last commit | 45 |
| Burst ratio (work crammed into week one) | 20 |
| No README | 10 |
| No tests | 10 |
| No CI | 5 |
| No description | 5 |
| 3 or fewer commits | 5 |

---

## 🗂️ Project Structure

```
Project-Graveyard/
├── app.py             # Streamlit UI (timeline, risk bars, tombstones)
├── github_client.py   # GitHub API calls (repos, commits, file tree)
├── scoring.py         # Feature extraction, status, risk score, causes of death
├── ai.py              # Optional AI autopsy with rule-based fallback
├── requirements.txt   # Dependencies
└── README.md
```

---

## 🛠️ Tech Stack

Python · Streamlit · Pandas · Altair · GitHub REST API · Anthropic API (optional)

---

## 🚀 Run Locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

**Optional environment variables**

| Variable | Why |
|---|---|
| `GITHUB_TOKEN` | Raises the GitHub limit from 60 to 5000 requests/hour (no scopes needed) |
| `ANTHROPIC_API_KEY` | Enables the AI-written autopsy |

Windows (cmd):
```
set GITHUB_TOKEN=your_token
python -m streamlit run app.py
```
Mac/Linux:
```
export GITHUB_TOKEN=your_token
streamlit run app.py
```

> 🔒 Never commit your tokens. Set them as environment variables or Streamlit secrets.

---

## ⚠️ Limitations

- Analyzes public repos only, the latest 15 non-fork repos, and the last 100 commits per repo
- The risk score is a hand-tuned heuristic, not a trained model
- Without a GitHub token, the API rate limit allows only about 2 analyses per hour

---

## 🔮 What's Next

- 🤖 Train a model (logistic regression) on labeled public repos to replace the heuristic
- 🪪 Shareable "My Graveyard" card
- 🔔 Revival reminders for high-risk repos

---

## 🎓 Learning Outcomes

- Working with the GitHub REST API: pagination, rate limits, and authentication
- Feature engineering from time-series commit data
- Designing an explainable scoring system
- Building and deploying a data app with Streamlit
- Handling graceful fallbacks when an external AI service is unavailable

---

## 👩‍💻 Author

**Lalitha shree**: B.Tech AI & Data Science
GitHub: [@shreeversehub](https://github.com/shreeversehub)
