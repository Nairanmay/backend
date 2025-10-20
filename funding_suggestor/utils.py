import google.generativeai as genai
import os
import re
import json

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

def call_gemini_model(prompt: str) -> str:
    model = genai.GenerativeModel("gemini-pro") # Use this one
    response = model.generate_content(prompt)
    return response.text

def get_funding_suggestion_from_ai(company_type, company_phase, funds_required):
    prompt = (
        f"You are an expert startup funding advisor.\n"
       f"A {company_phase} phase {company_type} company requires ₹{funds_required}.\n"
        "Respond ONLY with valid JSON, using exactly these keys:\n"
        '{"investor_type": string, "equity_to_dilute": number, "explanation": string}\n'
        "No extra text, no markdown.\n"
    )

    ai_text = call_gemini_model(prompt).strip()

    # Clean up possible code fences
    cleaned_text = ai_text.strip("` \n")

    try:
        # Try direct JSON load first
        result = json.loads(cleaned_text)
    except json.JSONDecodeError:
        # Fallback: find first JSON object in text
        match = re.search(r"\{[^{}]+\}", cleaned_text, re.DOTALL)
        if not match:
            raise ValueError(f"Invalid AI output: {cleaned_text}")
        result = json.loads(match.group())

    # Extract and validate
    investor_type = result.get("investor_type") or "Unknown"

    raw_equity = str(result.get("equity_to_dilute", "0")).replace("%", "").strip()
    try:
        equity_to_dilute = float(re.findall(r"[\d.]+", raw_equity)[0])
    except (IndexError, ValueError):
        equity_to_dilute = 0.0

    explanation = result.get("explanation") or ""

    return investor_type, equity_to_dilute, explanation