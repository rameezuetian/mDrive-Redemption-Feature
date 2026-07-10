from django.db import models
from django.contrib.auth.hashers import make_password, check_password


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
    password = models.CharField(max_length=255, default='')
    wallet_points = models.PositiveIntegerField(default=0)
    membership_level = models.CharField(max_length=20, choices=MEMBERSHIP_CHOICES, default='silver')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)   # <- calls the imported function, not itself

    def __str__(self):
        return self.name