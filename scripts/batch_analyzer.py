import os
import json
from dotenv import load_dotenv
from google import genai
from ranking_engine import rank_opportunities
load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

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

    prompt = f"""
        You are a startup analyst.

        Return ONLY valid JSON.

        Return EXACTLY this schema:

    {{
        "problem": "",
        "category": "",
        "pain_type": "",
        "severity": 0,
        "frequency_estimate": 0,
        "willingness_to_pay": 0,
        "competition_level": 0,
        "evidence_strength": 0
    }}

    pain_type must be exactly one of:
    Time
    Money
    Productivity
    Trust
    Compliance
    Emotional

    Do not include:
    - reasoning
    - explanations
    - notes
    - opportunity_score
    - markdown
    - code fences
    

    target_customer should identify the primary affected customer segment.

Examples:
- Startup Founders
- Product Managers
- SaaS Companies
- Small Businesses
- Freelancers
- Recruiters
- Students

Complaint:
{complaint}
"""

    try:

        response = client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=prompt
        )

        cleaned = (
            response.text
            .replace("```json", "")
            .replace("```", "")
            .strip()
        )

        data = json.loads(cleaned)

        results.append(data)


        print(f"Processed: {complaint}")

    except Exception as e:

        print(f"Failed: {complaint}")
        print(e)
ranked_results = rank_opportunities(results)
print("\nRANKED RESULTS:")
print(json.dumps(ranked_results, indent=4))

with open(
    "data/processed/opportunities.json",
    "w",
    encoding="utf-8"
) as f:

    json.dump(ranked_results, f, indent=4)

print(f"\nSaved {len(results)} opportunities.")