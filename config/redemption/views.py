from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from accounts.models import Customer
from products.models import Product
from offers.models import Offer
from .models import RedemptionRecord
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

    def post(self, request):
        customer_id = request.data.get('customer_id')
        product_id = request.data.get('product_id')

        customer = get_object_or_404(Customer, pk=customer_id)
        product = get_object_or_404(Product, pk=product_id)

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
            points_used=product.points_required,
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

    def post(self, request):
        customer_id = request.data.get('customer_id')
        offer_id = request.data.get('offer_id')

        customer = get_object_or_404(Customer, pk=customer_id)
        offer = get_object_or_404(Offer, pk=offer_id)

        # Step 1: check offer is valid (active + within date range)
        is_valid, error = check_offer_validity(offer)
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