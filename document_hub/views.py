from rest_framework import viewsets, permissions
from .models import Document
from .serializers import DocumentSerializer

class DocumentViewSet(viewsets.ModelViewSet):
    serializer_class = DocumentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if not user.company_code:
            return Document.objects.none()
        
        # Filter by the logged-in user's company code
        queryset = Document.objects.filter(company_code=user.company_code).order_by('-uploaded_at')
        
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(title__icontains=search)
            
        return queryset

    def perform_create(self, serializer):
        serializer.save(
            uploaded_by=self.request.user,
            company_code=self.request.user.company_code
        )