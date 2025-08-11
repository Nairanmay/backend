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
    You are a startup pitch deck analyzer. Analyze the following pitch deck text:
    {text}

    Provide:
    1. A clear summary.
    2. Strengths & weaknesses.
    3. Ratings (market potential, team strength, clarity) from 1-10.
    4. Suggestions for improvement.

    Format the result in JSON with keys:
    summary, strengths, weaknesses, ratings, suggestions
    """
    model = genai.GenerativeModel("models/gemini-1.5-flash-latest")
    response = model.generate_content(prompt)
    print("Raw AI output:", response.text)

    # Clean markdown code blocks if present
    cleaned_text = re.sub(r"```json|```", "", response.text).strip()

    try:
        match = re.search(r"\{.*\}", cleaned_text, re.DOTALL)
        if match:
            json_str = match.group()
            result = json.loads(json_str)
        else:
            raise ValueError("No JSON object found in AI response")
    except Exception as e:
        result = {
            "summary": cleaned_text,
            "strengths": [],
            "weaknesses": [],
            "ratings": {},
            "suggestions": [],
            "error": f"Failed to parse JSON: {str(e)}"
        }

    return result