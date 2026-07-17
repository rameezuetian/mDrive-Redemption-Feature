from rest_framework import serializers
from .models import Offer

class OfferSerializer(serializers.ModelSerializer):
    partner_name = serializers.CharField(source = 'partner.company_name' , read_only = True , default = None)
    class Meta:
        model = Offer
        fields = '__all__'