from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum
from .models import Stakeholder, Security, Issuance
from .serializers import StakeholderSerializer, SecuritySerializer, IssuanceSerializer
from users.permission import IsRoleAdmin

# --- ViewSets for managing raw cap table data (Admins only) ---

class BaseCompanyViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsRoleAdmin]
    def get_queryset(self):
        user_company_code = self.request.user.company_code
        return self.queryset.filter(company_code=user_company_code)
    def perform_create(self, serializer):
        serializer.save(company_code=self.request.user.company_code)

class StakeholderViewSet(BaseCompanyViewSet):
    queryset = Stakeholder.objects.all()
    serializer_class = StakeholderSerializer

class SecurityViewSet(BaseCompanyViewSet):
    queryset = Security.objects.all()
    serializer_class = SecuritySerializer

class IssuanceViewSet(BaseCompanyViewSet):
    queryset = Issuance.objects.all()
    serializer_class = IssuanceSerializer

# --- View to calculate and serve the cap table summary ---

class CapTableSummaryView(APIView):
    """Provides a read-only, calculated summary for the logged-in admin's company."""
    permission_classes = [IsAuthenticated, IsRoleAdmin]

    def get(self, request, *args, **kwargs):
        # ✅ --- FIX: Get company_code from the authenticated user, not the URL ---
        company_code = request.user.company_code
        if not company_code:
            return Response({"error": "Admin user is not associated with a company."}, status=status.HTTP_400_BAD_REQUEST)

        total_shares = Issuance.objects.filter(company_code=company_code).aggregate(total=Sum('number_of_shares'))['total'] or 0
        if total_shares == 0:
            return Response({"total_shares": 0, "holdings": []})

        summary = Issuance.objects.filter(company_code=company_code) \
                                .values('stakeholder__name', 'stakeholder__stakeholder_type') \
                                .annotate(shares_held=Sum('number_of_shares')) \
                                .order_by('-shares_held')

        holdings_data = []
        for item in summary:
            percentage = (item['shares_held'] / total_shares) * 100
            holdings_data.append({
                'stakeholder_name': item['stakeholder__name'],
                'stakeholder_type': item['stakeholder__stakeholder_type'],
                'shares_held': item['shares_held'],
                'ownership_percentage': round(percentage, 4)
            })
        
        response_data = {"total_shares": total_shares, "holdings": holdings_data}
        return Response(response_data)

from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum
from .models import Stakeholder, Security, Issuance
from .serializers import StakeholderSerializer, SecuritySerializer, IssuanceSerializer
from users.permission import IsRoleAdmin

# --- ViewSets for managing raw cap table data (Admins only) ---

class BaseCompanyViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsRoleAdmin]
    def get_queryset(self):
        user_company_code = self.request.user.company_code
        return self.queryset.filter(company_code=user_company_code)
    def perform_create(self, serializer):
        serializer.save(company_code=self.request.user.company_code)

class StakeholderViewSet(BaseCompanyViewSet):
    queryset = Stakeholder.objects.all()
    serializer_class = StakeholderSerializer

class SecurityViewSet(BaseCompanyViewSet):
    queryset = Security.objects.all()
    serializer_class = SecuritySerializer

class IssuanceViewSet(BaseCompanyViewSet):
    queryset = Issuance.objects.all()
    serializer_class = IssuanceSerializer

# --- View to calculate and serve the cap table summary ---

class CapTableSummaryView(APIView):
    """Provides a read-only, calculated summary for the logged-in admin's company."""
    permission_classes = [IsAuthenticated, IsRoleAdmin]

    def get(self, request, *args, **kwargs):
        # ✅ --- FIX: Get company_code from the authenticated user, not the URL ---
        company_code = request.user.company_code
        if not company_code:
            return Response({"error": "Admin user is not associated with a company."}, status=status.HTTP_400_BAD_REQUEST)

        total_shares = Issuance.objects.filter(company_code=company_code).aggregate(total=Sum('number_of_shares'))['total'] or 0
        if total_shares == 0:
            return Response({"total_shares": 0, "holdings": []})

        summary = Issuance.objects.filter(company_code=company_code) \
                                .values('stakeholder__name', 'stakeholder__stakeholder_type') \
                                .annotate(shares_held=Sum('number_of_shares')) \
                                .order_by('-shares_held')

        holdings_data = []
        for item in summary:
            percentage = (item['shares_held'] / total_shares) * 100
            holdings_data.append({
                'stakeholder_name': item['stakeholder__name'],
                'stakeholder_type': item['stakeholder__stakeholder_type'],
                'shares_held': item['shares_held'],
                'ownership_percentage': round(percentage, 4)
            })
        
        response_data = {"total_shares": total_shares, "holdings": holdings_data}
        return Response(response_data)

