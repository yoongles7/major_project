from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from trading.models import Portfolio

User = get_user_model()

@receiver(post_save, sender=User)
def create_user_portfolio(sender, instance, created, **kwargs):
    """
    When a new user is created, automatically create their portfolio
    """
    if created:
        Portfolio.objects.create(
            user=instance,
            cash_balance=100000.00  # Start with Rs. 100,000
        )
        print(f"✓ Created portfolio for {instance.email}")  # Debug message