from rest_framework import serializers
from .models import Stock, Trade, Holding, Portfolio
from decimal import Decimal

class StockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stock
        fields = ['id', 'symbol', 'name', 'current_price', 'sector', 'last_updated']

class TradeSerializer(serializers.ModelSerializer):
    symbol = serializers.CharField(source='stock.symbol', read_only=True)
    company_name = serializers.CharField(source='stock.name', read_only=True)
    
    class Meta:
        model = Trade
        fields = [
            'id', 'symbol', 'company_name', 'order_type', 
            'quantity', 'price_per_share', 'total_amount', 'timestamp'
        ]

class HoldingSerializer(serializers.ModelSerializer):
    symbol = serializers.CharField(source='stock.symbol', read_only=True)
    company_name = serializers.CharField(source='stock.name', read_only=True)
    current_price = serializers.DecimalField(
        source='stock.current_price', 
        max_digits=10, 
        decimal_places=2,
        read_only=True
    )
    current_value = serializers.SerializerMethodField()
    profit_loss = serializers.SerializerMethodField()
    profit_loss_percentage = serializers.SerializerMethodField()
    
    class Meta:
        model = Holding
        fields = [
            'id', 'symbol', 'company_name', 'quantity',
            'average_buy_price', 'total_invested', 'current_price',
            'current_value', 'profit_loss', 'profit_loss_percentage'
        ]
    
    def get_current_value(self, obj):
        return obj.quantity * obj.stock.current_price
    
    def get_profit_loss(self, obj):
        return (obj.quantity * obj.stock.current_price) - obj.total_invested
    
    def get_profit_loss_percentage(self, obj):
        if obj.total_invested == 0:
            return 0
        return ((obj.quantity * obj.stock.current_price) - obj.total_invested) / obj.total_invested * 100

class PortfolioSerializer(serializers.ModelSerializer):
    """Serializer for Portfolio model"""
    total_value = serializers.SerializerMethodField()
    total_profit_loss = serializers.SerializerMethodField()
    holdings_count = serializers.SerializerMethodField()
    holdings = serializers.SerializerMethodField()
    
    class Meta:
        model = Portfolio
        fields = [
            'id', 'cash_balance', 'total_value', 
            'total_profit_loss', 'holdings_count', 
            'holdings', 'updated_at', 'created_at'
        ]
    
    def get_total_value(self, obj):
        """Calculate total portfolio value (cash + stocks)"""
        holdings = Holding.objects.filter(user=obj.user)
        stock_value = sum(h.quantity * h.stock.current_price for h in holdings)
        return float(obj.cash_balance + stock_value)
    
    def get_total_profit_loss(self, obj):
        """Calculate total profit/loss"""
        holdings = Holding.objects.filter(user=obj.user)
        total_invested = sum(h.total_invested for h in holdings)
        total_current = sum(h.quantity * h.stock.current_price for h in holdings)
        return float(total_current - total_invested)
    
    def get_holdings_count(self, obj):
        """Get number of unique holdings"""
        return Holding.objects.filter(user=obj.user).count()
    
    def get_holdings(self, obj):
        """Get all holdings with details"""
        holdings = Holding.objects.filter(user=obj.user)
        return HoldingSerializer(holdings, many=True).data
class PortfolioSummarySerializer(serializers.ModelSerializer):
    total_value = serializers.SerializerMethodField()
    total_profit_loss = serializers.SerializerMethodField()
    holdings_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Portfolio
        fields = [
            'id', 'cash_balance', 'total_value', 
            'total_profit_loss', 'holdings_count', 'updated_at'
        ]
    
    def get_total_value(self, obj):
        holdings = Holding.objects.filter(user=obj.user)
        stock_value = sum(h.quantity * h.stock.current_price for h in holdings)
        return obj.cash_balance + stock_value
    
    def get_total_profit_loss(self, obj):
        holdings = Holding.objects.filter(user=obj.user)
        total_invested = sum(h.total_invested for h in holdings)
        total_current = sum(h.quantity * h.stock.current_price for h in holdings)
        return total_current - total_invested
    
    def get_holdings_count(self, obj):
        return Holding.objects.filter(user=obj.user).count()