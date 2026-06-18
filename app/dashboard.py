import json
import pandas as pd
import streamlit as st

from scripts.ranking_engine import rank_opportunities
from scripts.recommendation_engine import generate_recommendation

st.set_page_config(
    page_title="Founder Intelligence Platform",
    layout="wide"
)

st.sidebar.title("🚀 Founder Intelligence")

st.sidebar.markdown("---")

st.sidebar.markdown(
    """
    **Version:** 0.1

    **Data Source:** Founder Dataset

    **Opportunities:** 3
    """
)

st.sidebar.markdown("---")

page = st.sidebar.selectbox(
    "Navigation",
    [
        "Dashboard",
        "Opportunities"
    ]
)

# Load opportunities
with open(
    "data/processed/test_opportunities.json",
    "r",
    encoding="utf-8"
) as f:
    opportunities = json.load(f)

# Rank opportunities
ranked_opportunities = rank_opportunities(opportunities)

# Top opportunity
top_opportunity = ranked_opportunities[0]

# Category counts
category_counts = {}

for opp in ranked_opportunities:
    category = opp["category"]

    if category not in category_counts:
        category_counts[category] = 0

    category_counts[category] += 1

# Top trend
top_trend = max(
    category_counts,
    key=category_counts.get
)

# Recommendation
recommendation = generate_recommendation(
    top_opportunity,
    top_trend
)

# DASHBOARD PAGE
if page == "Dashboard":

    st.title("🚀 Founder Intelligence Platform")

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Opportunities",
        len(ranked_opportunities)
    )

    col2.metric(
        "Top Score",
        top_opportunity["opportunity_score"]
    )

    col3.metric(
        "Categories",
        len(category_counts)
    )

    st.divider()

    left, right = st.columns(2)

with left:

    st.subheader("🔥 Top Trend")
    st.write(top_trend)

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

with right:

    st.subheader("🏆 Top Opportunity")

    st.write(top_opportunity["problem"])

    st.write(
        f"Category: {top_opportunity['category']}"
    )

    st.write(
        f"Pain Type: {top_opportunity['pain_type']}"
    )

    st.write(
        f"Opportunity Score: {top_opportunity['opportunity_score']}"
    )

    st.subheader("💡 Founder Recommendation")

    st.info(
        f"""
    Recommended Startup

    {recommendation['startup_idea']}

    Target Customer:
    {recommendation['target_customer']}

    Difficulty:
    {recommendation['difficulty']}

    Reason:
    {recommendation['reason']}
    """
    )

    st.subheader("🏆 Top Opportunity")

    st.write(top_opportunity["problem"])

    st.write(
        f"Category: {top_opportunity['category']}"
    )

    st.write(
        f"Pain Type: {top_opportunity['pain_type']}"
    )

    st.write(
        f"Opportunity Score: {top_opportunity['opportunity_score']}"
    )

    st.subheader("💡 Founder Recommendation")

    st.info(
    f"""
    Recommended Startup

    {recommendation['startup_idea']}

    Target Customer:
    {recommendation['target_customer']}

    Difficulty:
    {recommendation['difficulty']}

    Reason:
    {recommendation['reason']}
    """)
    
# OPPORTUNITIES PAGE
if page == "Opportunities":

    st.title("📋 Opportunity Rankings")

    rankings_df = pd.DataFrame(
        ranked_opportunities
    )

    st.dataframe(
        rankings_df,
        use_container_width=True
    )