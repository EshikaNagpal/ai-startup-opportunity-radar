import json
import pandas as pd
import streamlit as st

from scripts.ranking_engine import rank_opportunities

st.set_page_config(
    page_title="Founder Intelligence Platform",
    layout="wide"
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

# Dashboard Header
st.title("🚀 Founder Intelligence Platform")

# Metrics
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

# Trend Section
st.subheader("🔥 Top Trend")
st.write(top_trend)

# Category Breakdown
st.subheader("📊 Category Breakdown")

category_df = pd.DataFrame(
    {
        "Category": list(category_counts.keys()),
        "Mentions": list(category_counts.values())
    }
)

st.dataframe(
    category_df,
    use_container_width=True
)

st.bar_chart(
    category_df.set_index("Category")
)

# Opportunity Section
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

# Full Rankings
st.subheader("📋 Opportunity Rankings")

rankings_df = pd.DataFrame(ranked_opportunities)

st.dataframe(
    rankings_df[
        [
            "problem",
            "category",
            "pain_type",
            "opportunity_score"
        ]
    ],
    use_container_width=True
)