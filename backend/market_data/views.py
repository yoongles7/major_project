from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from services.nepse_client import NepseClient
import logging

logger = logging.getLogger(__name__)

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
            return Response(price_data)
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
        
        return Response({
            'symbol': symbol,
            'market_status': market_status,
            'data': chart_data,
            'data_points': len(chart_data)
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
        
        return Response({
            'summary': summary,
            'nepse_index': nepse_index,
            'top_gainers': NepseClient.get_top_gainers(5),
            'top_losers': NepseClient.get_top_losers(5)
        })