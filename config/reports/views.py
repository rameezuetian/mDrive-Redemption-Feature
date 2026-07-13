from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Sum , Count
from redemption.models import RedemptionRecord 
from core.permissions import IsAdminUser
from rest_framework.authentication import TokenAuthentication
# Create your views here.


class ReportSummaryView(APIView):
    """
    GET /api/reports/summary/
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdminUser]
    def get(self , request):
        total_product_redemptions = RedemptionRecord.objects.filter(
            product__isnull = False , status = "completed"
        ).count()
        total_offer_redemptions = RedemptionRecord.objects.filter(
            offer__isnull = False  , status = "completed"
        ).count()
        total_points_used = RedemptionRecord.objects.filter(
            status= "completed"
        ).aggregate(total_sum=Sum("points_used"))['total_sum'] or 0
        
        total_redemptions = RedemptionRecord.objects.filter(status='completed').count()
        
        data = {
            "total_product_redemptions":total_product_redemptions,
            "total_offer_redemptions": total_offer_redemptions,
            "total_redemptions" :total_redemptions,
            "total_wallet_points_used" : total_points_used,
        }
        return Response(data)
    

class RedemptionByCustomerView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdminUser]
    """
    GET /api/reports/by-customer/
    """
    def get(self , request , ):
        data = (
            RedemptionRecord.objects.filter(status='completed')
            .values('customer__id' , 'customer__name')
            .annotate(total_redemptions = Count('id'))
            .order_by('-total_redemptions')
        )
        return Response(list(data))