from datetime import date, timedelta

from django.contrib.auth.models import User
from rest_framework.test import APITestCase

from offers.models import Offer
from partners.models import Partner


class OfferListViewTests(APITestCase):
    def setUp(self):
        partner_user = User.objects.create_user(username="partner-public", password="pass12345")
        self.partner = Partner.objects.create(
            user=partner_user,
            company_name="Partner Public",
            contact_email="public@example.com",
        )

        self.future_partner_offer = Offer.objects.create(
            partner=self.partner,
            title="Upcoming Partner Offer",
            category="Dining",
            start_date=date.today() + timedelta(days=3),
            end_date=date.today() + timedelta(days=10),
            status="active",
            redemption_limit=1,
        )
        self.expired_offer = Offer.objects.create(
            title="Expired Offer",
            category="Travel",
            start_date=date.today() - timedelta(days=10),
            end_date=date.today() - timedelta(days=1),
            status="expired",
            redemption_limit=1,
        )
        self.inactive_offer = Offer.objects.create(
            title="Inactive Offer",
            category="Retail",
            start_date=date.today(),
            end_date=date.today() + timedelta(days=5),
            status="inactive",
            redemption_limit=1,
        )

    def test_customer_offers_include_upcoming_active_partner_offers(self):
        response = self.client.get("/api/offers/?status=activated")

        self.assertEqual(response.status_code, 200)
        offer_ids = {offer["id"] for offer in response.data}
        self.assertIn(self.future_partner_offer.id, offer_ids)
        self.assertNotIn(self.expired_offer.id, offer_ids)
        self.assertNotIn(self.inactive_offer.id, offer_ids)
