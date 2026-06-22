import json
import time
from scripts.live_analyzer import analyze_complaint
from scripts.ranking_engine import rank_opportunities
from scripts.trend_tracker import save_snapshot
INPUT_FILE = "data/raw/founder_complaints.txt"

print(f"\nLoading data from: {INPUT_FILE}\n")

with open(
    INPUT_FILE,
    "r",
    encoding="utf-8"
) as f:

    complaints = [
        line.strip()
        for line in f.readlines()
        if line.strip()
    ]

results = []

for complaint in complaints:

    try:

        data = analyze_complaint(
            complaint
        )

        results.append(data)

        print(
            f"Processed: {complaint}"
        )
        time.sleep(7)

    except Exception as e:

        print(
            f"Failed: {complaint}"
        )

        print(e)

ranked_results = rank_opportunities(
    results
)

print("\nRANKED RESULTS:")

print(
    json.dumps(
        ranked_results,
        indent=4
    )
)

print(f"Saving {len(ranked_results)} opportunities")

save_snapshot(ranked_results)

with open(
    "data/processed/opportunities.json",
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        ranked_results,
        f,
        indent=4,
        ensure_ascii=False
    )

print(
    f"\nSaved {len(ranked_results)} opportunities."
)