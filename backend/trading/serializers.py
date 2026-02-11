from rest_framework import serializers
from .models import Stock

class StockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stock
        fields = ['id', 'symbol', 'name', 'current_price', 'sector', 'last_updated']
        # Or use fields = '__all__' to include all fields