from datetime import date, timedelta

from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from offers.models import Offer
from partners.models import Partner


class PartnerOfferApiTests(APITestCase):
    def setUp(self):
        self.user_a = User.objects.create_user(username="partner-a", password="pass12345")
        self.user_b = User.objects.create_user(username="partner-b", password="pass12345")

        self.partner_a = Partner.objects.create(
            user=self.user_a,
            company_name="Partner A",
            contact_email="a@example.com",
        )
        self.partner_b = Partner.objects.create(
            user=self.user_b,
            company_name="Partner B",
            contact_email="b@example.com",
        )

        self.token_a = Token.objects.create(user=self.user_a)
        self.token_b = Token.objects.create(user=self.user_b)

        self.offer_a = Offer.objects.create(
            partner=self.partner_a,
            title="Offer A",
            category="Dining",
            start_date=date.today(),
            end_date=date.today() + timedelta(days=7),
            status="active",
            redemption_limit=2,
        )
        self.offer_b = Offer.objects.create(
            partner=self.partner_b,
            title="Offer B",
            category="Travel",
            start_date=date.today(),
            end_date=date.today() + timedelta(days=7),
            status="active",
            redemption_limit=1,
        )

    def auth(self, token):
        return {"HTTP_AUTHORIZATION": f"Token {token.key}"}

    def test_partner_list_only_returns_owned_offers(self):
        response = self.client.get("/api/partner/offers/", **self.auth(self.token_a))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], self.offer_a.id)

    def test_partner_cannot_access_another_partners_offer(self):
        response = self.client.get(
            f"/api/partner/offers/{self.offer_b.id}/",
            **self.auth(self.token_a),
        )

        self.assertEqual(response.status_code, 404)

    def test_partner_cannot_update_another_partners_offer(self):
        response = self.client.put(
            f"/api/partner/offers/{self.offer_b.id}/",
            {
                "title": "Hacked Title",
                "start_date": str(date.today()),
                "end_date": str(date.today() + timedelta(days=10)),
                "status": "inactive",
                "redemption_limit": 3,
            },
            format="json",
            **self.auth(self.token_a),
        )

        self.assertEqual(response.status_code, 404)
        self.offer_b.refresh_from_db()
        self.assertEqual(self.offer_b.title, "Offer B")

    def test_partner_cannot_delete_another_partners_offer(self):
        response = self.client.delete(
            f"/api/partner/offers/{self.offer_b.id}/",
            **self.auth(self.token_a),
        )

        self.assertEqual(response.status_code, 404)
        self.assertTrue(Offer.objects.filter(id=self.offer_b.id).exists())
