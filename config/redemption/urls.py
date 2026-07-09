from django.urls import path
from .views import RedeemProductView, RedeemOfferView, ScanQRView , RedemptionHistoryView

urlpatterns = [
    path('redeem/product/', RedeemProductView.as_view(), name='redeem-product'),
    path('redeem/offer/', RedeemOfferView.as_view(), name='redeem-offer'),
    path('redeem/scan/', ScanQRView.as_view(), name='redeem-scan'),
    path('redeem/history/<int:customer_id>/', RedemptionHistoryView.as_view(), name='redeem-history')
]