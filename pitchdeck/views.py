from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from .utils import extract_text_from_pdf, analyze_with_gemini
from .models import PitchDeckAnalysis
from .serializers import PitchDeckAnalysisSerializer

class PitchDeckAnalysisView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        pdf_file = request.FILES.get("file")
        if not pdf_file:
            return JsonResponse({"error": "No PDF file uploaded"}, status=400)

        try:
            # Extract and analyze
            text = extract_text_from_pdf(pdf_file)
            analysis_result = analyze_with_gemini(text)

            # Save to DB
            pitch = PitchDeckAnalysis.objects.create(
                user=request.user if request.user.is_authenticated else None,
                file=pdf_file,
                analysis_text=analysis_result.get("summary", ""),
                ratings=analysis_result.get("ratings", {}),
                chart_data={},  # You can later generate charts here
            )

            serializer = PitchDeckAnalysisSerializer(pitch)
            return JsonResponse(serializer.data, safe=False)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
