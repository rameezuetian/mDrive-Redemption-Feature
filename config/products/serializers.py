from rest_framework import serializers
from .models import Product , ProductTierPricing



class ProductTierPricingSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductTierPricing
        fields = ['membership_level' , 'points_required']




class ProductSerializer(serializers.ModelSerializer):
    tier_pricing = ProductTierPricingSerializer(many = True , read_only = True)
    class Meta:
        model = Product
        fields = '__all__'