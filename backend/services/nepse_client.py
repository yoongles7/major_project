import requests
import logging
from django.core.cache import cache
from datetime import datetime
import pytz

logger = logging.getLogger(__name__)

class NepseClient:
    BASE_URL = "http://localhost:8000"
    
    # Mock data for when API is down/market closed
    MOCK_PRICES = {
        'NABIL': {'price': 1850.50, 'change': 1.25},
        'NIC': {'price': 420.75, 'change': -0.50},
        'NMB': {'price': 210.30, 'change': 0.75},
        'SCB': {'price': 650.25, 'change': 0.00},
        'NTC': {'price': 720.00, 'change': 0.25},
        'HDL': {'price': 1500.50, 'change': -1.20},
        'PCBL': {'price': 180.25, 'change': 0.50},
        'SBI': {'price': 450.00, 'change': -0.25},
        'EBL': {'price': 550.75, 'change': 0.15},
        'PRVU': {'price': 300.50, 'change': 0.30},
        'ADBL': {'price': 320.00, 'change': 0.40},
        'CZBIL': {'price': 400.25, 'change': -0.10},
        'GBIME': {'price': 280.75, 'change': 0.20},
        'NABILP': {'price': 125.50, 'change': 0.00},
        'SANIMA': {'price': 350.00, 'change': 0.15},
    }
    
    @classmethod
    def is_market_open(cls):
        """Check if NEPSE market is currently open"""
        nepali_tz = pytz.timezone('Asia/Kathmandu')
        now = datetime.now(nepali_tz)
        
        # NEPSE: Sunday (6) to Thursday (3), 11:00-15:00
        day = now.weekday()
        if day > 4 or day == 5:  # Friday(4) or Saturday(5)
            return False
        
        market_open = datetime.strptime("11:00", "%H:%M").time()
        market_close = datetime.strptime("15:00", "%H:%M").time()
        
        return market_open <= now.time() <= market_close
    
    @classmethod
    def get_live_prices(cls):
        """Get live market data with fallback"""
        cache_key = 'nepse_live_prices'
        
        # Try cache first
        cached = cache.get(cache_key)
        if cached:
            logger.debug("Returning cached live prices")
            return cached
        
        try:
            logger.debug("Fetching live prices from API...")
            response = requests.get(
                f"{cls.BASE_URL}/LiveMarket",
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"API returned {len(data)} stocks")
                
                if data and len(data) > 0:
                    # Log sample for debugging
                    sample = data[0]
                    logger.debug(f"Sample data: {sample.get('symbol')} = {sample.get('lastTradedPrice')}")
                    
                    # Cache for 30 seconds
                    cache.set(cache_key, data, 30)
                    return data
                else:
                    logger.warning("API returned empty data")
            else:
                logger.warning(f"API returned status {response.status_code}")
                
        except Exception as e:
            logger.error(f"Live market fetch failed: {e}")
        
        # Return mock data if API fails
        logger.info("Using mock data as fallback")
        mock_data = cls.get_mock_prices()
        cache.set(cache_key, mock_data, 60)
        return mock_data
    
    @classmethod
    def get_stock_price(cls, symbol):
        """Get price for specific stock"""
        logger.debug(f"Getting price for {symbol}")
        
        # Try live data first
        live_data = cls.get_live_prices()
        if live_data:
            for item in live_data:
                if item.get('symbol') == symbol:
                    price_data = {
                        'price': item.get('lastTradedPrice'),  # API uses lastTradedPrice
                        'change': item.get('percentageChange'),  # API uses percentageChange
                        'high': item.get('highPrice'),
                        'low': item.get('lowPrice'),
                        'volume': item.get('totalTradeQuantity'),
                        'open': item.get('openPrice'),
                        'prev_close': item.get('previousClose')
                    }
                    logger.debug(f"Found {symbol}: ₹{price_data['price']}")
                    return price_data
        
        # Fallback to mock data
        if symbol in cls.MOCK_PRICES:
            logger.debug(f"Using mock data for {symbol}")
            return cls.MOCK_PRICES[symbol]
        
        logger.warning(f"No price found for {symbol}")
        return None
    
    @classmethod
    def get_mock_prices(cls):
        """Return mock prices for testing"""
        return [
            {
                "symbol": k, 
                "lastTradedPrice": v['price'], 
                "percentageChange": v['change'],
                "companyName": f"{k} Company"
            }
            for k, v in cls.MOCK_PRICES.items()
        ]
    
    @classmethod
    def get_stock_list(cls):
        """Get list of all stocks"""
        try:
            response = requests.get(
                f"{cls.BASE_URL}/CompanyList",
                timeout=10
            )
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            logger.error(f"Failed to fetch stock list: {e}")
        
        # Return mock stock list
        return [
            {"symbol": k, "companyName": f"{k} Company", "sectorName": "Various"}
            for k in cls.MOCK_PRICES.keys()
        ]