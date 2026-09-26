"""
app.py
------
AI Resume Screening System for HR - a simple 2-page Streamlit app.

Page 1: HR Login (static username/password, no database)
Page 2: HR Candidate Dashboard (summary cards, charts, candidate table, details)

Run with:
    streamlit run app.py

This is a beginner-friendly demo. It does NOT contain a real authentication
system or a database - that is intentional, as requested for this project.
"""

import json
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

# ---------------------------------------------------------------------------
# 1. STATIC LOGIN CREDENTIALS
# ---------------------------------------------------------------------------
VALID_USERNAME = "admin"
VALID_PASSWORD = "admin123"

DATA_FILE = Path(__file__).parent / "data" / "candidates.json"

# Colours used consistently across cards, tables and charts
VERDICT_COLORS = {
    "Strong Fit": "#22C55E",
    "Potential Fit": "#FACC15",
    "Not Fit": "#EF4444",
}


# ---------------------------------------------------------------------------
# 2. DATA LOADING
#    This is the ONLY function that needs to change later to plug in real
#    n8n / Python screening results. Everything below (charts, table, etc.)
#    already works off whatever this function returns, as long as each
#    candidate dict has these keys:
#        candidate_name, email, match_score, final_verdict,
#        key_strengths, missing_skills, explanation
# ---------------------------------------------------------------------------
def load_candidates() -> list[dict]:
    """
    Load candidate screening results.

    Right now this reads from a local JSON test file (data/candidates.json).

    TO CONNECT REAL DATA LATER:
    Replace the body of this function with code that reads your Google
    Sheet, your n8n output, or a database, as long as you return a list
    of dicts with the same field names used below.
    """
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data


def candidates_to_dataframe(candidates: list[dict]) -> pd.DataFrame:
    """Convert the list of candidate dicts into a pandas DataFrame for tables/charts."""
    df = pd.DataFrame(candidates)
    df["match_score"] = pd.to_numeric(df["match_score"], errors="coerce").fillna(0)
    return df


# ---------------------------------------------------------------------------
# 3. PAGE SETUP + CUSTOM STYLING
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="AI Resume Screening System",
    page_icon="🧑‍💼",
    layout="wide",
)

# All the custom look-and-feel lives in this one CSS block. It only styles
# things - it doesn't change any app logic.
CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Poppins', sans-serif;
}
html { scroll-behavior: smooth; }

.stApp {
    background: linear-gradient(160deg, #0E1117 0%, #12172A 100%);
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(8px); }
    to   { opacity: 1; transform: translateY(0); }
}
.block-container { animation: fadeIn 0.45s ease; }

