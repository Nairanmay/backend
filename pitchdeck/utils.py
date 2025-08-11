import os
import fitz  # PyMuPDF
import google.generativeai as genai
import json

# ✅ Configure Gemini API key
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def extract_text_from_pdf(pdf_file):
    """Extract all text from PDF using PyMuPDF."""
    text = ""
    with fitz.open(stream=pdf_file.read(), filetype="pdf") as doc:
        for page in doc:
            text += page.get_text()
    return text

def analyze_with_gemini(text):
    """Send extracted text to Google Gemini for analysis."""
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

    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(prompt)

    try:
        # Ensure the output is valid JSON
        result = json.loads(response.text)
    except json.JSONDecodeError:
        result = {"error": "Invalid JSON from AI", "raw_output": response.text}

    return result
