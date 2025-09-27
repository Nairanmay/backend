import os
import fitz  # PyMuPDF
import google.generativeai as genai
import json
from dotenv import load_dotenv
import re

# ✅ Load environment variables from .env
load_dotenv()

# ✅ Configure Gemini API key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError(
        "❌ GEMINI_API_KEY is not set. Please add it to your .env file.\n"
        "Example: GEMINI_API_KEY=your_api_key_here"
    )

genai.configure(api_key=GEMINI_API_KEY)


def extract_text_from_pdf(pdf_file):
    """Extract all text from PDF using PyMuPDF."""
    text = ""
    with fitz.open(stream=pdf_file.read(), filetype="pdf") as doc:
        for page in doc:
            text += page.get_text()
    return text


import json
import re

def analyze_with_gemini(text):
    prompt = f"""
You are a startup pitch deck analyzer. Analyze the following pitch deck text strictly.

Provide ONLY a JSON object with the following keys (no extra text or explanation):

1. summary (string): A clear and concise summary.
2. strengths (array of strings): List key strengths.
3. weaknesses (array of strings): List key weaknesses.
4. ratings (object): Ratings on a scale of 1-10 with keys: market_potential, team_strength, clarity.
5. suggestions (array of strings): Concrete suggestions for improvement.

Pitch Deck Text:
\"\"\"
{text}
\"\"\"
"""

    model_name = "models/gemini-flash-latest"  # ✅ Use a valid model from your list

    # Use chat.completions.create() for text generation
    response = genai.chat.completions.create(
        model=model_name,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_output_tokens=500
    )

    # Extract the AI's response
    raw_text = response.choices[0].message.content
    print("Raw AI output:", raw_text)

    # Clean markdown code blocks if present
    cleaned_text = re.sub(r"```json|```", "", raw_text).strip()

    try:
        match = re.search(r"\{.*\}", cleaned_text, re.DOTALL)
        if match:
            json_str = match.group()
            result = json.loads(json_str)

            # Ensure keys exist
            result.setdefault("summary", "")
            result.setdefault("strengths", [])
            result.setdefault("weaknesses", [])
            result.setdefault("ratings", {
                "market_potential": 0,
                "team_strength": 0,
                "clarity": 0,
            })
            result.setdefault("suggestions", [])

        else:
            raise ValueError("No JSON object found in AI response")

    except Exception as e:
        print("JSON parse error:", str(e))
        result = {
            "summary": cleaned_text,
            "strengths": [],
            "weaknesses": [],
            "ratings": {
                "market_potential": 0,
                "team_strength": 0,
                "clarity": 0,
            },
            "suggestions": [],
            "error": f"Failed to parse JSON: {str(e)}"
        }

    return result