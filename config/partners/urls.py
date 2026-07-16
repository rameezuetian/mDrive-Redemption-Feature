from django.urls import path
from .views import (
    CreatePartnerView,
    PartnerListView,
    PartnerLoginView,
    PartnerOfferDetailView,
    PartnerOfferListCreateView,
    PartnerOfferRedemptionBreakdownView,
    PartnerOfferStatusBreakdownView,
    PartnerReportSummaryView,
)


urlpatterns = [
    path('partners/login/' , PartnerLoginView.as_view() , name='partner-login'),
    path('partners/create/' , CreatePartnerView.as_view() , name='partner-create'),
    path('partners/' , PartnerListView.as_view() , name='partner-list'),
    path('partner/offers/', PartnerOfferListCreateView.as_view(), name='partner-offer-list-create'),
    path('partner/offers/<int:pk>/', PartnerOfferDetailView.as_view(), name='partner-offer-detail'),
    path('partner/reports/summary/', PartnerReportSummaryView.as_view(), name='partner-report-summary'),
    path('partner/reports/status-breakdown/', PartnerOfferStatusBreakdownView.as_view(), name='partner-report-status-breakdown'),
    path('partner/reports/redemption-breakdown/', PartnerOfferRedemptionBreakdownView.as_view(), name='partner-report-redemption-breakdown'),
]
