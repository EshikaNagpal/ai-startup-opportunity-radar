import os

from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

def generate_ai_advice(opportunity):

    prompt = f"""
You are an expert startup advisor.

Based on this opportunity:

Problem:
{opportunity["problem"]}

Category:
{opportunity["category"]}

Pain Type:
{opportunity["pain_type"]}

Opportunity Score:
{opportunity["opportunity_score"]}

Provide:

1. Startup Idea
2. Target Customer
3. Difficulty
4. Why Now
5. Go-To-Market

Keep the response concise.
"""

    try:

        response = client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=prompt
        )

        return response.text

    except Exception as e:

        print("Gemini Error:", e)

        return """
### Startup Idea
AI Customer Discovery Platform

### Target Customer
Startup Founders and Product Teams

### Difficulty
Medium

### Why Now
Customer research and interview analysis remain time-consuming for founders.

### Go-To-Market
Partner with startup communities and accelerators.
"""