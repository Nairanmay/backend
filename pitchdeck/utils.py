import os
import re
import json
import google.generativeai as genai
from PyPDF2 import PdfReader

# ----------------------------
# 1. Configure Gemini API
# ----------------------------
API_KEY = os.getenv("GEMINI_API_KEY")  # Make sure this is set in your environment
if not API_KEY:
    raise ValueError("❌ Please set your GEMINI_API_KEY environment variable")

genai.configure(api_key=API_KEY)

# ----------------------------
# 2. Extract text from PDF
# ----------------------------
def extract_text_from_pdf(pdf_path):
    """Extract all text from a PDF file."""
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text.strip()

# ----------------------------
# 3. Analyze text with Gemini
# ----------------------------
def analyze_with_gemini(text):
    """
    Sends text to Gemini for structured analysis.
    Returns a Python dictionary with parsed JSON output.
    """
    model = genai.GenerativeModel(model_name="gemini-2.5-flash")

    prompt = f"""
    You are an expert startup analyst.
    Extract key information from the following pitch deck text and return it as JSON.
    Make the explanation sections long and detailed (3-4 sentences each).

    Fields to include:

    {{
        "startup_name": string,
        "problem_statement": string,
        "solution": string,
        "business_model": string,
        "target_market": string,
        "competition": string,
        "traction": string,
        "team": string,
        "financials": string,
        "funding_request": string,
        "strengths": [list of strings],
        "weaknesses": [list of strings]
    }}

    Pitch deck text:
    {text}
    """

    response = model.generate_content(prompt)

    # Clean possible markdown/code formatting
    raw_text = response.text.strip() if hasattr(response, "text") else str(response)
    cleaned_text = re.sub(r"^```(?:json)?|```$", "", raw_text, flags=re.MULTILINE).strip()

    try:
        return json.loads(cleaned_text)
    except json.JSONDecodeError:
        # Fallback: wrap raw response
        return {"raw_response": cleaned_text}

# ----------------------------
# 4. Main program
# ----------------------------
if __name__ == "__main__":
    pdf_path = input("📂 Enter the path to your pitch deck PDF: ").strip()

    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"❌ PDF file not found: {pdf_path}")

    print("⏳ Extracting text from PDF...")
    pdf_text = extract_text_from_pdf(pdf_path)

    print("⏳ Analyzing with Gemini...")
    analysis = analyze_with_gemini(pdf_text)

    # Print result
    print("\n--- Parsed Analysis ---")
    print(json.dumps(analysis, indent=4, ensure_ascii=False))

    # Save JSON file
    output_file = os.path.splitext(pdf_path)[0] + "_analysis.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(analysis, f, indent=4, ensure_ascii=False)

    print(f"\n✅ Analysis saved to {output_file}")
