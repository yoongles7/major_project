import requests
import logging
from django.core.cache import cache

logger = logging.getLogger(__name__)

class NepseClient:
    """Client to interact with local NEPSE API"""
    
    # Base URL of your locally running NEPSE API
    BASE_URL = "http://localhost:8000"
    
    @classmethod
    def get_stock_list(cls):
        """Fetch all stocks from NEPSE"""
        cache_key = 'nepse_stock_list'
        
        # Try cache first (reduce API calls)
        cached = cache.get(cache_key)
        if cached:
            return cached
        
        try:
            response = requests.get(
                f"{cls.BASE_URL}/CompanyList",
                timeout=10  # Don't wait forever
            )
            
            if response.status_code == 200:
                data = response.json()
                # Cache for 1 hour (3600 seconds)
                cache.set(cache_key, data, 3600)
                return data
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch stock list: {e}")
        
        return None
    
    @classmethod
    def get_live_prices(cls):
        """Get live market data"""
        try:
            response = requests.get(
                f"{cls.BASE_URL}/LiveMarket",
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            logger.error(f"Live market fetch failed: {e}")
        
        return None
    
    @classmethod
    def get_stock_price(cls, symbol):
        """Get price for a specific stock"""
        try:
            # First try LiveMarket (has all stocks)
            live_data = cls.get_live_prices()
            if live_data:
                for stock in live_data:
                    if stock.get('symbol') == symbol:
                        return {
                            'price': stock.get('lastTradedPrice'),
                            'change': stock.get('percentChange'),
                            'volume': stock.get('totalTradedQuantity')
                        }
            
            # Fallback: try company details
            response = requests.get(
                f"{cls.BASE_URL}/CompanyDetails",
                params={'symbol': symbol},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'price': data.get('lastTradedPrice'),
                    'change': data.get('percentChange'),
                    'volume': data.get('totalTradedQuantity')
                }
        except Exception as e:
            logger.error(f"Failed to get price for {symbol}: {e}")
        
        return None