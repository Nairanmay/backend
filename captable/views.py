from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny # <-- Import AllowAny
from django.db.models import Sum
from .models import Stakeholder, Security, Issuance
from .serializers import StakeholderSerializer, SecuritySerializer, IssuanceSerializer
from users.permission import IsRoleAdmin

# --- ViewSets for managing raw cap table data (Still requires Admin Auth) ---

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


# --- Special view to calculate and serve the cap table (Now Public) ---

class CapTableSummaryView(APIView):
    """
    Provides a read-only, publicly accessible summary of the capitalization table.
    It requires a company_code to be passed in the URL.
    """
    # ✅ --- FIX: Changed permission to allow anyone to access this view ---
    permission_classes = [AllowAny]

    def get(self, request, company_code, *args, **kwargs):
        # ✅ --- FIX: The company_code now comes directly from the URL, not the logged-in user ---
        
        # 1. Calculate total outstanding shares for the given company
        total_shares = Issuance.objects.filter(company_code=company_code).aggregate(total=Sum('number_of_shares'))['total'] or 0
        if total_shares == 0:
            # It's better to return an empty state than a 404 if the company exists but has no shares
            return Response({"total_shares": 0, "holdings": [], "company_code": company_code})

        # 2. Aggregate shares held by each stakeholder
        summary = Issuance.objects.filter(company_code=company_code) \
                                .values('stakeholder__name', 'stakeholder__stakeholder_type') \
                                .annotate(shares_held=Sum('number_of_shares')) \
                                .order_by('-shares_held')

        # 3. Calculate ownership percentage and format the response
        holdings_data = []
        for item in summary:
            percentage = (item['shares_held'] / total_shares) * 100
            holdings_data.append({
                'stakeholder_name': item['stakeholder__name'],
                'stakeholder_type': item['stakeholder__stakeholder_type'],
                'shares_held': item['shares_held'],
                'ownership_percentage': round(percentage, 4)
            })
        
        response_data = {
            "company_code": company_code,
            "total_shares": total_shares,
            "holdings": holdings_data
        }
        
        return Response(response_data)

