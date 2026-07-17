from django.urls import path
from .views import (
    CreatePartnerView,
    PartnerListView,
    PartnerLoginView,
    MyOffersView,
    MyOfferRedemptionView
    
    )


urlpatterns = [
    path('partners/login/' , PartnerLoginView.as_view() , name='partner-login'),
    path('partners/create/' , CreatePartnerView.as_view() , name='partner-create'),
    path('partners/' , PartnerListView.as_view() , name='partner-list'),
    path('partners/my-offers/' , MyOffersView.as_view() , name='partner-my-offers'),
    path('partners/my-offers/<int:offer_id>/redemptions/' , MyOfferRedemptionView.as_view() , name='parnter-offer-redemptions'),
]
