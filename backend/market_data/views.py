from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from services.nepse_client import NepseClient
import logging
import datetime
import pytz
from datetime import datetime

logger = logging.getLogger(__name__)

# Helper function for Nepal time conversion
def to_nepal_time(dt_str=None):
    """
    Convert datetime to Nepal time (UTC+5:45)
    If no input, returns current Nepal time
    """
    nepali_tz = pytz.timezone('Asia/Kathmandu')
    
    if dt_str is None:
        return datetime.now(nepali_tz)
    
    try:
        # Try to parse the datetime string
        if isinstance(dt_str, str):
            try:
                dt = datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                dt = datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S')
        else:
            dt = dt_str
        
        # Convert to Nepal time
        if dt.tzinfo is None:
            dt = pytz.UTC.localize(dt)
        
        return dt.astimezone(nepali_tz)
    except Exception as e:
        logger.error(f"Error converting to Nepal time: {e}")
        return datetime.now(nepali_tz)

class MarketStatusView(APIView):
    """Check if market is open using NEPSE API"""
    
    def get(self, request):
        # Try to get status from NEPSE API
        market_status = NepseClient.get_market_status()
        
        if market_status:
            # Determine badge color for frontend
            if market_status['is_open']:
                badge_color = "green"
                badge_text = "OPEN"
            elif market_status['is_halted']:
                badge_color = "orange"
                badge_text = "HALTED"
            else:
                badge_color = "red"
                badge_text = "CLOSED"
            
            return Response({
                'status': market_status['status'],
                'badge': {
                    'color': badge_color,
                    'text': badge_text
                },
                'is_open': market_status['is_open'],
                'is_halted': market_status['is_halted'],
                'is_closed': market_status['is_closed'],
                'trading_allowed': market_status['trading_allowed'],
                'message': market_status['message'],
                'current_time': market_status['current_time'],
                'market_hours': market_status['market_hours'],
                'source': 'NEPSE API'
            })
        else:
            # API failed, use fallback calculation
            return self._fallback_market_status()
    
    def _fallback_market_status(self):
        """Fallback method when API is unavailable"""
        from services.market_hours import is_market_open
        
        nepali_time = datetime.datetime.now(pytz.timezone('Asia/Kathmandu'))
        is_open = is_market_open()
        
        return Response({
            'status': 'OPEN' if is_open else 'CLOSED',
            'badge': {
                'color': 'green' if is_open else 'red',
                'text': 'OPEN' if is_open else 'CLOSED'
            },
            'is_open': is_open,
            'is_halted': False,
            'is_closed': not is_open,
            'trading_allowed': is_open,
            'message': f"Market is {'OPEN' if is_open else 'CLOSED'} (estimated)",
            'current_time': nepali_time.isoformat(),
            'market_hours': 'Sunday-Thursday, 11:00 AM - 3:00 PM NPT',
            'source': 'local calculation (API unavailable)'
        })
        
class LivePricesView(APIView):
    """Get live prices for all stocks"""
    permission_classes = []
    
    def get(self, request):
        prices = NepseClient.get_live_prices()
        return Response(prices)

class StockPriceView(APIView):
    """Get price for specific stock"""
    permission_classes = []
    
    def get(self, request, symbol):
        price_data = NepseClient.get_stock_price(symbol.upper())
        if price_data:
            # Add market status and Nepal time
            market_status = NepseClient.get_market_status()
            
            # Get current Nepal time
            nepali_time = to_nepal_time()
            
            return Response({
                **price_data,
                'market_status': {
                    'is_open': market_status.get('is_open') if market_status else False,
                    'message': market_status.get('message') if market_status else 'Market status unknown'
                },
                'nepal_time': nepali_time.isoformat(),
                'last_updated': datetime.now().isoformat()
            })
        return Response({'error': 'Stock not found'}, status=404)

