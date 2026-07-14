from django.db import models

class Product(models.Model):
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    )

    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    short_description = models.CharField(max_length=255 , blank=True)
    description = models.TextField(blank=True)
    points_required = models.PositiveIntegerField()
    available_quantity = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    category = models.CharField(max_length=100, blank=True)
    terms_and_conditions = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def get_price_for_tier(self , membership_level):
        """
        Returns the tier-specific price if one exists, otherwise falls back
        to the product's base points_required.
        """
        tier_price = self.tier_pricing.filter(membership_level = membership_level).first()
        if tier_price:
            return tier_price.points_required
        return self.points_required


    def __str__(self):
        return self.name
    
    
    
class ProductTierPricing(models.Model):
    MEMBERSHIP_CHOICES = (
        ('silver', 'Silver'),
        ('silver_plus', 'Silver Plus'),
        ('gold', 'Gold'),
        ('platinum', 'Platinum'),
    )
    product = models.ForeignKey(Product , related_name='tier_pricing' , on_delete=models.CASCADE)
    membership_level = models.CharField(max_length=20 , choices=MEMBERSHIP_CHOICES)
    poinst_required = models.PositiveIntegerField()
    
    class Meta:
        unique_together  = ('product'  , 'membership_level')
        
    def __str__(self):
        return f"{self.name} - {self.membership_level}: {self.poinst_required} pts"
    