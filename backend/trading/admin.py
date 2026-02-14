from django.contrib import admin
from .models import Stock, Portfolio, Trade

@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ['symbol', 'name', 'current_price', 'sector', 'last_updated']
    search_fields = ['symbol', 'name']

@admin.register(Portfolio)
class PortfolioAdmin(admin.ModelAdmin):
    list_display = ['user', 'cash_balance', 'created_at']
    list_select_related = ['user']

@admin.register(Trade)
class TradeAdmin(admin.ModelAdmin):
    list_display = ['user', 'stock', 'order_type', 'quantity', 'total_amount', 'timestamp']
    list_filter = ['order_type', 'status']
    search_fields = ['user__email', 'stock__symbol']