import os
import json
import google.generativeai as genai
from PyPDF2 import PdfReader

# ----------------------------
# 1. Configure Gemini API
# ----------------------------
API_KEY = os.getenv("GEMINI_API_KEY")  # Make sure you set this in your environment
if not API_KEY:
    raise ValueError("❌ Please set your GEMINI_API_KEY environment variable")

genai.configure(api_key=API_KEY)

# ----------------------------
# 2. Extract text from PDF
# ----------------------------
def extract_text_from_pdf(pdf_path):
    """Extracts all text from a PDF file."""
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text.strip()

# ----------------------------
# 3. Analyze text with Gemini
# ----------------------------
def analyze_with_gemini(text):
    """Sends text to Gemini for structured analysis."""
    model = genai.GenerativeModel("gemini-1.5-flash")

    prompt = f"""
    You are analyzing a startup pitch deck. 
    Extract key information and return it as JSON with the following fields:

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

    Text to analyze:
    {text}
    """

    response = model.generate_content(prompt)

    try:
        # Try to parse model output as JSON
        return json.loads(response.text)
    except json.JSONDecodeError:
        # If model didn’t output valid JSON, return raw text
        return {"raw_response": response.text}

# ----------------------------
# 4. Main program
# ----------------------------
if __name__ == "__main__":
    # Ask user for PDF path
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
