from rest_framework.routers import DefaultRouter
# from .views import ProductViewSet,
from .views import ProductListCreateView ,ProductDetailView
from django.urls import path



urlpatterns = [
    path('products/' , ProductListCreateView.as_view(), name = 'product-list-create'),
    path('products/<int:pk>/' , ProductDetailView.as_view() ,name='product-detail')
]











# router = DefaultRouter()

# router.register('products' , ProductViewSet)

# urlpatterns = router.urls