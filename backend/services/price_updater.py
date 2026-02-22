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
        
        # Try multiple possible price field names
        price = (
            item.get('lastTradedPrice') or
            item.get('price') or
            item.get('ltp') or
            item.get('close')
        )
        
        if not symbol or not price:
            continue
        
        try:
            stock = Stock.objects.get(symbol=symbol)
            stock.current_price = price
            stock.save()
            updated_count += 1
            logger.debug(f"Updated {symbol}: ₹{price}")
            
        except Stock.DoesNotExist:
            # Stock not in DB yet - create it
            try:
                Stock.objects.create(
                    symbol=symbol,
                    name=f"{symbol} (NEPSE)",
                    current_price=price,
                    sector="Unknown"
                )
                updated_count += 1
                logger.info(f"Created new stock: {symbol}")
            except Exception as e:
                logger.error(f"Failed to create {symbol}: {e}")
                
        except Exception as e:
            logger.error(f"Error updating {symbol}: {e}")
    
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
            # Create the stock if it doesn't exist
            try:
                Stock.objects.create(
                    symbol=symbol,
                    name=f"{symbol} (NEPSE)",
                    current_price=price_data['price'],
                    sector="Unknown"
                )
                return True
            except Exception as e:
                logger.error(f"Failed to create {symbol}: {e}")
        except Exception as e:
            logger.error(f"Error updating {symbol}: {e}")
    
    return False