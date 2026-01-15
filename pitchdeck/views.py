from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from .utils import extract_text_from_pdf, analyze_with_gemini
from .models import PitchDeckAnalysis
from .serializers import PitchDeckAnalysisSerializer

class PitchDeckAnalysisView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    def get(self, request, *args, **kwargs):
        """
        Retrieve the latest pitch deck analysis for the logged-in user.
        """
        try:
            # Get the latest analysis object created by this user
            latest_analysis = PitchDeckAnalysis.objects.filter(user=request.user).latest('id')
            serializer = PitchDeckAnalysisSerializer(latest_analysis)
            return Response(serializer.data)
        except PitchDeckAnalysis.DoesNotExist:
            return Response({"error": "No pitch deck analysis found."}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request, *args, **kwargs):
        if not hasattr(request.user, "role") or request.user.role != "admin":
            return Response(
                {"error": "Only admins can upload pitch decks."},
                status=status.HTTP_403_FORBIDDEN,
            )

        pdf_file = request.FILES.get("file")
        if not pdf_file:
            return Response(
                {"error": "No PDF file uploaded"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            text = extract_text_from_pdf(pdf_file)
            analysis_result = analyze_with_gemini(text)
            
            pitch = PitchDeckAnalysis.objects.create(
                user=request.user,
                file=pdf_file,
                analysis_text=analysis_result.get("summary", ""),
                strengths=analysis_result.get("strengths", []),
                weaknesses=analysis_result.get("weaknesses", []),
                suggestions=analysis_result.get("suggestions", []),
                ratings=analysis_result.get("ratings", {}),
                chart_data={},  
            )

            serializer = PitchDeckAnalysisSerializer(pitch)
            return Response(serializer.data)

        except Exception as e:
            print(f"Analysis Error: {e}") 
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)