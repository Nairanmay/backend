import os
import re
import json
import google.generativeai as genai
from django.conf import settings

# Configure Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise EnvironmentError(
        "❌ Missing GEMINI_API_KEY. Please set it in environment variables."
    )

genai.configure(api_key=GEMINI_API_KEY)

def call_gemini_model(prompt: str) -> str:
    """
    Calls Gemini model to generate structured funding advice.
    """
    try:
        model = genai.GenerativeModel(model_name="gemini-2.5-flash")  # Updated to valid model
        response = model.generate_content(prompt)
        return response.text.strip() if hasattr(response, "text") else str(response).strip()
    except Exception as e:
        raise RuntimeError(f"Gemini API error: {str(e)}")

def get_funding_suggestion_from_ai(company_type: str, company_phase: str, funds_required: str):
    """
    Generates funding suggestions from Gemini model and returns
    (investor_type, equity_to_dilute, explanation)
    """
    prompt = (
        f"You are an expert startup funding advisor with decades of experience.\n"
        f"A {company_phase} phase {company_type} company requires ₹{funds_required}.\n"
        "Respond ONLY with valid JSON, using exactly these keys:\n"
        '{"investor_type": string, "equity_to_dilute": number, "explanation": string}\n'
        "The explanation must be very detailed (at least 300-400 words), structured in paragraphs, "
        "covering reasoning behind the suggestion, benefits, risks, market context, funding options, "
        "and actionable advice. Include examples and multiple perspectives if possible.\n"
        "Do NOT include markdown, extra text, or commentary outside the JSON.\n"
    )

    ai_text = call_gemini_model(prompt)

    # Clean up possible markdown/code formatting
    cleaned_text = ai_text.strip("` \n")

    try:
        # Try direct JSON parsing
        result = json.loads(cleaned_text)
    except json.JSONDecodeError:
        # Try to find JSON object inside the text
        match = re.search(r"\{.*\}", cleaned_text, re.DOTALL)
        if not match:
            raise ValueError(f"Invalid AI output (no JSON found): {cleaned_text}")
        try:
            result = json.loads(match.group())
        except Exception:
            raise ValueError(f"Invalid JSON extracted: {match.group()}")

    # Extract and sanitize values
    investor_type = str(result.get("investor_type", "Unknown")).strip()

    raw_equity = str(result.get("equity_to_dilute", "0")).replace("%", "").strip()
    try:
        equity_to_dilute = float(re.findall(r"[\d.]+", raw_equity)[0])
    except (IndexError, ValueError):
        equity_to_dilute = 0.0

    explanation = str(result.get("explanation", "")).strip()

    return investor_type, equity_to_dilute, explanation


# Optional: Test function locally
if __name__ == "__main__":
    investor, equity, explanation = get_funding_suggestion_from_ai("AI startup", "seed", "5000000")
    print("Investor Type:", investor)
    print("Equity to Dilute (%):", equity)
    print("Explanation:\n", explanation)
