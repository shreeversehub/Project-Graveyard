import altair as alt
import pandas as pd
import streamlit as st

from ai import ai_autopsy
from github_client import fetch_commit_dates, fetch_files, fetch_repos
from scoring import STATUS_EMOJI, analyze

st.set_page_config(page_title="Project Graveyard", page_icon="🪦", layout="wide")
st.title("🪦 Project Graveyard")
st.caption("Enter a GitHub username. See which repos died, why, and which one dies next.")


@st.cache_data(ttl=3600, show_spinner=False)
def load(username):
    out = []
    for r in fetch_repos(username):
        owner = r["owner"]["login"]
        dates = fetch_commit_dates(owner, r["name"])
        paths = fetch_files(owner, r["name"], r["default_branch"])
        out.append(analyze(r, dates, paths))
    return out


user = st.text_input("GitHub username", placeholder="e.g. your-username")
if st.button("Dig 🪦") and user.strip():
    try:
        with st.spinner("Digging through commits..."):
            st.session_state["res"] = load(user.strip())
    except Exception as e:
        st.error(str(e))
        st.stop()

res = st.session_state.get("res")
if res:
    df = pd.DataFrame([{"repo": r["name"], "status": r["status"], "risk": r["risk"],
                        "language": r["language"], "commits": r["features"]["commits"],
                        "days_idle": r["features"]["days_idle"]} for r in res])
    dead = (df.status == "Dead").sum()

    c1, c2, c3 = st.columns(3)
    c1.metric("Repos analyzed", len(df))
    c2.metric("In the graveyard", int(dead))
    c3.metric("Graveyard rate", f"{dead / len(df):.0%}")

    st.subheader("⚰️ Commit timeline")
    tl = pd.DataFrame([{"repo": r["name"], "date": d, "status": r["status"]}
                       for r in res for d in r["dates"]])
    if not tl.empty:
        st.altair_chart(
            alt.Chart(tl).mark_circle(size=40, opacity=0.7).encode(
                x="date:T", y=alt.Y("repo:N", sort="-x"),
                color=alt.Color("status:N", scale=alt.Scale(
                    domain=list(STATUS_EMOJI), range=["#2ecc71", "#f1c40f", "#e67e22", "#7f8c8d"])),
                tooltip=["repo", "date", "status"]).properties(height=60 + 28 * len(res)),
            use_container_width=True)

    st.subheader("⚠️ Next to die")
    alive = sorted([r for r in res if r["status"] in ("Alive", "Sleeping")], key=lambda r: -r["risk"])[:3]
    if alive:
        for r in alive:
            st.progress(r["risk"] / 100, text=f"{r['name']}: {r['risk']}% abandonment risk")
    else:
        st.info("No living repos found. Everything's already buried.")

    st.subheader("🪦 Tombstones")
    for r in sorted(res, key=lambda r: -r["features"]["days_idle"]):
        if r["status"] in ("Dying", "Dead"):
            with st.expander(f"{STATUS_EMOJI[r['status']]} {r['name']}: idle {r['features']['days_idle']} days"):
                for c in r["causes"]:
                    st.write("• " + c)
                st.link_button("Open repo", r["url"])
                if st.button("🔬 AI autopsy", key=f"ai_{r['name']}"):
                    try:
                        st.info(ai_autopsy(r["name"], r["features"], r["causes"]))
                    except Exception as e:
                        st.warning(str(e))

    st.dataframe(df, use_container_width=True, hide_index=True)
