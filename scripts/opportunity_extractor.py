import os
import json
import time
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

complaint = """
I spend hours validating startup ideas.
Most ideas already exist and I don't know
what problems are worth solving.
"""

prompt = f"""
You are an expert startup analyst.

Analyze the complaint and return ONLY valid JSON.

Opportunity Score Rules:

Return an integer between 1 and 10 only.

1-3 = weak opportunity
4-6 = moderate opportunity
7-8 = strong opportunity
9-10 = exceptional opportunity

The score must consider:
- severity
- frequency
- willingness to pay
- competition level

Lower competition should increase the score.

Required format:

{{
    "problem": "",
    "category": "",
    "severity": 0,
    "customer_type": "",
    "opportunity": ""
}}

Complaint:
{complaint}
"""

for attempt in range(3):

    try:

        response = client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=prompt
        )

        break

    except Exception as e:

        print(f"Attempt {attempt + 1} failed")

        if attempt == 2:
            raise

        time.sleep(5)