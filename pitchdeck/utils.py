import os
import fitz  # PyMuPDF
import google.generativeai as genai
import json
import re
from dotenv import load_dotenv

# -------------------------------
# Load environment variables
# -------------------------------
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError(
        "❌ GEMINI_API_KEY is not set. Please add it to your .env file.\n"
        "Example: GEMINI_API_KEY=your_api_key_here"
    )

genai.configure(api_key=GEMINI_API_KEY)

# -------------------------------
# PDF Text Extraction
# -------------------------------
def extract_text_from_pdf(pdf_file):
    """
    Extract all text from PDF using PyMuPDF.
    pdf_file: file-like object opened in 'rb' mode
    """
    text = ""
    with fitz.open(stream=pdf_file.read(), filetype="pdf") as doc:
        for page in doc:
            text += page.get_text()
    return text

# -------------------------------
# Gemini Analysis
# -------------------------------
def analyze_with_gemini(text):
    """
    Sends extracted text to Gemini and returns parsed JSON analysis.
    """
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

    # -------------------------------
    # Use a valid model from your account
    # -------------------------------
    model_name = "models/gemini-flash-latest"

    # Generate content via chat.completions.create
    response = genai.chat.completions.create(
        model=model_name,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_output_tokens=700
    )

    # Extract raw text from AI response
    raw_text = response.choices[0].message.content
    print("Raw AI output:\n", raw_text)

    # Remove markdown code blocks if present
    cleaned_text = re.sub(r"```json|```", "", raw_text).strip()

    # Parse JSON safely
    try:
        match = re.search(r"\{.*\}", cleaned_text, re.DOTALL)
        if match:
            json_str = match.group()
            result = json.loads(json_str)

            # Ensure all keys exist
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

# -------------------------------
# Example Usage
# -------------------------------
if __name__ == "__main__":
    pdf_path = "example_pitch_deck.pdf"  # Replace with your PDF file path

    with open(pdf_path, "rb") as f:
        pdf_text = extract_text_from_pdf(f)

    analysis = analyze_with_gemini(pdf_text)

    # Print formatted JSON
    print("\n--- Parsed Analysis ---")
    print(json.dumps(analysis, indent=4))
