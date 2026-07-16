from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Partner(models.Model):
    user = models.OneToOneField(User , on_delete=models.CASCADE , related_name='partner_profile')
    company_name = models.CharField(max_length=255)
    contact_email = models.EmailField()
    contact_phone =  models.CharField(max_length=20 , blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.company_name