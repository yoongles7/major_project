import requests
import logging
from django.core.cache import cache
from datetime import datetime
import pytz
from enum import Enum

logger = logging.getLogger(__name__)

class MarketStatus(Enum):
    """Enum for market status values"""
    OPEN = "OPEN"
    CLOSED = "CLOSE"
    HALTED = "HALT"
    UNKNOWN = "UNKNOWN"

class NepseClient:
    BASE_URL = "http://localhost:8003"
    
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
    def get_market_status(cls):
        """Check if NEPSE market is currently open"""
        cache_key = 'nepse_market_status'
        
        # Try cache first
        cached = cache.get(cache_key)
        if cached:
            return cached
        
        try:
            response = requests.get(
                f"{cls.BASE_URL}/IsNepseOpen",
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Get raw status from API
                raw_status = data.get('isOpen', 'UNKNOWN').upper()
                
                # Convert to our enum
                status = MarketStatus.UNKNOWN
                message = ""
                trading_allowed = False
                
                if raw_status == "OPEN":
                    status = MarketStatus.OPEN
                    message = "Market is OPEN for trading"
                    trading_allowed = True
                elif raw_status == "CLOSE":
                    status = MarketStatus.CLOSED
                    message = "Market is CLOSED"
                    trading_allowed = False
                elif raw_status == "HALT":
                    status = MarketStatus.HALTED
                    message = "Market is HALTED (trading temporarily suspended)"
                    trading_allowed = False
                else:
                    message = f"Unknown market status: {raw_status}"
                    trading_allowed = False
                
                # Format the response
                result = {
                    'status': status.value,
                    'is_open': status == MarketStatus.OPEN,
                    'is_halted': status == MarketStatus.HALTED,
                    'is_closed': status == MarketStatus.CLOSED,
                    'trading_allowed': trading_allowed,
                    'message': message,
                    'raw_status': raw_status,
                    'current_time': data.get('asOf'),
                    'market_hours': 'Sunday-Thursday, 11:00 AM - 3:00 PM NPT'
                }
                
                # Cache for 60 seconds
                cache.set(cache_key, result, 60)
                
                logger.info(f"Market status: {raw_status} at {data.get('asOf')}")
                return result
                
        except requests.exceptions.ConnectionError:
            logger.error(f"Cannot connect to NEPSE API at {cls.BASE_URL}")
        except Exception as e:
            logger.error(f"Failed to fetch market status: {e}")
        
        return None
    
    @classmethod
    def get_live_prices(cls):
        """Get live market data with fallback"""
        cache_key = 'nepse_live_prices'
        
        # Try cache first
        cached = cache.get(cache_key)
        if cached:
            logger.debug("Returning cached live prices")
            return cached
        
        # First check if market is open/halted
        market_status = cls.get_market_status()
        
        # If market is CLOSED or HALTED, return mock data immediately
        if market_status and (market_status['is_closed'] or market_status['is_halted']):
            logger.info(f"Market is {market_status['status']}, using mock data")
            mock_data = cls.get_mock_prices()
            cache.set(cache_key, mock_data, 60)
            return mock_data
        
        try:
            logger.debug("Fetching live prices from API...")
            response = requests.get(
                f"{cls.BASE_URL}/LiveMarket",
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"API returned {len(data) if data else 0} stocks")
                
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
        
        # First check market status
        market_status = cls.get_market_status()
        
        # If market is CLOSED or HALTED, use mock data
        if market_status and (market_status['is_closed'] or market_status['is_halted']):
            logger.debug(f"Market {market_status['status']}, using mock for {symbol}")
            if symbol in cls.MOCK_PRICES:
                return {
                    'price': cls.MOCK_PRICES[symbol]['price'],
                    'change': cls.MOCK_PRICES[symbol]['change'],
                    'source': 'mock (market closed/halted)'
                }
        
        # Try live data first
        live_data = cls.get_live_prices()
        if live_data:
            for item in live_data:
                if item.get('symbol') == symbol:
                    price_data = {
                        'price': item.get('lastTradedPrice'),
                        'change': item.get('percentageChange'),
                        'high': item.get('highPrice'),
                        'low': item.get('lowPrice'),
                        'volume': item.get('totalTradeQuantity'),
                        'open': item.get('openPrice'),
                        'prev_close': item.get('previousClose'),
                        'source': 'live'
                    }
                    logger.debug(f"Found {symbol}: ₹{price_data['price']}")
                    return price_data
        
        # Fallback to mock data
        if symbol in cls.MOCK_PRICES:
            logger.debug(f"Using mock data for {symbol}")
            mock_data = cls.MOCK_PRICES[symbol].copy()
            mock_data['source'] = 'mock'
            return mock_data
        
        logger.warning(f"No price found for {symbol}")
        return None
    
    @classmethod
    def get_mock_prices(cls):
        """Return mock prices for testing"""
        mock_list = []
        for k, v in cls.MOCK_PRICES.items():
            mock_list.append({
                "symbol": k,
                "lastTradedPrice": v['price'],
                "percentageChange": v['change'],
                "companyName": f"{k} Company",
                "source": "mock"
            })
        return mock_list
    
    @classmethod
    def get_stock_list(cls):
        """Get list of all stocks"""
        cache_key = 'nepse_stock_list'
        
        cached = cache.get(cache_key)
        if cached:
            return cached
        
        try:
            response = requests.get(
                f"{cls.BASE_URL}/CompanyList",
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                cache.set(cache_key, data, 3600)  # Cache for 1 hour
                return data
        except Exception as e:
            logger.error(f"Failed to fetch stock list: {e}")
        
        # Return mock stock list
        mock_list = [
            {"symbol": k, "companyName": f"{k} Company", "sectorName": "Various"}
            for k in cls.MOCK_PRICES.keys()
        ]
        cache.set(cache_key, mock_list, 3600)
        return mock_list
    
    @classmethod
    def get_market_summary(cls):
        """Get market summary (top gainers, losers, etc)"""
        try:
            response = requests.get(
                f"{cls.BASE_URL}/Summary",
                timeout=5
            )
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            logger.error(f"Failed to fetch market summary: {e}")
        
        return None
    
    @classmethod
    def get_top_gainers(cls, limit=5):
        """Get top gaining stocks"""
        summary = cls.get_market_summary()
        if summary and 'topGainers' in summary:
            return summary['topGainers'][:limit]
        return []
    
    @classmethod
    def get_top_losers(cls, limit=5):
        """Get top losing stocks"""
        summary = cls.get_market_summary()
        if summary and 'topLosers' in summary:
            return summary['topLosers'][:limit]
        return []
    
    @classmethod
    def get_nepse_index(cls):
        """Get current NEPSE index"""
        try:
            response = requests.get(
                f"{cls.BASE_URL}/NepseIndex",
                timeout=5
            )
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            logger.error(f"Failed to fetch NEPSE index: {e}")
        
        return None