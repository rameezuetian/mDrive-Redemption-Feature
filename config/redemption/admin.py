from django.contrib import admin
from .models import RedemptionRecord , QRCode
# Register your models here.
admin.site.register(RedemptionRecord)
admin.site.register(QRCode)