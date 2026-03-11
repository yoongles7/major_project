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
    
    @classmethod
    def get_intraday_data(cls, symbol, days=1):
        """
        Get intraday candlestick data for chart
        This is what your frontend needs for the landing page chart
        """
        cache_key = f'intraday_{symbol}_{days}'
        
        # Check cache first
        cached = cache.get(cache_key)
        if cached:
            logger.debug(f"Returning cached intraday data for {symbol}")
            return cached
        
        # Check market status
        market_status = cls.get_market_status()
        
        try:
            # Try to get from API
            response = requests.get(
                f"{cls.BASE_URL}/stockIntraday",
                params={
                    'symbol': symbol,
                    'days': days if days > 1 else None  # API might expect different param
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Format for candlestick chart
                formatted_data = []
                for item in data:
                    # Handle different possible date formats
                    date_str = item.get('date') or item.get('time') or item.get('timestamp')
                    
                    formatted_data.append({
                        'time': date_str,
                        'open': float(item.get('open', 0)),
                        'high': float(item.get('high', 0)),
                        'low': float(item.get('low', 0)),
                        'close': float(item.get('close', 0)),
                        'volume': int(item.get('volume', 0))
                    })
                
                # Sort by time
                formatted_data.sort(key=lambda x: x['time'])
                
                # Cache appropriately
                if market_status and market_status['is_open']:
                    cache_timeout = 30  # 30 seconds when market open
                else:
                    cache_timeout = 300  # 5 minutes when market closed
                
                cache.set(cache_key, formatted_data, cache_timeout)
                logger.info(f"Got intraday data for {symbol}: {len(formatted_data)} points")
                return formatted_data
                
        except requests.exceptions.ConnectionError:
            logger.error(f"Cannot connect to NEPSE API at {cls.BASE_URL}")
        except Exception as e:
            logger.error(f"Failed to fetch intraday for {symbol}: {e}")
        
        # Generate mock intraday data if API fails
        logger.info(f"Generating mock intraday data for {symbol}")
        mock_data = cls.generate_mock_intraday(symbol, days)
        cache.set(cache_key, mock_data, 300)  # Cache mock data for 5 minutes
        return mock_data

    @classmethod
    def generate_mock_intraday(cls, symbol, days=1):
        """Generate mock candlestick data for testing"""
        import random
        from datetime import datetime, timedelta
        
        mock_data = []
        now = datetime.now()
        
        # Get base price from mock prices or use default
        base_price = cls.MOCK_PRICES.get(symbol, {}).get('price', 400)
        
        # Generate data points (one per hour for demonstration)
        for day in range(days):
            for hour in range(10, 15):  # 10 AM to 3 PM
                time_point = now - timedelta(days=days-day-1, hours=14-hour)
                
                # Random walk price
                open_price = base_price + random.uniform(-5, 5)
                close_price = open_price + random.uniform(-8, 8)
                high_price = max(open_price, close_price) + random.uniform(0, 3)
                low_price = min(open_price, close_price) - random.uniform(0, 3)
                
                mock_data.append({
                    'time': time_point.strftime('%Y-%m-%d %H:%M:%S'),
                    'open': round(open_price, 2),
                    'high': round(high_price, 2),
                    'low': round(low_price, 2),
                    'close': round(close_price, 2),
                    'volume': random.randint(1000, 10000)
                })
                
                base_price = close_price  # Next candle starts where previous ended
        
        return mock_data