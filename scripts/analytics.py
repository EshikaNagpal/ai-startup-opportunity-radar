import json
from ranking_engine import rank_opportunities

with open(
    "data/processed/test_opportunities.json",
    "r",
    encoding="utf-8"
) as f:
    opportunities = json.load(f)

ranked_opportunities = rank_opportunities(opportunities)

print("\nTOP OPPORTUNITIES\n")


for i, opp in enumerate(ranked_opportunities, start=1):
    print(
        f"{i}. {opp['problem']} "
        f"(Score: {opp['opportunity_score']})"
    )
print("\nPAIN TYPE BREAKDOWN\n")
pain_counts = {}

for opp in ranked_opportunities:
    pain_type = opp["pain_type"]

    if pain_type not in pain_counts:
        pain_counts[pain_type] = 0

    pain_counts[pain_type] += 1

for pain_type, count in pain_counts.items():
    print(f"{pain_type}: {count}")

print("\nCATEGORY BREAKDOWN\n")

category_counts = {}

for opp in ranked_opportunities:
    category = opp["category"]

    if category not in category_counts:
        category_counts[category] = 0

    category_counts[category] += 1

for category, count in category_counts.items():
    print(f"{category}: {count}")