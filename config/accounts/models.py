from django.db import models

class Customer(models.Model):
    MEMBERSHIP_CHOICES = (
        ('silver', 'Silver'),
        ('silver_plus', 'Silver Plus'),
        ('gold', 'Gold'),
        ('platinum', 'Platinum'),
    )

    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)
    wallet_points = models.PositiveIntegerField(default=0)
    membership_level = models.CharField(max_length=20, choices=MEMBERSHIP_CHOICES, default='silver')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name