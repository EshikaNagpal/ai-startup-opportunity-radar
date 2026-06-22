import streamlit as st
import json

st.set_page_config(
    page_title="Saved Opportunities",
    page_icon="💾",
    layout="wide"
)

st.title("💾 Saved Opportunities")

try:

    with open(
        "data/live/saved_opportunities.json",
        "r",
        encoding="utf-8"
    ) as f:

        opportunities = json.load(f)

except:

    opportunities = []

st.metric(
    "Saved Opportunities",
    len(opportunities)
)

st.divider()

if not opportunities:

    st.info(
        "No opportunities saved yet."
    )

else:

    for opp in opportunities:

        with st.container():

            st.subheader(
                opp.get("title", "Untitled")
            )

            st.caption(
                f"Source: {opp.get('source', 'Unknown')}"
            )

            if opp.get("text"):
                st.write(
                    opp.get("text")
                )

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric(
                    "Comments",
                    opp.get("comments", 0)
                )

            with col2:
                st.metric(
                    "Pain Score",
                    opp.get("pain_score", 0)
                )

            with col3:
                st.metric(
                    "Signal Score",
                    round(
                        opp.get(
                            "signal_score",
                            0
                        ),
                        2
                    )
                )

            st.divider()