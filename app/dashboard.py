import json
import pandas as pd
import streamlit as st

from scripts.ranking_engine import rank_opportunities
from scripts.recommendation_engine import generate_recommendation
from scripts.ai_advisor_engine import (generate_ai_advice)
from scripts.live_analyzer import (analyze_complaint)
st.set_page_config(
    page_title="Founder Intelligence Platform",
    layout="wide"
)

# =====================================
# SIDEBAR
# =====================================

st.sidebar.markdown("""
# 🚀 Founder Intelligence

AI-powered startup opportunity discovery
""")

page = st.sidebar.selectbox(
    "Navigation",
    [
        "Dashboard",
        "Opportunities",
        "AI Advisor",
        "Analyze Complaints"
    ]
)

# =====================================
# LOAD DATA
# =====================================

with open(
    "data/processed/opportunities.json",
    "r",
    encoding="utf-8"
) as f:
    opportunities = json.load(f)

ranked_opportunities = rank_opportunities(
    opportunities
)

top_opportunity = ranked_opportunities[0]

# =====================================
# CATEGORY COUNTS
# =====================================

category_counts = {}

for opp in ranked_opportunities:

    category = opp["category"]

    if category not in category_counts:
        category_counts[category] = 0

    category_counts[category] += 1

top_trend = max(
    category_counts,
    key=category_counts.get
)

recommendation = generate_recommendation(
    top_opportunity,
    top_trend
)

pain_counts = {}

for opp in ranked_opportunities:

    pain = opp["pain_type"]

    if pain not in pain_counts:
        pain_counts[pain] = 0

    pain_counts[pain] += 1


# =====================================
# SIDEBAR STATS
# =====================================

st.sidebar.markdown("---")

st.sidebar.markdown(
    f"""
**Version:** 0.1

**Data Source:** Founder Dataset

**Opportunities:** {len(ranked_opportunities)}

**Categories:** {len(category_counts)}
"""
)

st.sidebar.markdown("---")

# =====================================
# DASHBOARD PAGE
# =====================================

if page == "Dashboard":

    st.markdown("""
# 🚀 Founder Intelligence Platform

### Discover startup opportunities from founder pain points using AI
""")

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "📈 Opportunities",
        len(ranked_opportunities)
    )

    col2.metric(
        "🏆 Top Score",
        top_opportunity["opportunity_score"]
    )

    col3.metric(
        "🔥 Categories",
        len(category_counts)
    )

    st.divider()

    left, right = st.columns(2)

    with left:

        st.subheader("🔥 Top Trend")

        st.success(top_trend)

        st.subheader("📊 Category Breakdown")

        category_df = pd.DataFrame(
            {
                "Category": list(category_counts.keys()),
                "Mentions": list(category_counts.values())
            }
        )

        st.bar_chart(
            category_df.set_index("Category")
        )

        st.subheader("🎯 Pain Type Distribution")

        pain_df = pd.DataFrame(
            {
                "Pain Type": list(pain_counts.keys()),
                "Count": list(pain_counts.values())
            }
        )

        st.bar_chart(
            pain_df.set_index("Pain Type")
        )

    with right:

        st.subheader("🤖 Recommended Startup")

    st.markdown(
    f"""
### {recommendation['startup_idea']}

**Target Customer**

{recommendation['target_customer']}

**Difficulty**

{recommendation['difficulty']}

**Why This Opportunity?**

{recommendation['reason']}
"""
)

# =====================================
# OPPORTUNITIES PAGE
# =====================================

if page == "Opportunities":

    st.title("📋 Opportunity Rankings")

    rankings_df = pd.DataFrame(
        ranked_opportunities
    )

    selected_category = st.selectbox(
    "Category",
    ["All"] + sorted(
        rankings_df["category"].unique()
    )
    )

    selected_pain = st.selectbox(
    "Pain Type",
    ["All"] + sorted(
        rankings_df["pain_type"].unique()
    )
    )

    minimum_score = st.slider(
    "Minimum Score",
    0,
    100,
    50
)

    filtered_df = rankings_df.copy()

    if selected_category != "All":

        filtered_df = filtered_df[
            filtered_df["category"]== selected_category]

    if selected_pain != "All":

        filtered_df = filtered_df[
            filtered_df["pain_type"]== selected_pain
    ]

    filtered_df = filtered_df[
        filtered_df["opportunity_score"]>= minimum_score]

    st.divider()

    st.subheader("🔍 Opportunity Explorer")

    if len(filtered_df) > 0:

        selected_problem = st.selectbox(
            "Select an Opportunity",
            filtered_df["problem"].tolist()
        )

        selected_opportunity = next(
            opp
            for opp in ranked_opportunities
            if opp["problem"] == selected_problem
        )

        st.info(
            f"""
Problem:
{selected_opportunity['problem']}

Category:
{selected_opportunity['category']}

Pain Type:
{selected_opportunity['pain_type']}

Opportunity Score:
{selected_opportunity['opportunity_score']}
"""
        )

        if st.button("Generate Startup Analysis"):

            with st.spinner(
                "Analyzing opportunity..."
            ):

                try:

                    analysis = generate_ai_advice(
                        selected_opportunity
                    )

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

                st.markdown(analysis)

    else:

        st.warning(
            "No opportunities match the selected filters."
        )

# =====================================
# AI ADVISOR PAGE
# =====================================

if page == "AI Advisor":

    st.title("🤖 AI Founder Advisor")

    st.subheader(
        "Top Opportunity"
    )

    st.info(
        top_opportunity["problem"]
    )

    st.metric(
        "Opportunity Score",
        top_opportunity["opportunity_score"]
    )

    st.subheader(
        "AI Startup Recommendation"
    )

    try:

        ai_advice = generate_ai_advice(
            top_opportunity
        )

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

    st.markdown(ai_advice)

# =====================================
# ANALYZE COMPLAINTS PAGE
# =====================================

if page == "Analyze Complaints":

    st.title("📝 Analyze Founder Complaints")

    st.write(
        "Paste founder complaints below, one per line."
    )

    complaints_text = st.text_area(
        "Founder Complaints",
        height=250,
        placeholder="""
Customer interviews take forever
Finding early adopters is difficult
Competitor pricing changes constantly
"""
    )

    if st.button(
        "Analyze Complaints"
    ):

        if complaints_text.strip():

            complaints = [
                line.strip()
                for line in complaints_text.split("\n")
                if line.strip()
            ]

            results = []

            for complaint in complaints:

                result = analyze_complaint(complaint)

                results.append(result)

            for result in results:

                st.subheader("Analysis")

            st.json(result)

            st.subheader(
                "Preview"
            )

            for complaint in complaints:

                st.write(
                    f"• {complaint}"
                )

            st.success("Opportunity analysis completed successfully.")

        else:

            st.warning(
                "Please enter at least one complaint."
            )