"""
Founder Intelligence Platform — UI layer.

This file owns presentation only. Every call into scripts/ (ranking_engine,
recommendation_engine, ai_advisor_engine, live_analyzer, scoring_engine) is
untouched — same functions, same arguments, same fallback behavior on
exceptions. Nothing here changes what the backend computes, only how it's
displayed.
"""

import json
import re
from pathlib import Path

import pandas as pd
import streamlit as st

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO

from scripts.ranking_engine import rank_opportunities
from scripts.recommendation_engine import generate_recommendation
from scripts.ai_advisor_engine import generate_ai_advice
from scripts.live_analyzer import analyze_complaint
from utils.decision_engine import generate_founder_decision
st.set_page_config(
    page_title="Founder Intelligence Platform",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =====================================================================
# DESIGN SYSTEM
# =====================================================================

def load_css(path: str = "assets/styles.css") -> None:
    """Inject the design-system stylesheet. Run streamlit from the project
    root so this relative path resolves the same way data/processed does."""
    css_file = Path(path)
    if css_file.exists():
        st.markdown(f"<style>{css_file.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)
    else:
        st.warning(f"Stylesheet not found at '{path}'. Run `streamlit run` from the project root.")

load_css()


def render_html(html: str) -> None:
    """Render a raw HTML string via st.markdown, safely.

    Streamlit's markdown parser follows standard Markdown rules: a blank
    line followed by 4+ spaces of indentation is read as a *code block*,
    not HTML — so indented multi-line HTML (which is what every f-string
    template below produces) can randomly drop out of "raw HTML" mode and
    print literal tags like `</div>` as visible text. Collapsing the
    string to a single line (no newlines, no inter-tag whitespace) makes
    that ambiguity impossible. Spacing between elements is handled by CSS
    `gap` in the stylesheet, not by literal whitespace, so this is safe.
    """
    st.markdown(re.sub(r">\s+<", "><", html.strip()), unsafe_allow_html=True)


NAV_ITEMS = [
    "Dashboard",
    "Opportunities",
    "Saved Opportunities",
    "AI Advisor",
    "Analyze Complaints"
]

NAV_ICONS = {
    "Dashboard": "🏠",
    "Opportunities": "📋",
    "Saved Opportunities": "⭐",
    "AI Advisor": "🤖",
    "Analyze Complaints": "📝",
}

PAIN_COLORS = {
    "Time": "#22d3ee",
    "Money": "#34d399",
    "Productivity": "#6d5dfb",
    "Trust": "#fbbf67",
    "Compliance": "#fb7185",
    "Emotional": "#f472b6",
    "Unknown": "#9a9cab",
}

ADVICE_ICONS = {
    "startup idea": "💡",
    "target customer": "🎯",
    "difficulty": "⚙️",
    "why now": "📈",
    "go-to-market": "🚀",
    "go to market": "🚀",
}

# =====================================================================
# SESSION STATE
# =====================================================================

if "ai_calls" not in st.session_state:
    st.session_state.ai_calls = 0
if "selected_problem" not in st.session_state:
    st.session_state.selected_problem = None
if "complaint_results" not in st.session_state:
    st.session_state.complaint_results = []

# =====================================================================
# DATA LOADING  (unchanged logic)
# =====================================================================

with open(
    "data/processed/opportunities.json",
    "r",
    encoding="utf-8",
) as f:
    opportunities = json.load(f)

ranked_opportunities = rank_opportunities(
    opportunities
)
pain_counts = {}

for opp in ranked_opportunities:


    pain = opp.get(
    "pain_type",
    "Unknown"
)

    if pain not in pain_counts:
        pain_counts[pain] = 0

    pain_counts[pain] += 1

top_opportunity = (
    ranked_opportunities[0]
    if ranked_opportunities
    else None
)

category_counts = {}



for opp in ranked_opportunities:
    category = opp["category"]
    if category not in category_counts:
        category_counts[category] = 0
    category_counts[category] += 1

if ranked_opportunities:

    top_trend = max(
        category_counts,
        key=category_counts.get
    )

    recommendation = generate_recommendation(
        top_opportunity,
        top_trend
    )

else:

    top_trend = None
    recommendation = None

# =====================================================================
# SHARED RENDER HELPERS
# =====================================================================

def score_tier(score: float):
    """Returns (label, css_class, hex_color) for a given opportunity score."""
    if score >= 70:
        return "High", "tier-high", "#34d399"
    if score >= 50:
        return "Medium", "tier-medium", "#fbbf67"
    return "Low", "tier-low", "#fb7185"


def tag_html(label: str, color: str = None) -> str:
    style = f' style="color:{color}"' if color else ""
    dot = f'<span class="tag-dot"{style}></span>' if color else ""
    return f'<span class="tag"{style}>{dot}{label}</span>'


def score_ring_html(score: float, size: int = 128, label: str = "OPPORTUNITY SCORE") -> str:
    _, _, color = score_tier(score)
    pct = max(0, min(100, score))
    return f"""
    <div class="score-ring-wrap">
      <div class="score-ring" style="--pct:{pct};--ring-color:{color};--ring-size:{size}px;">
        <div class="score-ring-inner">
          <div class="score-ring-value">{score:.0f}</div>
          <div class="score-ring-max">/ 100</div>
        </div>
      </div>
      <div class="score-ring-label">{label}</div>
    </div>
    """


def score_bar_html(score: float) -> str:
    _, _, color = score_tier(score)
    pct = max(0, min(100, score))
    return f"""
    <div class="score-bar-wrap">
      <div class="score-bar-track"><div class="score-bar-fill" style="width:{pct}%;--ring-color:{color};"></div></div>
      <div class="score-bar-value">{score:.0f}</div>
    </div>
    """


def render_hero(top_opp: dict, rec: dict, trend: str) -> None:
    tier_label, tier_class, _ = score_tier(top_opp["opportunity_score"])
    pain_color = PAIN_COLORS.get(top_opp["pain_type"], PAIN_COLORS["Unknown"])
    render_html(f"""
        <div class="hero">
          <div class="hero-grid">
            <div class="hero-body">
              <span class="eyebrow">⭑ Featured Opportunity of the Week</span>
              <div class="hero-problem">{top_opp['problem']}</div>
              <div class="hero-meta">
                {tag_html(top_opp['category'])}
                {tag_html(top_opp['pain_type'], pain_color)}
                <span class="tier-pill {tier_class}">{tier_label} PRIORITY</span>
              </div>
              <div class="hero-insight">
                <b>AI Insight —</b> this opportunity leads a broader trend in
                <b>{trend}</b>. The recommended move: build
                <b>{rec['startup_idea']}</b> for {rec['target_customer'].lower()}.
              </div>
            </div>
            {score_ring_html(top_opp['opportunity_score'])}
          </div>
        </div>
        """)


def render_kpis(ranked: list, top_opp: dict, categories: dict, ai_calls: int) -> None:
    cards = [
        ("📈", "Opportunities", len(ranked)),
        ("🏆", "Top Score", f"{top_opp['opportunity_score']:.0f}"),
        ("🗂️", "Categories", len(categories)),
        ("✨", "AI Recommendations", ai_calls),
    ]
    cards_html = "".join(
        f"""
        <div class="kpi-card">
          <div class="kpi-top"><div class="kpi-icon">{icon}</div></div>
          <div class="kpi-label">{label}</div>
          <div class="kpi-value">{value}</div>
        </div>
        """
        for icon, label, value in cards
    )
    render_html(f'<div class="kpi-grid">{cards_html}</div>')


def render_featured_opportunity_card(opp: dict) -> None:
    pain_color = PAIN_COLORS.get(
        opp["pain_type"],
        PAIN_COLORS["Unknown"]
    )

    tier_label, tier_class, _ = score_tier(
        opp["opportunity_score"]
    )

    startup_idea = opp.get(
        "startup_idea",
        "Not available"
    )

    target_customer = opp.get(
        "target_customer",
        "Not available"
    )

    pricing_model = opp.get(
        "pricing_model",
        "Not available"
    )

    mvp_description = opp.get(
        "mvp_description",
        "Not available"
    )

    render_html(f"""
        <div class="glass-card">

          <div style="display:flex; justify-content:space-between; align-items:flex-start; gap:16px;">

            <div style="flex:1;">

              <div class="opp-tags" style="margin-bottom:10px;">
                {tag_html(opp['category'])}
                {tag_html(opp['pain_type'], pain_color)}
              </div>

              <div style="
                  font-size:1.02rem;
                  font-weight:600;
                  color:var(--text-primary);
                  line-height:1.45;
                  margin-bottom:18px;
              ">
                {opp['problem']}
              </div>

              <div style="margin-bottom:12px;">
                <strong>💡 Startup Idea</strong><br>
                {startup_idea}
              </div>

              <div style="margin-bottom:12px;">
                <strong>🎯 Target Customer</strong><br>
                {target_customer}
              </div>

              <div style="margin-bottom:12px;">
                <strong>💰 Pricing Model</strong><br>
                {pricing_model}
              </div>

              <div>
                <strong>🚀 MVP</strong><br>
                {mvp_description}
              </div>

            </div>

            <span class="tier-pill {tier_class}">
                {opp['opportunity_score']:.0f}
            </span>

          </div>

        </div>
    """)


def generate_founder_verdict(opp):

    score = opp["opportunity_score"]

    if score >= 40:
        verdict = "✅ Build This"
        confidence = "High"
    elif score >= 30:
        verdict = "⚠️ Worth Validating"
        confidence = "Medium"
    else:
        verdict = "❌ Low Priority"
        confidence = "Low"

    return f"""
### {verdict}

**Confidence:** {confidence}

**Startup Idea**
{opp.get("startup_idea", "N/A")}

**Target Customer**
{opp.get("target_customer", "N/A")}

**Recommended Pricing**
{opp.get("pricing_model", "N/A")}

**Why This Matters**
This opportunity demonstrates recurring customer pain and monetization potential.

**Next Step**
Interview 10 potential customers before building the MVP.
"""

def render_recommendation_card(rec: dict) -> None:
    diff = rec["difficulty"]
    diff_class = {"Low": "tier-high", "Medium": "tier-medium", "High": "tier-low"}.get(diff, "tier-medium")
    render_html(f"""
        <div class="glass-card">
          <div style="font-size:1.1rem; font-weight:700; color:var(--text-primary); margin-bottom:14px;">
            {rec['startup_idea']}
          </div>
          <div class="metric-strip" style="margin-top:0;">
            <div class="metric-chip">
              <div class="metric-chip-label">Target Customer</div>
              <div class="metric-chip-value" style="font-family:var(--font-sans); font-weight:500;">{rec['target_customer']}</div>
            </div>
            <div class="metric-chip">
              <div class="metric-chip-label">Difficulty</div>
              <span class="tier-pill {diff_class}">{diff}</span>
            </div>
          </div>
          <hr style="margin:14px 0 12px 0;">
          <div style="font-size:0.86rem; color:var(--text-secondary); line-height:1.55;">
            <b style="color:var(--text-primary);">Why this opportunity —</b> {rec['reason']}
          </div>
        </div>
        """)


def render_opportunity_row(opp: dict, rank: int, is_selected: bool) -> None:
    pain_color = PAIN_COLORS.get(opp["pain_type"], PAIN_COLORS["Unknown"])
    selected_class = "is-selected" if is_selected else ""
    render_html(f"""
        <div class="opp-row {selected_class}">
          <div class="opp-rank">#{rank:02d}</div>
          <div class="opp-main">
            <div class="opp-problem">{opp['problem']}</div>
            <div class="opp-tags">
              {tag_html(opp['category'])}
              {tag_html(opp['pain_type'], pain_color)}
            </div>
          </div>
          {score_bar_html(opp['opportunity_score'])}
        </div>
        """)


def render_detail_card(opp: dict) -> None:
    pain_color = PAIN_COLORS.get(opp["pain_type"], PAIN_COLORS["Unknown"])
    col_text, col_ring = st.columns([3, 1])
    with col_text:
        render_html(f"""
            <div class="glass-card" style="height:100%;">
              <div class="opp-tags" style="margin-bottom:12px;">
                {tag_html(opp['category'])}
                {tag_html(opp['pain_type'], pain_color)}
              </div>
              <div style="font-size:1.05rem; font-weight:600; color:var(--text-primary); line-height:1.5; margin-bottom:16px;">
                {opp['problem']}
              </div>
              <div class="metric-strip">
                <div class="metric-chip"><div class="metric-chip-label">Severity</div><div class="metric-chip-value">{opp.get('severity', '–')}</div></div>
                <div class="metric-chip"><div class="metric-chip-label">Frequency</div><div class="metric-chip-value">{opp.get('frequency_estimate', '–')}</div></div>
                <div class="metric-chip"><div class="metric-chip-label">Willingness to Pay</div><div class="metric-chip-value">{opp.get('willingness_to_pay', '–')}</div></div>
                <div class="metric-chip"><div class="metric-chip-label">Competition</div><div class="metric-chip-value">{opp.get('competition_level', '–')}</div></div>
                <div class="metric-chip"><div class="metric-chip-label">Evidence</div><div class="metric-chip-value">{opp.get('evidence_strength', '–')}</div></div>
              </div>
            </div>
            """)
    with col_ring:
        render_html(f'<div class="glass-card" style="display:flex; align-items:center; justify-content:center; height:100%;">{score_ring_html(opp["opportunity_score"], size=104, label="SCORE")}</div>')


def parse_advice_sections(text: str):
    """Best-effort split of the Gemini markdown response into ### sections.
    Falls back to None if the text doesn't follow that shape, so the caller
    can render it as a single card instead."""
    if not text or "###" not in text:
        return None
    try:
        parts = re.split(r"\n?###\s*", text.strip())
        parts = [p for p in parts if p.strip()]
        sections = []
        for part in parts:
            lines = part.strip().split("\n", 1)
            heading = lines[0].strip().strip("#").strip()
            body = lines[1].strip() if len(lines) > 1 else ""
            if heading:
                sections.append((heading, body))
        return sections or None
    except Exception:
        return None


def render_ai_advice(text: str) -> None:
    sections = parse_advice_sections(text)
    if not sections:
        render_html(f'<div class="glass-card">{text}</div>')
        return
    for heading, body in sections:
        icon = ADVICE_ICONS.get(heading.lower(), "▸")
        render_html(f'<div class="advice-section"><div class="advice-heading">{icon} {heading}</div></div>')
        render_html(body if body else "—")


def render_complaint_result_card(result: dict, idx: int) -> None:
    score = result.get("opportunity_score", 0)
    pain = result.get("pain_type", "Unknown")
    pain_color = PAIN_COLORS.get(pain, PAIN_COLORS["Unknown"])
    st.markdown(
    f"""
    <div class="timeline-item">
      <div class="glass-card" style="padding:18px 20px;">
        <div style="display:flex; justify-content:space-between; align-items:flex-start; gap:14px;">
          <div style="flex:1;">
            <div class="opp-tags" style="margin-bottom:8px;">
              {tag_html(result.get('category', 'Unknown'))}
              {tag_html(pain, pain_color)}
            </div>
            <div style="font-size:0.94rem; font-weight:600; color:var(--text-primary); line-height:1.45;">
              {result.get('problem', '')}
            </div>
          </div>
          <span class="tier-pill {score_tier(score)[1]}">{score:.0f}</span>
        </div>
        <div class="metric-strip">
          <div class="metric-chip"><div class="metric-chip-label">Severity</div><div class="metric-chip-value">{result.get('severity', '–')}</div></div>
          <div class="metric-chip"><div class="metric-chip-label">Frequency</div><div class="metric-chip-value">{result.get('frequency_estimate', '–')}</div></div>
          <div class="metric-chip"><div class="metric-chip-label">Willingness</div><div class="metric-chip-value">{result.get('willingness_to_pay', '–')}</div></div>
          <div class="metric-chip"><div class="metric-chip-label">Competition</div><div class="metric-chip-value">{result.get('competition_level', '–')}</div></div>
          <div class="metric-chip"><div class="metric-chip-label">Evidence</div><div class="metric-chip-value">{result.get('evidence_strength', '–')}</div></div>
        </div>
      </div>
    </div>
    """,
    unsafe_allow_html=True
)

# =====================================================================
# SIDEBAR
# =====================================================================

with st.sidebar:
    render_html("""
        <div class="brand">
          <div class="brand-mark">🚀</div>
          <div>
            <div class="brand-name">Founder Intelligence</div>
            <div class="brand-tag">AI Opportunity Engine</div>
          </div>
        </div>
        """)

    render_html('<div class="nav-label">Navigate</div>')

    page = st.radio(
        "Navigation",
        options=NAV_ITEMS,
        format_func=lambda p: f"{NAV_ICONS.get(p, '')}  {p}",
        label_visibility="collapsed",
    )

    render_html('<div class="sidebar-divider"></div>')

    render_html(f"""
        <div class="sidebar-stats">
          <div class="stat-row"><span>Version</span><span>0.1</span></div>
          <div class="stat-row"><span>Data Source</span><span>Founder Dataset</span></div>
          <div class="stat-row"><span>Opportunities</span><span>{len(ranked_opportunities)}</span></div>
          <div class="stat-row"><span>Categories</span><span>{len(category_counts)}</span></div>
        </div>
        """)

# =====================================================================
# DASHBOARD PAGE
# =====================================================================

if page == "Dashboard":

    if not ranked_opportunities:

        st.warning(
        "No opportunities available yet."
    )

        st.info(
        "Go to Analyze Complaints and save your first opportunity."
    )

    else:

        render_hero(
        top_opportunity,
        recommendation,
        top_trend
    )

        render_kpis(
        ranked_opportunities,
        top_opportunity,
        category_counts,
        st.session_state.ai_calls
    )

        left, right = st.columns(
        [1.15, 0.85],
        gap="large"
    )

        with left:

            render_html(
            '<p class="section-title">📊 Intelligence Overview</p>'
        )

            tab_cat, tab_pain = st.tabs(
            ["By Category", "By Pain Type"]
        )

        with tab_cat:

            category_df = pd.DataFrame(
                {
                    "Category": list(
                        category_counts.keys()
                    ),
                    "Mentions": list(
                        category_counts.values()
                    )
                }
            )

            st.bar_chart(
                category_df.set_index(
                    "Category"
                ),
                color="#6D5DFB"
            )

        with tab_pain:

            pain_df = pd.DataFrame(
                {
                    "Pain Type": list(
                        pain_counts.keys()
                    ),
                    "Count": list(
                        pain_counts.values()
                    )
                }
            )

            st.bar_chart(
                pain_df.set_index(
                    "Pain Type"
                ),
                color="#22D3EE"
            )

        render_html(
            '<p class="section-title">🏆 Featured Opportunity</p>'
        )

        render_featured_opportunity_card(
            top_opportunity
        )

        render_html(
            '<p class="section-title">🤖 AI Founder Verdict</p>'
        )

        st.markdown(
            generate_founder_verdict(
                top_opportunity
            )
        )

        with right:

            render_html(
            '<p class="section-title">🤖 Founder Recommendation</p>'
        )

            render_recommendation_card(
            recommendation
        )


    

# =====================================================================
# OPPORTUNITIES PAGE  (Intelligence Terminal)
# =====================================================================

if page == "Opportunities":

    render_html('<p class="page-title">📋 Opportunity Explorer</p>')
    render_html('<p class="page-subtitle">Filter, rank, and drill into founder pain points scored by the engine.</p>')

    rankings_df = pd.DataFrame(ranked_opportunities)

    render_html('<div class="filter-bar">')
    f1, f2, f3 = st.columns(3)
    with f1:
        selected_category = st.selectbox("Category", ["All"] + sorted(rankings_df["category"].unique()))
    with f2:
        selected_pain = st.selectbox("Pain Type", ["All"] + sorted(rankings_df["pain_type"].unique()))
    with f3:
        minimum_score = st.slider("Minimum Score", 0, 100, 50)
    render_html("</div>")

    filtered_df = rankings_df.copy()

    if selected_category != "All":
        filtered_df = filtered_df[filtered_df["category"] == selected_category]

    if selected_pain != "All":
        filtered_df = filtered_df[filtered_df["pain_type"] == selected_pain]

    filtered_df = filtered_df[filtered_df["opportunity_score"] >= minimum_score]

    render_html(f'<p class="result-count">{len(filtered_df)} opportunit{"y" if len(filtered_df) == 1 else "ies"} match your filters</p>')

    if len(filtered_df) > 0:

        filtered_problems = filtered_df["problem"].tolist()
        filtered_opportunities = [opp for opp in ranked_opportunities if opp["problem"] in filtered_problems]

        # keep selection valid as filters change, defaulting to the top match
        if st.session_state.selected_problem not in filtered_problems:
            st.session_state.selected_problem = filtered_problems[0]

        render_html('<p class="section-title">🔍 Ranked Results</p>')

        for idx, opp in enumerate(filtered_opportunities, start=1):
            is_selected = st.session_state.selected_problem == opp["problem"]
            row_col, btn_col = st.columns([9, 1.1])
            with row_col:
                render_opportunity_row(opp, idx, is_selected)
            with btn_col:
                if st.button("✓ Selected" if is_selected else "Select", key=f"select_{idx}"):
                    st.session_state.selected_problem = opp["problem"]
                    st.rerun()

        st.divider()

        selected_opportunity = next(
            opp for opp in ranked_opportunities if opp["problem"] == st.session_state.selected_problem
        )

        render_html('<p class="section-title">🧠 Opportunity Detail</p>')
        render_detail_card(selected_opportunity)

        if st.button("💾 Save Opportunity"):

            try:

                with open(
                "data/live/saved_opportunities.json",
                "r",
                encoding="utf-8"
            ) as f:

                    saved = json.load(f)

            except:

                saved = []

            already_saved = any(
            item["problem"] == selected_opportunity["problem"]
            for item in saved
    )

            if not already_saved:

                saved.append(
            selected_opportunity
        )

            with open(
                "data/live/saved_opportunities.json",
                "w",
                encoding="utf-8"
        )   as f:

                json.dump(
                saved,
                f,
                indent=4
            )

        st.success(
                "Opportunity saved."
        )

    else:

        st.info(
            "Already saved."
        )

        render_html("<div style='height:14px;'></div>")

    if st.button("✨ Generate Startup Analysis", type="primary"):
            with st.spinner("Analyzing opportunity..."):
                try:
                    analysis = generate_ai_advice(selected_opportunity)
                    st.session_state.ai_calls += 1
                except Exception:
                    analysis = """
### Startup Idea
AI Customer Discovery Platform

### Target Customer
Startup Founders and Product Teams

### Difficulty
Medium

### Why Now
Customer research remains one of the most time-consuming founder activities.

### Go-To-Market
Partner with startup communities and accelerators.
"""
            render_html('<p class="section-title">📄 Startup Analysis</p>')
            render_ai_advice(analysis)

    else:
        render_html("""
            <div class="empty-state">
              <div class="empty-state-icon">🔍</div>
              No opportunities match the selected filters. Try widening the score range or category.
            </div>
            """)

# =====================================================================
# AI ADVISOR PAGE
# =====================================================================

if page == "AI Advisor":

    render_html('<p class="page-title">🤖 AI Founder Advisor</p>')
    render_html('<p class="page-subtitle">An always-on AI consultant analyzing your highest-ranked opportunity.</p>')

    if not top_opportunity:

        st.warning("No opportunities available yet.")
        st.info("Go to Analyze Complaints and save your first opportunity.")

    else:

        render_html('<p class="section-title">📌 Executive Summary</p>')
        render_detail_card(top_opportunity)

        render_html('<p class="section-title">🚀 AI Startup Recommendation</p>')

        try:
            ai_advice = generate_ai_advice(top_opportunity)
            st.session_state.ai_calls += 1

        except Exception as e:
            print("Dashboard Error:", e)

            ai_advice = """
### Startup Idea
AI Customer Discovery Platform

### Target Customer
Startup Founders and Product Teams

### Difficulty
Medium

### Why Now
Customer research and interview analysis remain time-consuming for founders.

### Go-To-Market
Partner with startup communities and accelerators.
"""

        render_html('<div class="glass-card">')
        render_ai_advice(ai_advice)
        render_html("</div>")
# =====================================================================
# ANALYZE COMPLAINTS PAGE  (AI Workspace)
# =====================================================================

if page == "Analyze Complaints":

    render_html('<p class="page-title">📝 Analyze Founder Complaints</p>')
    render_html('<p class="page-subtitle">Paste raw founder complaints — one per line — and let AI structure them into scored opportunities.</p>')

    complaints_text = st.text_area(
        "Founder Complaints",
        height=220,
        placeholder="Customer interviews take forever\nFinding early adopters is difficult\nCompetitor pricing changes constantly",
        label_visibility="collapsed",
    )

    run_analysis = st.button(
        "⚡ Analyze Complaints",
        type="primary"
    )

    if run_analysis:

        if complaints_text.strip():

            complaints = [
                line.strip()
                for line in complaints_text.split("\n")
                if line.strip()
            ]

            results = []

            progress = st.progress(
                0,
                text="Analyzing complaints..."
            )

            for i, complaint in enumerate(complaints):

                result = analyze_complaint(
                    complaint
                )

                st.session_state.ai_calls += 1

                results.append(result)

                progress.progress(
                    (i + 1) / len(complaints),
                    text=f"Analyzed {i + 1}/{len(complaints)}"
                )

            progress.empty()

            st.session_state.complaint_results = results

            st.success(
                "Opportunity analysis completed successfully."
            )

        else:

            st.warning(
                "Please enter at least one complaint."
            )

    if st.session_state.complaint_results:

        render_html(
            '<p class="section-title">🧠 Analysis Timeline</p>'
        )

        for i, result in enumerate(
            st.session_state.complaint_results,
            start=1
        ):
            render_complaint_result_card(
                result,
                i
            )

        st.divider()

        if st.button(
            "💾 Save Opportunities to Database"
        ):

            with open(
                "data/processed/opportunities.json",
                "r",
                encoding="utf-8"
            ) as f:
                existing = json.load(f)

            existing.extend(
                st.session_state.complaint_results
            )

            with open(
                "data/processed/opportunities.json",
                "w",
                encoding="utf-8"
            ) as f:
                json.dump(
                    existing,
                    f,
                    indent=4
                )

            st.success(
                "Opportunities saved successfully."
            )

# =====================================================================
# SAVED OPPORTUNITIES PAGE
# =====================================================================
if page == "Saved Opportunities":


    render_html('<p class="page-title">⭐ Saved Opportunities</p>')

try:
    with open(
        "data/live/saved_opportunities.json",
        "r",
        encoding="utf-8"
    ) as f:
        saved_opportunities = json.load(f)

except:
    saved_opportunities = []

if not saved_opportunities:

    st.info("No saved opportunities yet.")

else:

    saved_opportunities = sorted(
        saved_opportunities,
        key=lambda x: x["opportunity_score"],
        reverse=True
    )

    # ========================================
    # FOUNDER PORTFOLIO RANKING
    # ========================================

    st.markdown("## 🏆 Founder Portfolio Ranking")

    if len(saved_opportunities) >= 1:

        best = saved_opportunities[0]

        st.success(
            f"🏆 Best Startup To Build: "
            f"{best['startup_idea']} "
            f"(Score: {best['opportunity_score']})"
        )

    if len(saved_opportunities) >= 2:

        second = saved_opportunities[1]

        st.info(
            f"🥈 Runner Up: "
            f"{second['startup_idea']} "
            f"(Score: {second['opportunity_score']})"
        )

    if len(saved_opportunities) >= 3:

        third = saved_opportunities[2]

        st.warning(
            f"🥉 Third Choice: "
            f"{third['startup_idea']} "
            f"(Score: {third['opportunity_score']})"
        )

    # ========================================
    # FOUNDER DECISION ENGINE
    # ========================================

    st.divider()

    winner = saved_opportunities[0]

    reasons = []

    if winner.get("opportunity_score", 0) >= 75:
        reasons.append("Highest overall opportunity score")

    if winner.get("willingness_to_pay", 0) >= 4:
        reasons.append("Strong willingness to pay")

    if winner.get("frequency_estimate", 0) >= 4:
        reasons.append("High frequency customer pain")

    if winner.get("severity", 0) >= 4:
        reasons.append("Severe customer problem")

    if winner.get("competition_level", 5) <= 2:
        reasons.append("Relatively low competition")

    reasons.append("Clear target customer segment")
    reasons.append("Fast MVP validation potential")

    confidence = round(
    (
        winner.get("severity", 0)
        + winner.get("frequency_estimate", 0)
        + winner.get("willingness_to_pay", 0)
        + winner.get("evidence_strength", 0)
    ) / 20 * 100
)

    st.markdown("## 🎯 Founder Decision Engine")

    st.success(
    f"Recommended Build: {winner['category']}"
)

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "Opportunity Score",
            winner["opportunity_score"]
        )

    with col2:
        st.metric(
            "Confidence",
            f"{confidence}%"
        )

    st.markdown("### Why This Opportunity?")

    for reason in reasons:
        st.markdown(f"• {reason}")

# ========================================

# PORTFOLIO ANALYTICS

# ========================================

st.divider()

st.markdown("## 📊 Portfolio Analytics")

total = len(saved_opportunities)

avg_score = round(
sum(o["opportunity_score"] for o in saved_opportunities) / total,
1
)

best_score = max(
o["opportunity_score"] for o in saved_opportunities
)

categories = len(
set(o["category"] for o in saved_opportunities)
)

c1, c2, c3, c4 = st.columns(4)

c1.metric("Saved", total)
c2.metric("Avg Score", avg_score)
c3.metric("Best Score", best_score)
c4.metric("Categories", categories)

chart_df = pd.DataFrame({
"Opportunity": [
f"#{i+1}"
for i in range(len(saved_opportunities))
],
"Score": [
o["opportunity_score"]
for o in saved_opportunities
]
})

import plotly.express as px

fig = px.bar(
chart_df,
x="Opportunity",
y="Score"
)

fig.update_layout(
bargap=0.8,
height=350
)

st.plotly_chart(
fig,
use_container_width=True
)

# ========================================

# FOUNDER REPORT EXPORT

# ========================================

st.divider()

if st.button("📄 Generate Founder Report"):


    report = []

    report.append("# Founder Intelligence Report\n")

    report.append(
    f"Recommended Build: {winner['category']}"
)

    report.append(
    f"Opportunity Score: {winner['opportunity_score']}"
)

    report.append(
    f"Confidence: {confidence}%"
)

    report.append("\n")
    report.append("## Portfolio Ranking")

    for i, opp in enumerate(saved_opportunities, start=1):

        report.append(
        f"{i}. {opp['category']} "
        f"(Score: {opp['opportunity_score']})"
    )

    report.append("\n")

    report.append(
    f"Total Opportunities: {total}"
)

    report.append(
    f"Average Score: {avg_score}"
)

    report.append(
    f"Best Score: {best_score}"
)

    report.append(
    f"Categories: {categories}"
)

    buffer = BytesIO()

    doc = SimpleDocTemplate(buffer)

    styles = getSampleStyleSheet()

    content = []

    content.append(
    Paragraph(
        "Founder Intelligence Report",
        styles["Title"]
    )
)

    content.append(Spacer(1, 12))

    for line in report:

        content.append(
        Paragraph(
            str(line),
            styles["BodyText"]
        )
    )

    doc.build(content)

    pdf = buffer.getvalue()

    buffer.close()

    st.download_button(
    label="⬇ Download PDF Report",
    data=pdf,
    file_name="founder_report.pdf",
    mime="application/pdf"
)


# ========================================

# SAVED OPPORTUNITIES LIST

# ========================================

st.divider()

st.markdown("## 📂 Saved Opportunity Library")

for opp in saved_opportunities:


    st.markdown("---")

    st.subheader(
    opp["startup_idea"]
)

    st.write(
    f"**Score:** {opp['opportunity_score']}"
)

    st.write(
    f"**Category:** {opp['category']}"
)

    st.write(
    f"**Problem:** {opp['problem']}"
)

    st.write(
    f"**Target Customer:** {opp['target_customer']}"
)
