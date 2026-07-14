from django.contrib import admin
from .models import Product , ProductTierPricing

# Register your models here.

class ProductTierPricingInline(admin.TabularInline):
    model = ProductTierPricing
    extra = 4
    
    
class  ProductAdmin(admin.ModelAdmin):
    inlines = [ProductTierPricingInline]


admin.site.register(Product , ProductAdmin)
