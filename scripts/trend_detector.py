import json
from ranking_engine import rank_opportunities

with open(
    "data/processed/test_opportunities.json",
    "r",
    encoding="utf-8"
) as f:
    opportunities = json.load(f)

ranked_opportunities = rank_opportunities(opportunities)

trend_stats = {}

for opp in ranked_opportunities:
    category = opp["category"]

    if category not in trend_stats:
        trend_stats[category] = {
            "mentions": 0,
            "total_score": 0
        }

    trend_stats[category]["mentions"] += 1
    trend_stats[category]["total_score"] += opp["opportunity_score"]

sorted_trends = sorted(
    trend_stats.items(),
    key=lambda item: item[1]["mentions"],
    reverse=True
)

print("\nFOUNDER TREND REPORT\n")

for i, (category, stats) in enumerate(sorted_trends, start=1):

    average_score = (
        stats["total_score"] / stats["mentions"]
    )

    print(f"{i}. {category}")
    print(f"   Mentions: {stats['mentions']}")
    print(f"   Average Score: {average_score:.1f}\n")