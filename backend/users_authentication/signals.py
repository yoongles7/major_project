from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import CustomUser
from trading.models import Portfolio

@receiver(post_save, sender=CustomUser)
def create_user_portfolio(sender, instance, created, **kwargs):
    """Create a portfolio whenever a new user is created"""
    if created:
        Portfolio.objects.create(
            user=instance,
            cash_balance=100000.00  # Default starting money
        )
        print(f"Portfolio created for user: {instance.email}")

@receiver(post_save, sender=CustomUser)
def save_user_portfolio(sender, instance, **kwargs):
    """This runs on every save, but portfolio already exists"""
    # If for some reason portfolio doesn't exist, create it
    if not hasattr(instance, 'portfolio'):
        Portfolio.objects.create(
            user=instance,
            cash_balance=100000.00
        )