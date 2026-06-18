import json
from ranking_engine import rank_opportunities

with open(
    "data/processed/test_opportunities.json",
    "r",
    encoding="utf-8"
) as f:
    opportunities = json.load(f)

ranked_opportunities = rank_opportunities(opportunities)

top_opportunity = ranked_opportunities[0]

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

print("=" * 40)
print("FOUNDER INTELLIGENCE REPORT")
print("=" * 40)

print("\nTOP TREND")
print(f"Category: {top_trend}")
print(f"Mentions: {category_counts[top_trend]}")

print("\nTOP OPPORTUNITY")
print(top_opportunity["problem"])
print(
    f"Score: {top_opportunity['opportunity_score']}"
)

print("\nPAIN TYPE")
print(top_opportunity["pain_type"])

print("\nRECOMMENDED STARTUP ANGLE")

if top_trend == "Customer Research":
    print(
        "Build a customer feedback intelligence platform."
    )

elif top_trend == "Competitive Intelligence":
    print(
        "Build an automated competitor monitoring tool."
    )

elif top_trend == "Startup Validation":
    print(
        "Build an AI-powered idea validation platform."
    )

else:
    print(
        "Investigate this category further."
    )