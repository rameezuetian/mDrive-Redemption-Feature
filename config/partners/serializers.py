from rest_framework import serializers

from offers.models import Offer


class PartnerOfferSerializer(serializers.ModelSerializer):
    partner_id = serializers.IntegerField(source="partner.id", read_only=True)

    class Meta:
        model = Offer
        fields = [
            "id",
            "partner_id",
            "title",
            "banner",
            "description",
            "category",
            "start_date",
            "end_date",
            "status",
            "terms_and_conditions",
            "redemption_instructions",
            "membership_eligibility",
            "redemption_limit",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "partner_id", "created_at", "updated_at"]
