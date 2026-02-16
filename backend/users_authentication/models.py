from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    virtual_balance = models.DecimalField(max_digits=12, decimal_places=2, default=100000)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def get_or_create_portfolio(self):
        """Helper method to ensure portfolio exists"""
        from trading.models import Portfolio
        portfolio, created = Portfolio.objects.get_or_create(
            user=self,
            defaults={'cash_balance': 100000.00}
        )
        if created:
            print(f"Portfolio created for {self.email}")
        return portfolio