from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum
from .models import Stakeholder, Security, Issuance
from .serializers import StakeholderSerializer, SecuritySerializer, IssuanceSerializer

# --- ViewSets for managing raw cap table data ---

class StakeholderViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = StakeholderSerializer
    def get_queryset(self):
        # Users can only see stakeholders in their own company
        return Stakeholder.objects.filter(company_code=self.request.user.company_code)

class SecurityViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = SecuritySerializer
    def get_queryset(self):
        return Security.objects.filter(company_code=self.request.user.company_code)

class IssuanceViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = IssuanceSerializer
    def get_queryset(self):
        return Issuance.objects.filter(company_code=self.request.user.company_code)


# --- Special view to calculate and serve the cap table ---

class CapTableSummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        if user.role != 'admin':
            return Response({"error": "Only admins can view the cap table."}, status=status.HTTP_403_FORBIDDEN)

        company_code = user.company_code
        
        # 1. Calculate total shares
        total_shares = Issuance.objects.filter(company_code=company_code).aggregate(total=Sum('number_of_shares'))['total'] or 0
        if total_shares == 0:
            return Response({"total_shares": 0, "holdings": []})

        # 2. Aggregate shares by stakeholder
        summary = Issuance.objects.filter(company_code=company_code) \
                                .values('stakeholder__name', 'stakeholder__stakeholder_type') \
                                .annotate(shares_held=Sum('number_of_shares')) \
                                .order_by('-shares_held')

        # 3. Calculate ownership percentage for each and format the response
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
            "total_shares": total_shares,
            "holdings": holdings_data
        }
        
        return Response(response_data)
