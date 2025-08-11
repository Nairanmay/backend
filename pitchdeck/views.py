from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from django.http import JsonResponse
from .utils import extract_text_from_pdf, analyze_with_gemini
from .models import PitchDeckAnalysis
from .serializers import PitchDeckAnalysisSerializer  # <--- Add this line

class PitchDeckAnalysisView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        if request.user.role != "admin":
            return Response({"error": "Only admins can upload pitch decks."}, status=status.HTTP_403_FORBIDDEN)

        pdf_file = request.FILES.get("file")
        if not pdf_file:
            return JsonResponse({"error": "No PDF file uploaded"}, status=400)

        try:
            text = extract_text_from_pdf(pdf_file)
            analysis_result = analyze_with_gemini(text)

            pitch = PitchDeckAnalysis.objects.create(
                user=request.user,
                file=pdf_file,
                analysis_text=analysis_result.get("summary", ""),
                ratings=analysis_result.get("ratings", {}),
                chart_data={},  # You can later generate charts here
            )

            serializer = PitchDeckAnalysisSerializer(pitch)
            return JsonResponse(serializer.data, safe=False)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
