import os
import json
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

try:
    response = client.models.generate_content(
        model="gemini-2.5-flash-lite",
        contents=prompt
    )

    print(response.text)

except Exception as e:
    print(f"Error: {e}")

print(response.text)