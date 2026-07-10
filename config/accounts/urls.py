from django.urls import path
from .views import CustomerListCreateView, CustomerDetailView,SignupView , LoginView , AddWalletPointsView

urlpatterns = [
    path('customers/', CustomerListCreateView.as_view(), name='customer-list-create'),
    path('customers/<int:pk>/', CustomerDetailView.as_view(), name='customer-detail'),
    path('auth/signup/' , SignupView.as_view() , name='signup'),
    path('auth/login/' , LoginView.as_view() , name='login'),
    path('customers/<int:pk>/add-points/', AddWalletPointsView.as_view(), name='add-wallet-points'),

]