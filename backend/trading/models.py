from django.db import models
from django.conf import settings
from decimal import Decimal
from datetime import datetime, timedelta

class Stock(models.Model):
    symbol = models.CharField(max_length=20, unique=True)  # E.g., 'NIC', 'NMB'
    name = models.CharField(max_length=200)
    current_price = models.DecimalField(max_digits=10, decimal_places=2)
    sector = models.CharField(max_length=100, blank=True)
    last_updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.symbol} - {self.name}"
class Portfolio(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    cash_balance = models.DecimalField(max_digits=12, decimal_places=2, default=100000.00)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.email}'s Portfolio"
    
    # === NEW METHODS START HERE ===
    
    def get_holdings(self):
        """Get all holdings for this portfolio"""
        return self.user.holdings.all()
    
    def get_total_stock_value(self):
        """Calculate current value of all stocks owned"""
        total = Decimal('0.00')
        for holding in self.get_holdings():
            # Current market value = quantity * current stock price
            current_value = holding.quantity * holding.stock.current_price
            total += current_value
        return total
    
    def get_total_invested(self):
        """Calculate total money invested in stocks (buy price)"""
        total = Decimal('0.00')
        for holding in self.get_holdings():
            total += holding.total_invested
        return total
    
    def get_total_portfolio_value(self):
        """Total value = cash + current stock value"""
        return self.cash_balance + self.get_total_stock_value()
    
    def get_total_profit_loss(self):
        """Total P&L = current value - invested amount"""
        return self.get_total_stock_value() - self.get_total_invested()
    
    def get_profit_loss_percentage(self):
        """P&L as percentage of invested amount"""
        invested = self.get_total_invested()
        if invested == 0:
            return Decimal('0.00')
        pl = self.get_total_profit_loss()
        return (pl / invested) * 100
    
    def get_portfolio_summary(self):
        """Get complete portfolio summary as dictionary"""
        return {
            'cash_balance': float(self.cash_balance),
            'total_invested': float(self.get_total_invested()),
            'total_stock_value': float(self.get_total_stock_value()),
            'total_portfolio_value': float(self.get_total_portfolio_value()),
            'total_profit_loss': float(self.get_total_profit_loss()),
            'profit_loss_percentage': float(self.get_profit_loss_percentage()),
            'holdings_count': self.get_holdings().count(),
            'last_updated': self.updated_at.isoformat()
        }
        
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
    price_source = models.CharField(
        max_length=20,
        choices=[
            ('nepse_api_live', 'Live NEPSE API'),
            ('nepse_api_cached', 'Cached NEPSE API'),
            ('database_cache', 'Database Cache'),
            ('database_fallback', 'Emergency Fallback'),
            ('mock_data', 'Mock Data (Development)')
        ],
        default='mock_data',
        help_text="Where the price came from"
    )
        
    def __str__(self):
        return f"{self.order_type} {self.quantity} {self.stock.symbol} @ Rs.{self.price_per_share}"
    
    class OrderStatus(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        EXECUTED = 'EXECUTED', 'Executed'
        FAILED = 'FAILED', 'Failed'
        CANCELLED = 'CANCELLED', 'Cancelled'
    
    status = models.CharField(
        max_length=10,
        choices=OrderStatus.choices,
        default=OrderStatus.EXECUTED
    )
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
    
    # Core fields (YOUR EXISTING FIELDS - KEEP THEM)
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
    
    # NEW FIELDS FOR ENHANCED TRACKING
    first_purchase_date = models.DateTimeField(null=True, blank=True)
    last_purchase_date = models.DateTimeField(auto_now=True)
    
    # Meta data
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        # Ensure one record per user per stock
        unique_together = ['user', 'stock']
        ordering = ['-updated_at']
        
        # NEW: Add indexes for faster queries
        indexes = [
            models.Index(fields=['user', 'stock']),
            models.Index(fields=['user', '-updated_at']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.stock.symbol}: {self.quantity} shares"
    
    # === YOUR EXISTING PROPERTIES (KEEP ALL OF THESE) ===
    
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
    
    # === YOUR EXISTING METHODS (KEEP ALL OF THESE) ===
    
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
        
        # Set first purchase date if this is the first buy
        if not self.first_purchase_date:
            self.first_purchase_date = datetime.now()
        
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
        amount_to_remove = self.average_buy_price * quantity_sold
        
        # Update fields
        self.total_invested -= amount_to_remove
        self.quantity -= quantity_sold
        
        if self.quantity == 0:
            self.delete()
        else:
            self.save()
    
    def update_current_value(self):
        """Update current value and profit/loss based on latest stock price"""
        self.current_value = self.quantity * self.stock.current_price
        self.profit_loss = self.current_value - self.total_invested
        self.save()
        return self.current_value
    
    # === NEW ENHANCED METHODS (ADD THESE) ===
    
    def get_current_value(self):
        """Same as property but as method for consistency"""
        return self.quantity * self.stock.current_price
    
    def get_days_held(self):
        """Number of days since first purchase"""
        if not self.first_purchase_date:
            return 0
        delta = datetime.now() - self.first_purchase_date
        return delta.days
    
    def get_annualized_return(self):
        """
        Calculate annualized return percentage
        Useful for comparing performance across different holding periods
        """
        if self.total_invested == 0 or self.get_days_held() == 0:
            return 0
        
        total_return = float(self.profit_loss) / float(self.total_invested)
        days_held = self.get_days_held()
        
        # Annualized return = (1 + total_return)^(365/days) - 1
        annualized = ((1 + total_return) ** (365 / days_held)) - 1
        
        return annualized * 100
    
    def get_breakdown_by_purchase(self):
        """
        Get breakdown of different purchase lots
        Requires separate Lot model - advanced feature
        """
        from .models import Trade
        buy_trades = Trade.objects.filter(
            user=self.user,
            stock=self.stock,
            order_type='BUY'
        ).order_by('timestamp')
        
        lots = []
        remaining_quantity = self.quantity
        
        for trade in buy_trades:
            if remaining_quantity <= 0:
                break
            
            # This is simplified - actual lot tracking needs FIFO logic
            lots.append({
                'date': trade.timestamp,
                'quantity': trade.quantity,
                'price': float(trade.price_per_share),
                'total': float(trade.total_amount)
            })
        
        return lots
    
    def to_dict(self):
        """
        Convert holding to dictionary for API responses
        This is what frontend will use
        """
        return {
            # Stock info
            'symbol': self.stock.symbol,
            'company_name': self.stock.name,
            'sector': self.stock.sector,
            
            # Holding details
            'quantity': self.quantity,
            'average_buy_price': float(self.average_buy_price),
            'total_invested': float(self.total_invested),
            
            # Current values
            'current_price': float(self.stock.current_price),
            'current_value': float(self.get_current_value()),
            
            # Performance metrics
            'profit_loss': float(self.profit_loss),
            'profit_loss_percentage': float(self.profit_loss_percentage),
            'days_held': self.get_days_held(),
            'annualized_return': float(self.get_annualized_return()),
            
            # Dates
            'first_purchased': self.first_purchase_date.isoformat() if self.first_purchase_date else None,
            'last_updated': self.updated_at.isoformat(),
            
            # Weight in portfolio (calculated later)
            'portfolio_weight': 0  # Will be set by PortfolioService
        }
    
    def calculate_portfolio_weight(self, total_portfolio_value):
        """
        Calculate what percentage of portfolio this holding represents
        """
        if total_portfolio_value == 0:
            return 0
        return (self.get_current_value() / total_portfolio_value) * 100