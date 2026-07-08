from django.urls import path
from .views import RedeemProductView , ScanQRView


urlpatterns = [
    path('redeem/product/' , RedeemProductView.as_view() , name='redeem-product'),
    path('scan/product/' , ScanQRView.as_view() , name='redeem-scan')
    
]