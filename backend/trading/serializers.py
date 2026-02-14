from rest_framework import serializers
from .models import Stock, Portfolio, Trade, Holding

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
        
class HoldingSerializer(serializers.ModelSerializer):
    """Serializer for holdings with calculated fields"""
    stock_symbol = serializers.CharField(source='stock.symbol', read_only=True)
    stock_name = serializers.CharField(source='stock.name', read_only=True)
    current_price = serializers.DecimalField(
        source='stock.current_price', 
        max_digits=10, 
        decimal_places=2,
        read_only=True
    )
    current_value = serializers.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        read_only=True
    )
    profit_loss = serializers.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        read_only=True
    )
    profit_loss_percentage = serializers.FloatField(read_only=True)
    
    class Meta:
        model = Holding
        fields = [
            'id', 'stock_symbol', 'stock_name', 'quantity',
            'average_buy_price', 'total_invested', 'current_price',
            'current_value', 'profit_loss', 'profit_loss_percentage',
            'updated_at'
        ]