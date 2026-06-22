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
You are an elite startup analyst.

Analyze the complaint.

Identify:

1. Core problem
2. Startup opportunity
3. Best target customer
4. Recommended pricing model
5. Lean MVP idea

Return ONLY valid JSON.

Startup ideas should be realistic,
software-first,
and achievable by a small startup team.

Schema:

{{
    "problem": "",
    "category": "",
    "pain_type": "",

    "startup_idea": "",
    "target_customer": "",
    "pricing_model": "",
    "mvp_description": "",

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

        required_fields = [
            "startup_idea",
            "target_customer",
            "pricing_model",
            "mvp_description"
        ]

        for field in required_fields:
            data.setdefault(field, "")

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

            "startup_idea": "Unknown",
            "target_customer": "Unknown",
            "pricing_model": "Unknown",
            "mvp_description": "Unknown",

            "severity": 1,
            "frequency_estimate": 1,
            "willingness_to_pay": 1,
            "competition_level": 10,
            "evidence_strength": 1,

            "opportunity_score": 0
        }