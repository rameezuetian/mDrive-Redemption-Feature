from django.urls import path
from .views import RedemptionByCustomerView , ReportSummaryView

urlpatterns = [
    path('reports/summary/', ReportSummaryView.as_view() , name='reports-summary'),
    path('reports/by-customer/', RedemptionByCustomerView.as_view() , name='reports-by-customer')
]