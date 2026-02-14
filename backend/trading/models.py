from django.db import models

class Stock(models.Model):
    symbol = models.CharField(max_length=10, unique=True)  # E.g., 'NIC', 'NMB'
    name = models.CharField(max_length=200)
    current_price = models.DecimalField(max_digits=10, decimal_places=2)
    sector = models.CharField(max_length=100, blank=True)
    last_updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.symbol} - {self.name}"

class Portfolio(models.Model):
    """
    Tracks user's virtual money and portfolio summary
    One-to-One relationship with User
    """
    user = models.OneToOneField(
        'users_authentication.CustomUser',  # Reference your custom user model
        on_delete=models.CASCADE,
        related_name='portfolio'
    )
    cash_balance = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=100000.00,  # Start with Rs. 100,000
        help_text="Virtual cash available for trading"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.email}'s Portfolio (Balance: Rs.{self.cash_balance})"
    
    class Meta:
        verbose_name_plural = "Portfolios"
        
class Trade(models.Model):
    """
    Records every buy/sell transaction
    """
    class OrderType(models.TextChoices):
        BUY = 'BUY', 'Buy'
        SELL = 'SELL', 'Sell'
    
    class OrderStatus(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        COMPLETED = 'COMPLETED', 'Completed'
        CANCELLED = 'CANCELLED', 'Cancelled'
        FAILED = 'FAILED', 'Failed'
    
    user = models.ForeignKey(
        'users_authentication.CustomUser',
        on_delete=models.CASCADE,
        related_name='trades'
    )
    stock = models.ForeignKey(
        Stock,
        on_delete=models.PROTECT,  # Can't delete stock if trades exist
        related_name='trades'
    )
    quantity = models.PositiveIntegerField()
    price_per_share = models.DecimalField(max_digits=10, decimal_places=2)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    order_type = models.CharField(max_length=4, choices=OrderType.choices)
    status = models.CharField(
        max_length=20, 
        choices=OrderStatus.choices,
        default=OrderStatus.COMPLETED  # Start simple
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.order_type} {self.quantity} {self.stock.symbol} @ Rs.{self.price_per_share}"
    
    class Meta:
        ordering = ['-timestamp']  # Show newest first