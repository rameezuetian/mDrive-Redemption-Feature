from django.db import models
from partners.models import Partner
class Offer(models.Model):
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('expired', 'Expired'),
    )
    partner = models.ForeignKey(Partner , null = True , blank=True , related_name='offers' , on_delete=models.SET_NULL)
    title = models.CharField(max_length=255)
    banner = models.ImageField(upload_to='offers/', blank=True, null=True)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=100, blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    terms_and_conditions = models.TextField(blank=True)
    redemption_instructions = models.TextField(blank=True)
    membership_eligibility = models.CharField(max_length=100, blank=True)
    redemption_limit = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title