class IntradayChartView(APIView):
    """Get candlestick chart data for landing page"""
    permission_classes = []
    
    def get(self, request):
        symbol = request.GET.get('symbol', 'NABIL').upper()
        days = int(request.GET.get('days', 1))
        
        # Limit days to reasonable range
        if days > 5:
            days = 5
        
        chart_data = NepseClient.get_intraday_data(symbol, days)
        
        # Get market status to include in response
        market_status = NepseClient.get_market_status()
        
        # Convert timestamps to Nepal time (UTC+5:45)
        formatted_data = []
        for item in chart_data:
            dt_nepal = to_nepal_time(item.get('time'))
            
            # Format in a nice readable format
            if days > 1:
                # For multiple days, show date and time
                time_str = dt_nepal.strftime('%b %d, %H:%M')
            else:
                # For single day, just show time
                time_str = dt_nepal.strftime('%H:%M')
            
            formatted_item = {
                'time': time_str,
                'timestamp': dt_nepal.isoformat(),
                'open': item.get('open', 0),
                'high': item.get('high', 0),
                'low': item.get('low', 0),
                'close': item.get('close', 0),
                'volume': item.get('volume', 0)
            }
            formatted_data.append(formatted_item)
        
        return Response({
            'symbol': symbol,
            'market_status': market_status,
            'data': formatted_data,
            'data_points': len(formatted_data),
            'timezone': 'Asia/Kathmandu (NPT)'
        })

class StockSearchView(APIView):
    """Search stocks by symbol or name"""
    permission_classes = []
    
    def get(self, request):
        query = request.GET.get('q', '').upper()
        stocks = NepseClient.get_stock_list()
        
        if query:
            filtered = [
                s for s in stocks 
                if query in s.get('symbol', '').upper() or 
                   query in s.get('companyName', '').upper()
            ]
        else:
            filtered = stocks[:50]  # Limit to 50 if no query
        
        return Response(filtered)

class MarketSummaryView(APIView):
    """Get market summary (indices, gainers, losers)"""
    permission_classes = []
    
    def get(self, request):
        summary = NepseClient.get_market_summary()
        nepse_index = NepseClient.get_nepse_index()
        
        # Get top gainers and losers - ensure we get actual data
        top_gainers = NepseClient.get_top_gainers(5)
        top_losers = NepseClient.get_top_losers(5)
        
        # If they're None or empty, try to extract from live data
        if not top_gainers or len(top_gainers) == 0:
            live_data = NepseClient.get_live_prices()
            if live_data:
                # Sort by percentageChange descending for gainers
                sorted_by_change = sorted(
                    live_data, 
                    key=lambda x: float(x.get('percentageChange', 0)), 
                    reverse=True
                )
                top_gainers = [
                    {
                        'symbol': item['symbol'],
                        'companyName': item.get('securityName', item['symbol']),
                        'lastTradedPrice': item['lastTradedPrice'],
                        'percentageChange': item['percentageChange'],
                        'volume': item.get('totalTradeQuantity', 0)
                    }
                    for item in sorted_by_change[:5] 
                    if float(item.get('percentageChange', 0)) > 0
                ]
        
        if not top_losers or len(top_losers) == 0:
            live_data = NepseClient.get_live_prices()
            if live_data:
                # Sort by percentageChange ascending for losers
                sorted_by_change = sorted(
                    live_data, 
                    key=lambda x: float(x.get('percentageChange', 0))
                )
                top_losers = [
                    {
                        'symbol': item['symbol'],
                        'companyName': item.get('securityName', item['symbol']),
                        'lastTradedPrice': item['lastTradedPrice'],
                        'percentageChange': item['percentageChange'],
                        'volume': item.get('totalTradeQuantity', 0)
                    }
                    for item in sorted_by_change[:5] 
                    if float(item.get('percentageChange', 0)) < 0
                ]
        
        return Response({
            'summary': summary,
            'nepse_index': nepse_index,
            'top_gainers': top_gainers,
            'top_losers': top_losers,
            'last_updated': to_nepal_time().isoformat()
        })