from django.db import models
from django.conf import settings
from decimal import Decimal

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
        
class Holding(models.Model):
    """
    Tracks how many shares a user owns of a specific stock
    One record per user per stock they own
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='holdings'
    )
    stock = models.ForeignKey(
        'Stock', 
        on_delete=models.CASCADE,
        related_name='holdings'
    )
    
    # Core fields
    quantity = models.PositiveIntegerField(default=0)  # Number of shares owned
    average_buy_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0
    )  # Average price paid per share
    
    # Calculated fields (updated on each trade)
    total_invested = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=0
    )  # Total money spent on this stock
    
    # Meta data
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        # Ensure one record per user per stock
        unique_together = ['user', 'stock']
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"{self.user.email} - {self.stock.symbol}: {self.quantity} shares"
    
    @property
    def current_value(self):
        """Current market value of these holdings"""
        return self.quantity * self.stock.current_price
    
    @property
    def profit_loss(self):
        """Profit/Loss on this holding"""
        return self.current_value - self.total_invested
    
    @property
    def profit_loss_percentage(self):
        """Profit/Loss as percentage"""
        if self.total_invested > 0:
            return (self.profit_loss / self.total_invested) * 100
        return 0
    
    def update_current_value(self):
        """Update current value and profit/loss based on latest stock price"""
        self.current_value = self.quantity * self.stock.current_price
        self.profit_loss = self.current_value - self.total_invested
        self.save()
        return self.current_value
    
    def get_profit_loss_percentage(self):
        """Calculate profit/loss as percentage"""
        if self.total_invested == 0:
            return 0
        return (self.profit_loss / self.total_invested) * 100
    
    def update_after_buy(self, quantity_bought, price_per_share):
        """
        Update holding after a buy order
        Calculates new average price correctly
        """
        # Calculate new values
        new_total_invested = self.total_invested + (quantity_bought * price_per_share)
        new_quantity = self.quantity + quantity_bought
        
        # Update fields
        self.quantity = new_quantity
        self.total_invested = new_total_invested
        self.average_buy_price = new_total_invested / new_quantity
        self.save()
    
    def update_after_sell(self, quantity_sold, price_per_share):
        """
        Update holding after a sell order
        Reduces quantity but keeps average price same
        """
        # Ensure quantity_sold is Decimal for consistent math
        if not isinstance(quantity_sold, Decimal):
            quantity_sold = Decimal(str(quantity_sold))
        
        # Calculate amount to remove from total_invested
        # This is more accurate than using proportion
        amount_to_remove = self.average_buy_price * quantity_sold
        
        # Update fields
        self.total_invested -= amount_to_remove
        self.quantity -= quantity_sold
        
        if self.quantity == 0:
            self.delete()
        else:
            self.save()