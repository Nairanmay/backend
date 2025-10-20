import google.generativeai as genai
import os
import json
import re

# ✅ Configure Gemini API (make sure GEMINI_API_KEY is set in Render environment)
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def call_gemini_model(prompt: str) -> str:
    """
    Calls Gemini 1.5 Pro to generate a structured JSON suggestion.
    """
    # Use latest model (v1, not v1beta)
    model = genai.GenerativeModel("gemini-1.5-pro")

    # Generate content safely
    response = model.generate_content(prompt)

    # Return model text safely
    return response.text.strip() if hasattr(response, "text") else str(response)

def get_funding_suggestion_from_ai(company_type, company_phase, funds_required):
    """
    Generates funding suggestions from Gemini model.
    """
    prompt = (
        f"You are an expert startup funding advisor.\n"
        f"A {company_phase} phase {company_type} company requires ₹{funds_required}.\n"
        "Respond ONLY with valid JSON, using exactly these keys:\n"
        '{"investor_type": string, "equity_to_dilute": number, "explanation": string}\n'
        "No extra text, no markdown.\n"
    )

    ai_text = call_gemini_model(prompt)

    # Remove code fences or formatting
    cleaned_text = ai_text.strip("` \n")

    try:
        # Try parsing directly
        result = json.loads(cleaned_text)
    except json.JSONDecodeError:
        # Fallback: find JSON inside text
        match = re.search(r"\{[^{}]+\}", cleaned_text, re.DOTALL)
        if not match:
            raise ValueError(f"Invalid AI output: {cleaned_text}")
        result = json.loads(match.group())

    # Extract and sanitize fields
    investor_type = result.get("investor_type", "Unknown")
    raw_equity = str(result.get("equity_to_dilute", "0")).replace("%", "").strip()
    try:
        equity_to_dilute = float(re.findall(r"[\d.]+", raw_equity)[0])
    except (IndexError, ValueError):
        equity_to_dilute = 0.0
    explanation = result.get("explanation", "")

    return investor_type, equity_to_dilute, explanation
