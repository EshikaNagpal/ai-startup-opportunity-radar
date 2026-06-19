import json

from ai_advisor_engine import generate_ai_advice

with open(
    "data/processed/opportunities.json",
    "r",
    encoding="utf-8"
) as f:
    opportunities = json.load(f)

advice = generate_ai_advice(
    opportunities[0]
)

print(advice)