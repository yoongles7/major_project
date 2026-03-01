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
    created_count = 0
    
    # Create a set of existing symbols for quick lookup
    existing_symbols = set(Stock.objects.values_list('symbol', flat=True))
    
    # Update each stock in database
    for item in live_data:
        symbol = item.get('symbol')
        
        # API uses lastTradedPrice
        price = item.get('lastTradedPrice')
        
        if not symbol or not price:
            continue
        
        try:
            if symbol in existing_symbols:
                # Update existing stock
                Stock.objects.filter(symbol=symbol).update(
                    current_price=price,
                    name=item.get('companyName', item.get('securityName', symbol)),
                    sector=item.get('sectorName', 'Unknown')
                )
                updated_count += 1
                logger.debug(f"Updated {symbol}: ₹{price}")
            else:
                # Create new stock
                Stock.objects.create(
                    symbol=symbol,
                    name=item.get('companyName', item.get('securityName', symbol)),
                    current_price=price,
                    sector=item.get('sectorName', 'Unknown')
                )
                created_count += 1
                logger.info(f"Created new stock: {symbol} at ₹{price}")
                
        except Exception as e:
            logger.error(f"Error updating {symbol}: {e}")
    
    logger.info(f"Updated {updated_count} stocks, created {created_count} new stocks")
    return updated_count + created_count

def update_stock_price(symbol):
    """Update single stock price"""
    price_data = NepseClient.get_stock_price(symbol)
    
    if price_data and price_data.get('price'):
        try:
            stock = Stock.objects.get(symbol=symbol)
            stock.current_price = price_data['price']
            stock.save()
            logger.info(f"Updated {symbol} to ₹{price_data['price']}")
            return True
        except Stock.DoesNotExist:
            # Create the stock if it doesn't exist
            try:
                Stock.objects.create(
                    symbol=symbol,
                    name=f"{symbol} (NEPSE)",
                    current_price=price_data['price'],
                    sector="Unknown"
                )
                logger.info(f"Created {symbol} with price ₹{price_data['price']}")
                return True
            except Exception as e:
                logger.error(f"Failed to create {symbol}: {e}")
        except Exception as e:
            logger.error(f"Error updating {symbol}: {e}")
    
    return False