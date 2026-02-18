from trading.models import Stock
from services.nepse_client import NepseClient
import logging

logger = logging.getLogger(__name__)

def update_all_prices():
    """Update prices for all stocks"""
    
    # Get live market data
    live_data = NepseClient.get_live_prices()
    
    if not live_data:
        logger.warning("Could not fetch live prices")
        return 0
    
    updated_count = 0
    
    # Update each stock in database
    for item in live_data:
        symbol = item.get('symbol')
        price = item.get('lastTradedPrice')
        
        if not symbol or not price:
            continue
        
        try:
            stock = Stock.objects.get(symbol=symbol)
            stock.current_price = price
            stock.save()
            updated_count += 1
        except Stock.DoesNotExist:
            # Stock not in our DB yet
            pass
    
    logger.info(f"Updated {updated_count} stock prices")
    return updated_count

def update_stock_price(symbol):
    """Update single stock price"""
    price_data = NepseClient.get_stock_price(symbol)
    
    if price_data and price_data.get('price'):
        try:
            stock = Stock.objects.get(symbol=symbol)
            stock.current_price = price_data['price']
            stock.save()
            return True
        except Stock.DoesNotExist:
            pass
    
    return False