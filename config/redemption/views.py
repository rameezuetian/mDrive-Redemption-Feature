from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from accounts.models import Customer
from products.models import Product
from offers.models import Offer
from .models import RedemptionRecord
from django.utils import timezone
from core.permissions import IsSuperAdminUser ,IsStaffAdminOrPartner
from rest_framework.authentication import TokenAuthentication
from core.authentication import CsrfExemptSessionAuthentication
from .serializers import RedemptionRecordSerializer
from .services import (
    mock_wallet_check,
    generate_qr_for_redemption,
    validate_qr_code,
    mock_create_invoice,
    mock_deduct_points,
    check_membership_redemption_limit,
    check_offer_validity,
    MEMBERSHIP_LIMITS,
)


class RedeemProductView(APIView):
    """
    POST /api/redeem/product/
    Body: { "customer_id": 1, "product_id": 2 }
    """
    authentication_classes = [CsrfExemptSessionAuthentication]
    permission_classes = []
    def post(self, request):
        customer_id = request.data.get('customer_id')
        product_id = request.data.get('product_id')

        customer = get_object_or_404(Customer, pk=customer_id)
        product = get_object_or_404(Product, pk=product_id)
        
        price = product.get_price_for_tier(customer.membership_level)

        if not mock_wallet_check(customer, product.points_required):
            return Response(
                {"error": "Insufficient wallet points"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if product.available_quantity <= 0:
            return Response(
                {"error": "Product out of stock"},
                status=status.HTTP_400_BAD_REQUEST
            )

        redemption = RedemptionRecord.objects.create(
            customer=customer,
            product=product,
            points_used=price,
            status='generated'
        )

        generate_qr_for_redemption(redemption)

        serializer = RedemptionRecordSerializer(redemption)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class RedeemOfferView(APIView):
    """
    POST /api/redeem/offer/
    Body: { "customer_id": 1, "offer_id": 2 }
    """
    authentication_classes = [CsrfExemptSessionAuthentication]
    permission_classes = []
    def post(self, request):
        customer_id = request.data.get('customer_id')
        offer_id = request.data.get('offer_id')

        customer = get_object_or_404(Customer, pk=customer_id)
        offer = get_object_or_404(Offer, pk=offer_id)

        # Step 1: check offer is valid (active + within date range)
        is_valid, error = check_offer_validity(offer , customer)
        if not is_valid:
            return Response({"error": error}, status=status.HTTP_400_BAD_REQUEST)

        # Step 2: check membership + offer redemption limit
        if not check_membership_redemption_limit(customer, offer):
            tier_limit = MEMBERSHIP_LIMITS.get(customer.membership_level, 1)
            if offer.redemption_limit < tier_limit:
                message = f"This offer can only be redeemed {offer.redemption_limit} time(s)"
            else:
                message = f"Your membership level allows only {tier_limit} redemption(s) for this offer"
            return Response({"error": message}, status=status.HTTP_400_BAD_REQUEST)

        # Step 3: create redemption record
        redemption = RedemptionRecord.objects.create(
            customer=customer,
            offer=offer,
            points_used=0,
            status='generated'
        )

        # Step 4: generate QR code
        generate_qr_for_redemption(redemption)

        serializer = RedemptionRecordSerializer(redemption)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ScanQRView(APIView):
    """
    POST /api/redeem/scan/
    Body: { "code": "the-qr-code-uuid" }
    """
    authentication_classes = [TokenAuthentication, CsrfExemptSessionAuthentication]
    permission_classes = [IsStaffAdminOrPartner]
    def post(self, request):
        code = request.data.get('code')

        if not code:
            return Response(
                {"error": "QR code is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        qr, error = validate_qr_code(code)
        if error:
            return Response({"error": error}, status=status.HTTP_400_BAD_REQUEST)

        redemption = qr.redemption_record
        if hasattr(request.user , 'partner_profile'):
            partner = request.user.partner_profile
            if not redemption.offer or redemption.offer.partner_id != partner.id:
                return Response(
                    {"error":"You can only scan redemption for their own offers"},
                    status=status.HTTP_403_FORBIDDEN    
                )
        
        customer = redemption.customer

        qr.is_used = True
        qr.save()
        redemption.status = 'scanned'
        redemption.save()

        mock_deduct_points(customer, redemption.points_used)

        if redemption.product:
            redemption.product.available_quantity -= 1
            redemption.product.save()

        mock_create_invoice(redemption)
        redemption.status = 'invoice_created'
        redemption.save()

        redemption.status = 'completed'
        redemption.save()

        serializer = RedemptionRecordSerializer(redemption)
        return Response(serializer.data, status=status.HTTP_200_OK)

     
    
class RedemptionHistoryView(APIView):
    def get(self , request , customer_id):
        customer = get_object_or_404(Customer , pk = customer_id)
        records = RedemptionRecord.objects.filter(customer=customer).order_by('-created_at')
        serializer = RedemptionRecordSerializer(records , many=True)
        return Response(serializer.data)
    

class ActiveRedemptionStatusView(APIView):
    def get(self, request):
        customer_id = request.query_params.get('customer_id')
        product_id = request.query_params.get('product_id')
        offer_id = request.query_params.get('offer_id')

        if not customer_id or (not product_id and not offer_id):
            return Response(
                {"error": "customer_id and either product_id or offer_id are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        filters = {'customer_id': customer_id, 'status': 'generated'}   # <- renamed
        if product_id:
            filters['product_id'] = product_id                          # <- renamed
        else:
            filters['offer_id'] = offer_id                               # <- renamed

        redemption = RedemptionRecord.objects.filter(**filters).order_by('-created_at').first()   # <- renamed

        if not redemption or not hasattr(redemption, 'qr_code'):
            return Response({"active": False})

        qr = redemption.qr_code

        if qr.is_used or qr.is_expire():
            return Response({"active": False})

        remaining_seconds = int((qr.expires_at - timezone.now()).total_seconds())
        remaining_seconds = max(remaining_seconds, 0)

        return Response({
            "active": True,
            "redemption_id": redemption.id,
            "code": qr.code,
            "expires_at": qr.expires_at,
            "remaining_seconds": remaining_seconds
        })
        
        

class ActivationCountView(APIView):
    """
    GET /api/redeem/activation-count/?customer_id=1&product_id=2
    GET /api/redeem/activation-count/?customer_id=1&offer_id=3

    Returns how many times this customer has completed activation
    for this specific product/offer.
    """
    def get(self, request):
        customer_id = request.query_params.get('customer_id')
        product_id = request.query_params.get('product_id')
        offer_id = request.query_params.get('offer_id')

        if not customer_id or (not product_id and not offer_id):
            return Response(
                {"error": "customer_id and either product_id or offer_id are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        filters = {
            'customer_id': customer_id,
            'status__in': ['completed', 'scanned', 'invoice_created']
        }
        if product_id:
            filters['product_id'] = product_id
        else:
            filters['offer_id'] = offer_id

        count = RedemptionRecord.objects.filter(**filters).count()

        return Response({"activation_count": count})