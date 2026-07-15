"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from accounts.views import (
    signup_page , 
    login_page  ,
     product_page ,
     qr_page , 
     offers_pages ,
     history_page,
     admin_login_page,
     admin_summary_page,
     outlet_scan_page,
     manage_offers_page,
     manage_products_page,
     product_detail_page
)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/' , include('products.urls')),
    path('api/' , include('offers.urls')),
    path('api/' , include('accounts.urls')),
    path('api/' , include('redemption.urls')),
    path('api/' , include('reports.urls')),
    path('signup/' ,signup_page , name='signup-page'),
    path('login/' , login_page , name='login-page'),
    path('products/' , product_page , name='product-page'),
    path('qr/' , qr_page , name='qr-page'),
    path('offers/', offers_pages , name='offers-page'),
    path('history/' , history_page , name='history-page'),
    path('admin-login' , admin_login_page , name='admin-login-page'),
    path('admin-summary' , admin_summary_page , name='admin-summary-page'),
    path('outlet-scan' , outlet_scan_page , name='outlet-scan-page'),
    path('manage-products/' , manage_products_page , name='manage-products-page'),
    path('manage-offers/' ,manage_offers_page , name='manage-offers-page'),
    path('products/<int:pk>/', product_detail_page, name='product-detail-page'),

    
]

urlpatterns +=static(settings.MEDIA_URL ,document_root =settings.MEDIA_ROOT)