.gradient-title {
    font-size: 2.3rem;
    font-weight: 700;
    background: linear-gradient(90deg, #7C5CFF, #38BDF8);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0;
}
.gradient-subtitle {
    color: #9CA3AF;
    margin-top: 2px;
    margin-bottom: 1.1rem;
}

/* st.metric cards */
div[data-testid="stMetric"] {
    background: linear-gradient(145deg, #161B29, #1D2333);
    border: 1px solid rgba(124, 92, 255, 0.25);
    border-radius: 16px;
    padding: 16px 12px;
    box-shadow: 0 4px 14px rgba(0,0,0,0.35);
    transition: transform 0.25s ease, box-shadow 0.25s ease;
}
div[data-testid="stMetric"]:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 22px rgba(124, 92, 255, 0.25);
}
div[data-testid="stMetricValue"] { color: #F5F5F7; font-weight: 700; }
div[data-testid="stMetricLabel"] { color: #9CA3AF; }

/* Buttons */
.stButton > button {
    border-radius: 10px;
    border: 1px solid rgba(124, 92, 255, 0.4);
    background: linear-gradient(90deg, #7C5CFF, #6046E0);
    color: white;
    font-weight: 600;
    transition: all 0.25s ease;
}
.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(124, 92, 255, 0.4);
    border-color: #7C5CFF;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] { gap: 6px; }
.stTabs [data-baseweb="tab"] {
    background-color: #161B29;
    border-radius: 10px 10px 0 0;
    padding: 8px 18px;
    color: #9CA3AF;
    transition: all 0.25s ease;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(90deg, #7C5CFF, #38BDF8);
    color: white !important;
    font-weight: 600;
}

/* Leaderboard cards (Top Candidates) */
.leader-card {
    background: linear-gradient(145deg, #161B29, #1D2333);
    border-radius: 16px;
    padding: 18px 16px;
    border: 1px solid rgba(255,255,255,0.06);
    box-shadow: 0 4px 14px rgba(0,0,0,0.35);
    transition: transform 0.25s ease, box-shadow 0.25s ease;
    text-align: center;
}
.leader-card:hover {
    transform: translateY(-6px);
    box-shadow: 0 10px 26px rgba(124, 92, 255, 0.3);
}
.leader-rank { font-size: 1.6rem; }
.leader-name { font-weight: 600; margin: 6px 0 2px 0; color: #F5F5F7; }
.leader-score { color: #7C5CFF; font-size: 1.4rem; font-weight: 700; }
.leader-verdict { font-size: 0.8rem; color: #9CA3AF; margin-bottom: 8px; }

.score-bar-bg {
    background: rgba(255,255,255,0.08);
    border-radius: 8px;
    height: 8px;
    width: 100%;
    overflow: hidden;
    margin-top: 6px;
}
.score-bar-fill {
    height: 100%;
    border-radius: 8px;
    background: linear-gradient(90deg, #7C5CFF, #38BDF8);
    transition: width 0.6s ease;
}

/* Dataframe container rounding */
div[data-testid="stDataFrame"] { border-radius: 12px; overflow: hidden; }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False


# ---------------------------------------------------------------------------
# 4. PAGE 1 - LOGIN PAGE
# ---------------------------------------------------------------------------
def show_login_page():
    st.markdown('<p class="gradient-title">🔐 HR Login</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="gradient-subtitle">Sign in to view the resume screening dashboard</p>',
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        with st.container(border=True):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            login_clicked = st.button("Login", use_container_width=True)

            if login_clicked:
                if username == VALID_USERNAME and password == VALID_PASSWORD:
                    st.session_state.logged_in = True
                    st.rerun()
                else:
                    st.error("Invalid username or password.")


# ---------------------------------------------------------------------------
# 5. PAGE 2 - HR CANDIDATE DASHBOARD
# ---------------------------------------------------------------------------
def show_dashboard_page():
    top_left, top_right = st.columns([5, 1])
    with top_left:
        st.markdown('<p class="gradient-title">AI Resume Screening Dashboard</p>', unsafe_allow_html=True)
        st.markdown(
            '<p class="gradient-subtitle">Smart, automated candidate screening &amp; ranking</p>',
            unsafe_allow_html=True,
        )
    with top_right:
        if st.button("Log out"):
            st.session_state.logged_in = False
            st.rerun()

    candidates = load_candidates()

    if not candidates:
        st.warning("No candidate data found yet.")
        return

    df = candidates_to_dataframe(candidates)

    tab_overview, tab_charts, tab_candidates, tab_compare = st.tabs(
        ["📊 Overview", "📈 Charts", "🗂️ Candidates", "⚖️ Compare"]
    )

    # ===================================================================
    # TAB 1: OVERVIEW  -  summary cards + top candidates leaderboard
    # ===================================================================
    with tab_overview:
        total_candidates = len(df)
        average_score = round(df["match_score"].mean(), 1)
        eligible_count = (df["final_verdict"] != "Not Fit").sum()
        not_eligible_count = (df["final_verdict"] == "Not Fit").sum()

        card1, card2, card3, card4 = st.columns(4)
        card1.metric("Total Candidates", total_candidates)
        card2.metric("Average Match Score", f"{average_score}%")
        card3.metric("Eligible Candidates", int(eligible_count))
        card4.metric("Not Eligible Candidates", int(not_eligible_count))

        st.markdown("<br>", unsafe_allow_html=True)
        st.subheader("🏆 Top Candidates")

        top_n = st.slider(
            "Number of top candidates to show",
            min_value=1,
            max_value=min(10, total_candidates),
            value=min(3, total_candidates),
        )
        top_df = df.sort_values("match_score", ascending=False).head(top_n).reset_index(drop=True)
        medals = ["🥇", "🥈", "🥉"]

        top_cols = st.columns(len(top_df))
        for i, (col, row) in enumerate(zip(top_cols, top_df.itertuples())):
            rank_label = medals[i] if i < len(medals) else f"#{i + 1}"
            with col:
                st.markdown(
                    f"""
                    <div class="leader-card">
                        <div class="leader-rank">{rank_label}</div>
                        <div class="leader-name">{row.candidate_name}</div>
                        <div class="leader-score">{row.match_score}%</div>
                        <div class="leader-verdict">{row.final_verdict}</div>
                        <div class="score-bar-bg">
                            <div class="score-bar-fill" style="width:{row.match_score}%;"></div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    # ===================================================================
    # TAB 2: CHARTS
    # ===================================================================
    with tab_charts:
        chart_col1, chart_col2 = st.columns(2)

        with chart_col1:
            st.markdown("**Match Score by Candidate**")
            score_chart = px.bar(
                df,
                x="candidate_name",
                y="match_score",
                labels={"candidate_name": "Candidate", "match_score": "Match Score (%)"},
                color="match_score",
                color_continuous_scale=["#38BDF8", "#7C5CFF"],
                template="plotly_dark",
            )
            score_chart.update_layout(
                showlegend=False,
                coloraxis_showscale=False,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font_color="#E6E6E6",
            )
            st.plotly_chart(score_chart, use_container_width=True)

        with chart_col2:
            st.markdown("**Eligibility Distribution**")
            verdict_counts = df["final_verdict"].value_counts().reset_index()
            verdict_counts.columns = ["final_verdict", "count"]
            pie_chart = px.pie(
                verdict_counts,
                names="final_verdict",
                values="count",
                hole=0.55,
                color="final_verdict",
                color_discrete_map=VERDICT_COLORS,
                template="plotly_dark",
            )
            pie_chart.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font_color="#E6E6E6",
                legend=dict(orientation="h", y=-0.1),
            )
            st.plotly_chart(pie_chart, use_container_width=True)

    # ===================================================================
    # TAB 3: CANDIDATES  -  full table + detail view
    # ===================================================================
    with tab_candidates:
        st.subheader("Candidate List")

        table_df = df[["candidate_name", "email", "match_score", "final_verdict"]].rename(
            columns={
                "candidate_name": "Candidate",
                "email": "Email",
                "match_score": "Match Score",
                "final_verdict": "Verdict",
            }
        )
        st.dataframe(
            table_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Match Score": st.column_config.ProgressColumn(
                    "Match Score",
                    help="AI-generated match score",
                    format="%d%%",
                    min_value=0,
                    max_value=100,
                ),
            },
        )

        st.markdown("<br>", unsafe_allow_html=True)
        st.subheader("Candidate Details")

        selected_name = st.selectbox(
            "Select a candidate to view details",
            options=df["candidate_name"].tolist(),
        )
        candidate = df[df["candidate_name"] == selected_name].iloc[0]

        with st.container(border=True):
            detail_col1, detail_col2 = st.columns(2)

            with detail_col1:
                st.markdown(f"**Candidate Name:** {candidate['candidate_name']}")
                st.markdown(f"**Email:** {candidate['email']}")
                st.markdown(f"**Match Score:** {candidate['match_score']}%")

                verdict = candidate["final_verdict"]
                if verdict == "Strong Fit":
                    st.success(f"Final Verdict: {verdict}")
                elif verdict == "Potential Fit":
                    st.warning(f"Final Verdict: {verdict}")
                else:
                    st.error(f"Final Verdict: {verdict}")

            with detail_col2:
                st.markdown("**Key Strengths**")
                strengths = candidate["key_strengths"]
                if strengths:
                    for skill in strengths:
                        st.markdown(f"- {skill}")
                else:
                    st.markdown("_None listed_")

                st.markdown("**Missing Skills**")
                gaps = candidate["missing_skills"]
                if gaps:
                    for skill in gaps:
                        st.markdown(f"- {skill}")
                else:
                    st.markdown("_None - no major gaps found_")

            st.markdown("**Explanation**")
            st.write(candidate["explanation"])

    # ===================================================================
    # TAB 4: COMPARE
    # ===================================================================
    with tab_compare:
        st.subheader("⚖️ Compare Candidates")

        compare_names = st.multiselect(
            "Select 2 or more candidates to compare",
            options=df["candidate_name"].tolist(),
            default=df.sort_values("match_score", ascending=False)["candidate_name"].tolist()[:2],
        )

        if len(compare_names) < 2:
            st.info("Select at least 2 candidates above to see a comparison.")
        else:
            compare_df = df[df["candidate_name"].isin(compare_names)]

            compare_chart = px.bar(
                compare_df,
                x="candidate_name",
                y="match_score",
                color="candidate_name",
                labels={"candidate_name": "Candidate", "match_score": "Match Score (%)"},
                color_discrete_sequence=["#7C5CFF", "#38BDF8", "#22C55E", "#FACC15", "#EF4444", "#F472B6"],
                template="plotly_dark",
            )
            compare_chart.update_layout(
                showlegend=False,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font_color="#E6E6E6",
            )
            st.plotly_chart(compare_chart, use_container_width=True)

            compare_cols = st.columns(len(compare_names))
            for col, name in zip(compare_cols, compare_names):
                person = df[df["candidate_name"] == name].iloc[0]
                with col:
                    with st.container(border=True):
                        st.markdown(f"**{person['candidate_name']}**")
                        st.metric("Match Score", f"{person['match_score']}%")
                        st.caption(person["final_verdict"])

                        st.markdown("_Strengths_")
                        strengths = person["key_strengths"]
                        st.write(", ".join(strengths) if strengths else "None listed")

                        st.markdown("_Missing Skills_")
                        gaps = person["missing_skills"]
                        st.write(", ".join(gaps) if gaps else "None")


# ---------------------------------------------------------------------------
# 6. MAIN APP LOGIC
# ---------------------------------------------------------------------------
if st.session_state.logged_in:
    show_dashboard_page()
else:
    show_login_page()