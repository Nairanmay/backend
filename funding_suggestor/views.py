# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .utils import call_gemini_model
import re

def get_funding_suggestion_from_ai(company_type, company_phase, funds_required):
    prompt = (
        f"You are an expert startup funding advisor. "
        f"A {company_phase} phase {company_type} company requires ${funds_required}. "
        "Suggest the most suitable investor type and the recommended equity percentage to dilute from the founder's equity. "
        "Explain your reasoning briefly in the format:\n"
        "Investor type: <type>\n"
        "Equity to dilute: <percentage>%\n"
        "Explanation: <your explanation>"
    )

    ai_text = call_gemini_model(prompt)

    investor_type = "Unknown"
    equity_to_dilute = 0.0
    explanation = ai_text.strip()

    for line in ai_text.splitlines():
        line_lower = line.lower().strip()
        if line_lower.startswith("investor type"):
            investor_type = line.split(":", 1)[1].strip()
        elif line_lower.startswith("equity to dilute"):
            match = re.search(r"[\d.]+", line)
            if match:
                equity_to_dilute = float(match.group())

    return investor_type, equity_to_dilute, explanation


class FundingSuggestionView(APIView):
    def post(self, request):
        data = request.data
        company_name = data.get('company_name')
        company_type = data.get('company_type')
        company_phase = data.get('company_phase')
        founder_equity = data.get('founder_equity')  # in %
        funds_required = data.get('funds_required')

        if not all([company_name, company_type, company_phase, founder_equity, funds_required]):
            return Response({"error": "Missing fields"}, status=status.HTTP_400_BAD_REQUEST)

        investor_type, equity_to_dilute, explanation = get_funding_suggestion_from_ai(
            company_type, company_phase, funds_required
        )

        # ✅ Equity dilution happens from founder's equity
        founder_equity_after = max(0, founder_equity - equity_to_dilute)
        investor_equity = equity_to_dilute
        others_equity = 100 - founder_equity_after - investor_equity

        graphs_data = {
            "pie_chart": [
                {"name": "Founder Equity", "value": founder_equity_after},
                {"name": "Investor Equity", "value": investor_equity},
                {"name": "Other Shareholders", "value": others_equity}
            ],
            "bar_chart": [
                {"name": "Founder", "Before": founder_equity, "After": founder_equity_after},
                {"name": "Investor", "Before": 0, "After": investor_equity},
                {"name": "Others", "Before": 100 - founder_equity, "After": others_equity}
            ]
        }

        suggestion = {
            "investor_type": investor_type,
            "equity_to_dilute": equity_to_dilute,
            "explanation": explanation,
            "graphs_data": graphs_data
        }
        return Response(suggestion, status=status.HTTP_200_OK)
