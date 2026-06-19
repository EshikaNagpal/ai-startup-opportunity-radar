import os
import json

from dotenv import load_dotenv
from google import genai

from scripts.scoring_engine import (
    calculate_opportunity_score
)

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


def analyze_complaint(complaint):

    prompt = f"""
You are a startup analyst.

Return ONLY valid JSON.

Schema:

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

        score = calculate_opportunity_score(
            data
        )

        data["opportunity_score"] = score

        return data

    except Exception as e:

        print("Analyzer Error:", e)

        return {
            "problem": complaint,
            "category": "Unknown",
            "pain_type": "Unknown",
            "severity": 5,
            "frequency_estimate": 5,
            "willingness_to_pay": 5,
            "competition_level": 5,
            "evidence_strength": 5,
            "opportunity_score": 50
        }