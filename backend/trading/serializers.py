from rest_framework import serializers
from .models import Stock, Portfolio, Trade

class StockSerializer(serializers.ModelSerializer):
    """
    Convert Stock model to JSON for API responses
    """
    class Meta:
        model = Stock
        fields = ['id', 'symbol', 'name', 'current_price', 'sector', 'last_updated']
class PortfolioSerializer(serializers.ModelSerializer):
    """
    Serialize portfolio data
    """
    user_email = serializers.ReadOnlyField(source='user.email')
    
    class Meta:
        model = Portfolio
        fields = ['id', 'user_email', 'cash_balance', 'created_at', 'updated_at']

class TradeSerializer(serializers.ModelSerializer):
    """
    Serialize trade data with stock details
    """
    stock_symbol = serializers.ReadOnlyField(source='stock.symbol')
    stock_name = serializers.ReadOnlyField(source='stock.name')
    
    class Meta:
        model = Trade
        fields = [
            'id', 'stock_symbol', 'stock_name', 'quantity', 
            'price_per_share', 'total_amount', 'order_type', 
            'status', 'timestamp'
        ]