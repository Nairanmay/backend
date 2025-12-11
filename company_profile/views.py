from rest_framework import viewsets, permissions
from rest_framework.response import Response
from .models import CompanyProfile
from .serializers import CompanyProfileSerializer

class CompanyProfileViewSet(viewsets.ModelViewSet):
    serializer_class = CompanyProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'post', 'patch']

    def get_queryset(self):
        # Only return the profile for the user's company
        return CompanyProfile.objects.filter(company_code=self.request.user.company_code)

    def list(self, request, *args, **kwargs):
        # Override list to return a single object instead of an array
        queryset = self.get_queryset()
        if queryset.exists():
            serializer = self.get_serializer(queryset.first())
            return Response(serializer.data)
        return Response({})  # Return empty if no profile exists yet

    def create(self, request, *args, **kwargs):
        # Ensure admins can only create/update their own company profile
        if request.user.role != 'admin':
            return Response({"error": "Only admins can edit business details."}, status=403)

        # Check if profile exists, if so, update it instead of creating new
        profile, created = CompanyProfile.objects.update_or_create(
            company_code=request.user.company_code,
            defaults=request.data
        )
        serializer = self.get_serializer(profile)
        return Response(serializer.data)