import os
import json
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

with open("data/raw/sample_complaints.txt", "r", encoding="utf-8") as f:
    complaints = [line.strip() for line in f.readlines() if line.strip()]

results = []

for complaint in complaints:

    prompt = f"""
    You are a startup analyst.

    Return ONLY valid JSON.

    Replace the JSON schema with:

    {{
        "problem": "",
        "category": "",
        "severity": 0,
        "frequency_estimate": 0,
        "willingness_to_pay": 0,
        "competition_level": 0,
        "opportunity_score": 0,
        "reasoning": ""
        "evidence_strength": 0
    }}

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

with open(
    "data/processed/opportunities.json",
    "w",
    encoding="utf-8"
) as f:

    json.dump(results, f, indent=4)

print(f"\nSaved {len(results)} opportunities.")