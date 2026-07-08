from django.db import models
import uuid
from django.db import models
from django.utils import timezone
from datetime import timedelta
from accounts.models import Customer
from products.models import Product
from offers.models import Offer

class RedemptionRecord(models.Model):
    STATUS_CHOICES = (
        ('generated', 'Generated'),
        ('scanned', 'Scanned'),
        ('invoice_created', 'Invoice Created'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('expired', 'Expired'),
    )
    customer = models.ForeignKey(Customer , on_delete = models.CASCADE , related_name="redemptions")
    product = models.ForeignKey(Product , on_delete=models.SET_NULL , null=True , blank=True)
    offer = models.ForeignKey(Offer, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20 ,choices=STATUS_CHOICES ,default="generated")
    points_used = models.PositiveIntegerField(default =0)
    invoice_number = models.CharField(max_length=50  , blank = True , null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    
    def __str__(self):
        return f"Redemption #{self.id} - {self.customer.name} - {self.status}"



class QRCode(models.Model):
    redemption_record = models.OneToOneField(RedemptionRecord , on_delete=models.CASCADE , related_name='qr_code')
    code = models.CharField(max_length=100  , unique=True  , default=uuid.uuid4)
    is_used = models.BooleanField(default=False)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def is_expire(self):
        return timezone.now() > self.expires_at
    
    def __str__(self):
        return f"QR for Redemption #{self.redemption_record.id}"
    
    