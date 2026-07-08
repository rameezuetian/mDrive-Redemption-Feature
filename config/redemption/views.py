from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from accounts.models import Customer
from products.models import Product
from .models import RedemptionRecord
from .serializers import RedemptionRecordSerializer
from .services import (
    mock_wallet_check, generate_qr_for_redemption, mock_create_invoice,mock_deduct_points,validate_qr_code
)


class RedeemProductView(APIView):
    """
    POST /api/redeem/product/
    Body: { "customer_id": 1, "product_id": 2 }
    """
    def post(self , request):
        customer_id = request.data.get('customer_id')
        product_id = request.data.get('product_id')
        
        customer = get_object_or_404(Customer , pk = customer_id)  
        product = get_object_or_404(Product , pk=product_id)
        
        
        # Check the balance 
        if not mock_wallet_check(customer , product.points_required):
            return Response(
                {
                    "error":"Insufficient wallet points"
                },
                 status=status.HTTP_400_BAD_REQUEST
            )      
            
        # check the product avalability
        if product.available_quantity <=0:
            return Response(
                {"error":"Product out of stock"},
                status = status.HTTP_400_BAD_REQUEST
            )
            
        # create redemption record
        redemption = RedemptionRecord.objects.create(
            customer= customer,
            product = product,
            points_used = product.points_required,
            status = 'generated',
        )
        
        
        # generate qr
        generate_qr_for_redemption(redemption)
        
        
        serializer = RedemptionRecordSerializer(redemption)
        
        return Response(serializer.data , status=status.HTTP_201_CREATED)
    
    
    
    
class ScanQRView(APIView):
    """
    POST /api/redeem/scan/
    """
    def post(self , request):
        code = request.data.get('code')
        
        if not code:
            return Response(
                {"error":"QR code is required"},
                status= status.HTTP_400_BAD_REQUEST
            )
        
        #  step 1 validate the qr
        qr , error = validate_qr_code(code)
        
        if error: # type: ignore
            return Response({"error":error}, status=status.HTTP_400_BAD_REQUEST)
        
        redemption = qr.redemption_record
        customer = redemption.customer
        
        #  check qr code is scan
        qr.is_used = True
        qr.save()
        redemption.status = "scanned"
        redemption.save()
        
        #  deduct the wallet points
        mock_deduct_points(customer,redemption.points_used)
        
        
        #  reduce the redemption quantity
        if redemption.product:
            redemption.product.available_quantity -=1
            redemption.product.save()
            
        # generate the invoice :
        mock_create_invoice(redemption)
        redemption.status = "invoice_created"
        redemption.save()
        
        
        # 
        redemption.status = "completed"
        redemption.save()
        
        serializer = RedemptionRecordSerializer(redemption)
        return Response(serializer.data , status=status.HTTP_200_OK)