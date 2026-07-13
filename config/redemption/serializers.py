from rest_framework import serializers
from .models import RedemptionRecord, QRCode


class QRCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = QRCode
        fields = '__all__'


class RedemptionRecordSerializer(serializers.ModelSerializer):
    qr_code = QRCodeSerializer(read_only=True)
    product_name = serializers.CharField(source = 'product.name' , read_only = True , default = None)
    offer_name = serializers.CharField(source ='offer.html' , read_only = True ,default = None)

    class Meta:
        model = RedemptionRecord
        fields = '__all__'