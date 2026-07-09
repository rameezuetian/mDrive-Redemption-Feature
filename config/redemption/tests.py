from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from rest_framework.test import APIClient
from rest_framework import status

from accounts.models import Customer
from products.models import Product
from offers.models import Offer
from redemption.models import RedemptionRecord, QRCode


class RedeemProductTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.customer = Customer.objects.create(
            name="Test User",
            email="test@example.com",
            wallet_points=200,
            membership_level="silver"
        )
        self.product = Product.objects.create(
            name="Test Product",
            points_required=100,
            available_quantity=5,
            status="active"
        )

    def test_successful_redeem_generates_qr(self):
        response = self.client.post('/api/redeem/product/', {
            "customer_id": self.customer.id,
            "product_id": self.product.id
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('qr_code', response.data)
        self.assertEqual(response.data['status'], 'generated')

    def test_insufficient_points_blocked(self):
        poor_customer = Customer.objects.create(
            name="Poor User",
            email="poor@example.com",
            wallet_points=10,
            membership_level="silver"
        )
        response = self.client.post('/api/redeem/product/', {
            "customer_id": poor_customer.id,
            "product_id": self.product.id
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Insufficient', response.data['error'])

    def test_out_of_stock_blocked(self):
        out_of_stock_product = Product.objects.create(
            name="Out of Stock Product",
            points_required=50,
            available_quantity=0,
            status="active"
        )
        response = self.client.post('/api/redeem/product/', {
            "customer_id": self.customer.id,
            "product_id": out_of_stock_product.id
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('stock', response.data['error'].lower())


class ScanQRTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.customer = Customer.objects.create(
            name="Scan Test User",
            email="scan@example.com",
            wallet_points=500,
            membership_level="gold"
        )
        self.product = Product.objects.create(
            name="Scan Test Product",
            points_required=100,
            available_quantity=5,
            status="active"
        )
        # Create a redemption + QR directly
        self.redemption = RedemptionRecord.objects.create(
            customer=self.customer,
            product=self.product,
            points_used=100,
            status='generated'
        )
        self.qr = QRCode.objects.create(
            redemption_record=self.redemption,
            expires_at=timezone.now() + timedelta(minutes=60)
        )

    def test_successful_scan_completes_redemption(self):
        response = self.client.post('/api/redeem/scan/', {"code": str(self.qr.code)})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'completed')
        self.assertIsNotNone(response.data['invoice_number'])

    def test_duplicate_scan_blocked(self):
        # First scan succeeds
        self.client.post('/api/redeem/scan/', {"code": str(self.qr.code)})
        # Second scan should fail
        response = self.client.post('/api/redeem/scan/', {"code": str(self.qr.code)})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('already used', response.data['error'])

    def test_expired_qr_blocked(self):
        expired_qr = QRCode.objects.create(
            redemption_record=RedemptionRecord.objects.create(
                customer=self.customer,
                product=self.product,
                points_used=100,
                status='generated'
            ),
            expires_at=timezone.now() - timedelta(minutes=10)  # already expired
        )
        response = self.client.post('/api/redeem/scan/', {"code": str(expired_qr.code)})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('expired', response.data['error'].lower())

    def test_invalid_qr_blocked(self):
        response = self.client.post('/api/redeem/scan/', {"code": "00000000-0000-0000-0000-000000000000"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Invalid', response.data['error'])

    def test_wallet_points_deducted_on_scan(self):
        original_points = self.customer.wallet_points
        self.client.post('/api/redeem/scan/', {"code": str(self.qr.code)})
        self.customer.refresh_from_db()
        self.assertEqual(self.customer.wallet_points, original_points - 100)

    def test_product_stock_reduced_on_scan(self):
        original_qty = self.product.available_quantity
        self.client.post('/api/redeem/scan/', {"code": str(self.qr.code)})
        self.product.refresh_from_db()
        self.assertEqual(self.product.available_quantity, original_qty - 1)


class RedeemOfferTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.customer = Customer.objects.create(
            name="Offer Test User",
            email="offer@example.com",
            wallet_points=1000,
            membership_level="silver"
        )
        today = timezone.now().date()
        self.active_offer = Offer.objects.create(
            title="Active Offer",
            category="Test",
            start_date=today - timedelta(days=5),
            end_date=today + timedelta(days=5),
            status="active",
            redemption_limit=1
        )
        self.expired_offer = Offer.objects.create(
            title="Expired Offer",
            category="Test",
            start_date=today - timedelta(days=30),
            end_date=today - timedelta(days=10),
            status="active",
            redemption_limit=1
        )
        self.inactive_offer = Offer.objects.create(
            title="Inactive Offer",
            category="Test",
            start_date=today - timedelta(days=5),
            end_date=today + timedelta(days=5),
            status="inactive",
            redemption_limit=1
        )

    def test_active_offer_redeems_successfully(self):
        response = self.client.post('/api/redeem/offer/', {
            "customer_id": self.customer.id,
            "offer_id": self.active_offer.id
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_expired_offer_blocked(self):
        response = self.client.post('/api/redeem/offer/', {
            "customer_id": self.customer.id,
            "offer_id": self.expired_offer.id
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_inactive_offer_blocked(self):
        response = self.client.post('/api/redeem/offer/', {
            "customer_id": self.customer.id,
            "offer_id": self.inactive_offer.id
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Active', response.data['error'])

    def test_redemption_limit_enforced(self):
        # First redeem + scan should succeed
        redeem_response = self.client.post('/api/redeem/offer/', {
            "customer_id": self.customer.id,
            "offer_id": self.active_offer.id
        })
        qr_code = redeem_response.data['qr_code']['code']
        self.client.post('/api/redeem/scan/', {"code": qr_code})

        # Second attempt should be blocked (limit = 1)
        second_response = self.client.post('/api/redeem/offer/', {
            "customer_id": self.customer.id,
            "offer_id": self.active_offer.id
        })
        self.assertEqual(second_response.status_code, status.HTTP_400_BAD_REQUEST)