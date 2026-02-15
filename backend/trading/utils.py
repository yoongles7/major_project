from decimal import Decimal
from .models import Holding

def update_holdings_after_buy(user, stock, quantity, price_per_share):
    """
    Update or create holding record after a buy order
    Returns the updated/created holding
    """
    total_cost = quantity * price_per_share
    
    # Try to get existing holding
    holding, created = Holding.objects.get_or_create(
        user=user,
        stock=stock,
        defaults={
            'quantity': quantity,
            'average_buy_price': price_per_share,
            'total_invested': total_cost
        }
    )
    
    if not created:
        # Update existing holding
        # Calculate new average price correctly
        new_total_invested = holding.total_invested + total_cost
        new_quantity = holding.quantity + quantity
        new_avg_price = new_total_invested / new_quantity
        
        holding.quantity = new_quantity
        holding.average_buy_price = new_avg_price
        holding.total_invested = new_total_invested
        holding.save()
    
    return holding, created

def can_user_afford(user, total_cost):
    """Check if user has enough cash balance"""
    return user.portfolio.cash_balance >= total_cost

def validate_buy_order(stock, quantity):
    """Validate buy order parameters"""
    errors = []
    
    if quantity <= 0:
        errors.append("Quantity must be positive")
    
    if quantity > 10000:  # Reasonable limit
        errors.append("Maximum 10,000 shares per order")
    
    return errors