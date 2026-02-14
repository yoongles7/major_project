from django.http import HttpResponse
from .models import Stock, Portfolio, Trade, Holding
from .serializers import StockSerializer, PortfolioSerializer, TradeSerializer, HoldingSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

def index(request):
    return HttpResponse("Hello, This is trading UI!")

class StockListView(APIView):
    def get(self, request):
        stocks = Stock.objects.all()
        serializer = StockSerializer(stocks, many=True)
        return Response(serializer.data)

class PortfolioView(APIView):
    """
    GET: Returns user's portfolio details
    Requires authentication
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        
        # Get or create portfolio (just in case)
        portfolio, created = Portfolio.objects.get_or_create(
            user=user,
            defaults={'cash_balance': 100000.00}
        )
        
        # Get user's recent trades
        recent_trades = Trade.objects.filter(user=user)[:5]  # Last 5 trades
        
        # Calculate some basic stats
        total_buys = Trade.objects.filter(user=user, order_type='BUY').count()
        total_sells = Trade.objects.filter(user=user, order_type='SELL').count()
        
        return Response({
            'portfolio': PortfolioSerializer(portfolio).data,
            'stats': {
                'total_trades': total_buys + total_sells,
                'total_buys': total_buys,
                'total_sells': total_sells,
            },
            'recent_trades': TradeSerializer(recent_trades, many=True).data
        })
        
class HoldingsListView(APIView):
    """
    GET: Get all holdings for logged-in user
    Shows what stocks user owns with current values
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        # Get all holdings for this user
        holdings = Holding.objects.filter(user=request.user)
        
        # Calculate total portfolio value
        total_portfolio_value = request.user.portfolio.cash_balance
        for holding in holdings:
            total_portfolio_value += holding.current_value
        
        # Serialize holdings
        serializer = HoldingSerializer(holdings, many=True)
        
        return Response({
            'holdings': serializer.data,
            'summary': {
                'total_holdings_count': holdings.count(),
                'total_portfolio_value': total_portfolio_value,
                'cash_balance': request.user.portfolio.cash_balance,
                'stocks_value': total_portfolio_value - request.user.portfolio.cash_balance
            }
        })