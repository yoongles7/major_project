from django.http import HttpResponse
from django.db import transaction
from django.utils import timezone
from .models import Stock, Portfolio, Trade, Holding
from .serializers import StockSerializer, PortfolioSerializer, TradeSerializer, HoldingSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from decimal import Decimal
from .utils import update_holdings_after_buy, can_user_afford, validate_buy_order

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
    Get user's current holdings with real-time values
    GET /api/trading/holdings/
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        holdings = Holding.objects.filter(user=user).select_related('stock')
        
        holdings_data = []
        total_stock_value = 0
        total_invested = 0
        
        for holding in holdings:
            # Update with latest price
            current_price = holding.stock.current_price
            current_value = holding.quantity * current_price
            profit_loss = current_value - holding.total_invested
            profit_loss_percent = (profit_loss / holding.total_invested * 100) if holding.total_invested > 0 else 0
            
            holdings_data.append({
                'symbol': holding.stock.symbol,
                'company_name': holding.stock.name,
                'quantity': holding.quantity,
                'average_buy_price': float(holding.average_buy_price),
                'current_price': float(current_price),
                'current_value': float(current_value),
                'total_invested': float(holding.total_invested),
                'profit_loss': float(profit_loss),
                'profit_loss_percentage': round(profit_loss_percent, 2),
                'day_change': 0,  # Will add later with NEPSE API
            })
            
            total_stock_value += current_value
            total_invested += holding.total_invested
        
        # Get cash balance from portfolio
        portfolio = user.portfolio
        cash_balance = portfolio.cash_balance
        
        # Calculate totals
        total_portfolio_value = cash_balance + total_stock_value
        total_profit_loss = total_stock_value - total_invested
        total_profit_loss_percent = (total_profit_loss / total_invested * 100) if total_invested > 0 else 0
        
        return Response({
            'holdings': holdings_data,
            'summary': {
                'cash_balance': float(cash_balance),
                'stock_value': float(total_stock_value),
                'total_portfolio_value': float(total_portfolio_value),
                'total_invested': float(total_invested),
                'total_profit_loss': float(total_profit_loss),
                'total_profit_loss_percentage': round(total_profit_loss_percent, 2),
                'number_of_holdings': len(holdings_data),
                'last_updated': timezone.now().isoformat()
            }
        })
        
# trading/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from trading.models import Stock, Trade, Portfolio, Holding
from services.nepse_client import NepseClient
from services.price_updater import update_stock_price
from services.market_hours import is_market_open
import logging

logger = logging.getLogger(__name__)

class BuyOrderView(APIView):
    """
    POST: Place a buy order
    Required data: symbol, quantity
    Uses real NEPSE API for price
    """
    permission_classes = [IsAuthenticated]
    
    @transaction.atomic  # CRITICAL: All or nothing
    def post(self, request):
        user = request.user
        
        # === STEP 1: Get and validate input ===
        symbol = request.data.get('symbol', '').upper()
        quantity_str = request.data.get('quantity', '1')
        
        # Validate presence
        if not symbol:
            return Response(
                {"error": "Stock symbol is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate quantity
        try:
            quantity = int(quantity_str)
            if quantity <= 0:
                raise ValueError
        except ValueError:
            return Response(
                {"error": "Quantity must be a positive number"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # === STEP 2: CHECK MARKET HOURS (Optional but recommended) ===
        if not is_market_open():
            return Response({
                "warning": "Market is currently closed. Order will be processed when market opens.",
                "market_hours": "NEPSE: Sunday-Thursday, 11:00 AM - 3:00 PM NPT"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # === STEP 3: GET REAL-TIME PRICE FROM NEPSE API ===
        try:
            # Try to get live price from NEPSE API
            price_data = NepseClient.get_stock_price(symbol)
            
            if price_data and price_data.get('price'):
                current_price = price_data['price']
                price_source = 'nepse_api_live'
                price_change = price_data.get('change', 0)
            else:
                # Fallback to database price
                try:
                    stock = Stock.objects.get(symbol=symbol)
                    current_price = stock.current_price
                    price_source = 'database_cache'
                    price_change = 0
                except Stock.DoesNotExist:
                    return Response({
                        "error": f"Stock with symbol '{symbol}' not found in our database",
                        "suggestion": "Please check the symbol or sync stocks first"
                    }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error fetching price for {symbol}: {e}")
            # Final fallback - use database price
            try:
                stock = Stock.objects.get(symbol=symbol)
                current_price = stock.current_price
                price_source = 'database_fallback'
                price_change = 0
            except Stock.DoesNotExist:
                return Response({
                    "error": f"Cannot get price for {symbol}. API and database both unavailable.",
                    "detail": str(e)
                }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        
        # === STEP 4: GET OR CREATE STOCK IN DATABASE ===
        stock, created = Stock.objects.get_or_create(
            symbol=symbol,
            defaults={
                'name': f'{symbol} (NEPSE Stock)',
                'current_price': current_price,
                'sector': 'Unknown'
            }
        )
        
        # Update stock price if we got fresh data
        if price_source != 'database_cache':
            stock.current_price = current_price
            stock.save()
        
        # === STEP 5: Calculate cost and check balance ===
        total_cost = current_price * quantity
        
        # Get user's portfolio (created automatically via signal)
        portfolio = user.portfolio
        
        if portfolio.cash_balance < total_cost:
            return Response({
                "error": "Insufficient balance",
                "required": float(total_cost),
                "available": float(portfolio.cash_balance),
                "short_by": float(total_cost - portfolio.cash_balance)
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # === STEP 6: Execute the buy order (ALL DATABASE UPDATES INSIDE TRANSACTION) ===
        try:
            # 6.1 Create trade record
            trade = Trade.objects.create(
                user=user,
                stock=stock,
                quantity=quantity,
                price_per_share=current_price,
                order_type=Trade.OrderType.BUY,
                total_amount=total_cost,
                price_source=price_source  # Add this field to Trade model
            )
            
            # 6.2 Update portfolio cash balance
            portfolio.cash_balance -= total_cost
            portfolio.save()
            
            # 6.3 Update holdings (CREATE or UPDATE)
            holding, is_new_holding = self.update_holdings_after_buy(
                user=user,
                stock=stock,
                quantity=quantity,
                price_per_share=current_price
            )
            
            # === STEP 7: Calculate updated portfolio summary ===
            total_invested = self.calculate_total_invested(user)
            total_current_value = self.calculate_current_portfolio_value(user)
            
            # === STEP 8: Prepare success response ===
            response_data = {
                "success": True,
                "message": f"Successfully bought {quantity} shares of {symbol}",
                "price_info": {
                    "price_per_share": float(current_price),
                    "total_cost": float(total_cost),
                    "price_source": price_source,
                    "price_change_percent": price_change,
                    "timestamp": trade.timestamp.isoformat()
                },
                "trade_details": {
                    "trade_id": trade.id,
                    "symbol": symbol,
                    "quantity": quantity,
                    "order_type": "BUY"
                },
                "portfolio_update": {
                    "new_balance": float(portfolio.cash_balance),
                    "total_invested": float(total_invested),
                    "total_portfolio_value": float(total_current_value),
                    "total_profit_loss": float(total_current_value - total_invested)
                },
                "holding_update": {
                    "is_new_holding": is_new_holding,
                    "total_shares_owned": holding.quantity,
                    "average_price": float(holding.average_buy_price),
                    "current_value": float(holding.quantity * current_price),
                    "unrealized_profit_loss": float(
                        (holding.quantity * current_price) - holding.total_invested
                    )
                }
            }
            
            # Add warning if price came from cache
            if price_source in ['database_cache', 'database_fallback']:
                response_data["warning"] = "Price may be delayed. Using last known price from database."
            
            return Response(response_data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            # If anything fails, the transaction rolls back automatically
            logger.error(f"Buy order failed for user {user.id}, stock {symbol}: {str(e)}")
            return Response({
                "error": "Trade failed due to server error",
                "detail": str(e) if settings.DEBUG else "Please try again later"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def update_holdings_after_buy(self, user, stock, quantity, price_per_share):
        """
        Helper method to update holdings after a buy order
        Returns: (holding_object, is_new_holding)
        """
        total_cost = price_per_share * quantity
        
        try:
            # Try to get existing holding
            holding = Holding.objects.get(user=user, stock=stock)
            
            # Calculate new average price
            new_quantity = holding.quantity + quantity
            new_total_invested = holding.total_invested + total_cost
            new_avg_price = new_total_invested / new_quantity
            
            # Update holding
            holding.quantity = new_quantity
            holding.average_buy_price = new_avg_price
            holding.total_invested = new_total_invested
            holding.current_value = new_quantity * stock.current_price
            holding.profit_loss = holding.current_value - new_total_invested
            holding.save()
            
            return holding, False
            
        except Holding.DoesNotExist:
            # Create new holding
            holding = Holding.objects.create(
                user=user,
                stock=stock,
                quantity=quantity,
                average_buy_price=price_per_share,
                total_invested=total_cost,
                current_value=quantity * stock.current_price,
                profit_loss=0  # Initially no profit/loss
            )
            return holding, True
    
    def calculate_total_invested(self, user):
        """Calculate total money invested across all holdings"""
        holdings = Holding.objects.filter(user=user)
        return sum(holding.total_invested for holding in holdings)
    
    def calculate_current_portfolio_value(self, user):
        """Calculate current value of all holdings + cash"""
        holdings_value = 0
        for holding in Holding.objects.filter(user=user):
            # Use current stock price
            holdings_value += holding.quantity * holding.stock.current_price
        
        return user.portfolio.cash_balance + holdings_value
class SellOrderView(APIView):
    permission_classes = [IsAuthenticated]
    
    @transaction.atomic
    def post(self, request):
        user = request.user
        symbol = request.data.get('symbol', '').upper()
        quantity = int(request.data.get('quantity', 0))
        
        # ========== VALIDATION ==========
        if quantity <= 0:
            return Response(
                {"error": "Quantity must be greater than 0"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            holding = Holding.objects.get(
                user=user, 
                stock__symbol=symbol
            )
        except Holding.DoesNotExist:
            return Response(
                {"error": f"You don't own any shares of {symbol}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if holding.quantity < quantity:
            return Response(
                {"error": f"Insufficient shares. You own {holding.quantity} shares"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # ========== GET CURRENT PRICE ==========
        stock = holding.stock
        current_price = stock.current_price
        total_value = current_price * quantity
        
        # ========== CREATE SELL TRADE ==========
        trade = Trade.objects.create(
            user=user,
            stock=stock,
            quantity=quantity,
            price_per_share=current_price,
            order_type=Trade.OrderType.SELL,
            total_amount=total_value
        )
        
        # ========== USE YOUR MODEL'S METHOD ==========
        # This is the KEY - use the method you already created!
        holding.update_after_sell(quantity, current_price)
        # Note: You don't need to update current_value or profit_loss
        # They're properties that calculate automatically!
        
        # ========== UPDATE CASH BALANCE ==========
        portfolio = user.portfolio
        portfolio.cash_balance += total_value
        portfolio.save()
        
        # ========== CHECK IF HOLDING STILL EXISTS ==========
        # After update_after_sell, holding might be deleted if quantity became 0
        try:
            # Try to get the holding again
            updated_holding = Holding.objects.get(
                user=user, 
                stock__symbol=symbol
            )
            remaining_shares = updated_holding.quantity
            new_avg_price = float(updated_holding.average_buy_price)
            new_total_invested = float(updated_holding.total_invested)
        except Holding.DoesNotExist:
            # Holding was deleted (all shares sold)
            remaining_shares = 0
            new_avg_price = 0
            new_total_invested = 0
        
        # ========== RETURN RESPONSE ==========
        return Response({
            "success": True,
            "message": f"Successfully sold {quantity} shares of {symbol}",
            "data": {
                "symbol": symbol,
                "company_name": stock.name,
                "quantity_sold": quantity,
                "price_per_share": float(current_price),
                "total_received": float(total_value),
                "remaining_balance": float(portfolio.cash_balance),
                "remaining_shares": remaining_shares,
                "new_average_price": new_avg_price,
                "total_invested_remaining": new_total_invested,
                "trade_id": trade.id,
                "timestamp": trade.timestamp.isoformat()
            }
        }, status=status.HTTP_200_OK)
        
class TradeHistoryView(APIView):
    """
    Get user's trade history
    GET /api/trading/history/
    Optional query params: ?limit=10&page=1
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        
        # Get query parameters for pagination
        limit = int(request.GET.get('limit', 50))
        page = int(request.GET.get('page', 1))
        offset = (page - 1) * limit
        
        # Get trades ordered by most recent
        trades = Trade.objects.filter(user=user)\
            .select_related('stock')\
            .order_by('-timestamp')
        
        # Apply pagination
        total_trades = trades.count()
        paginated_trades = trades[offset:offset + limit]
        
        # Serialize trade data
        trades_data = []
        for trade in paginated_trades:
            trades_data.append({
                'id': trade.id,
                'symbol': trade.stock.symbol,
                'company_name': trade.stock.name,
                'order_type': trade.order_type,
                'quantity': trade.quantity,
                'price_per_share': float(trade.price_per_share),
                'total_amount': float(trade.total_amount),
                'timestamp': trade.timestamp.isoformat(),
                'status': 'COMPLETED',  # Could add more statuses later
            })
        
        return Response({
            'trades': trades_data,
            'pagination': {
                'total': total_trades,
                'page': page,
                'limit': limit,
                'pages': (total_trades + limit - 1) // limit
            }
        })
        
class DashboardSummaryView(APIView):
    """
    Get all data needed for frontend dashboard in one call
    GET /api/trading/dashboard/
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        
        # Get portfolio basics
        portfolio = user.portfolio
        cash_balance = portfolio.cash_balance
        
        # Get holdings
        holdings = Holding.objects.filter(user=user).select_related('stock')
        
        # Calculate stock value
        stock_value = 0
        top_holding = None
        max_value = 0
        
        for holding in holdings:
            current_value = holding.quantity * holding.stock.current_price
            stock_value += current_value
            
            # Find top holding
            if current_value > max_value:
                max_value = current_value
                top_holding = {
                    'symbol': holding.stock.symbol,
                    'name': holding.stock.name,
                    'value': float(current_value),
                    'quantity': holding.quantity
                }
        
        # Get recent trades (last 5)
        recent_trades = Trade.objects.filter(user=user)\
            .select_related('stock')\
            .order_by('-timestamp')[:5]
        
        recent_trades_data = []
        for trade in recent_trades:
            recent_trades_data.append({
                'symbol': trade.stock.symbol,
                'type': trade.order_type,
                'quantity': trade.quantity,
                'amount': float(trade.total_amount),
                'time_ago': self.get_time_ago(trade.timestamp)
            })
        
        return Response({
            'portfolio': {
                'cash_balance': float(cash_balance),
                'stock_value': float(stock_value),
                'total_value': float(cash_balance + stock_value),
                'top_holding': top_holding
            },
            'recent_trades': recent_trades_data,
            'quick_stats': {
                'total_trades': Trade.objects.filter(user=user).count(),
                'holdings_count': holdings.count(),
                'today_pnl': 0,  # Will implement later
            }
        })
    
    def get_time_ago(self, timestamp):
        """Helper to format time ago"""
        from django.utils import timezone
        diff = timezone.now() - timestamp
        
        if diff.days > 0:
            return f"{diff.days}d ago"
        elif diff.seconds > 3600:
            return f"{diff.seconds // 3600}h ago"
        elif diff.seconds > 60:
            return f"{diff.seconds // 60}m ago"
        else:
            return "Just now"

class CurrentPriceView(APIView):
    """Get current price for one or multiple stocks"""
    
    def get(self, request, symbol=None):
        if symbol:
            # Single stock
            price_data = NepseClient.get_stock_price(symbol)
            if price_data:
                return Response({
                    'symbol': symbol,
                    'price': price_data['price'],
                    'change': price_data.get('change', 0)
                })
            return Response({'error': 'Not found'}, status=404)
        
        # Multiple stocks (from query params)
        symbols = request.GET.getlist('symbols[]')
        if symbols:
            prices = {}
            live_data = NepseClient.get_live_prices()
            if live_data:
                for item in live_data:
                    if item.get('symbol') in symbols:
                        prices[item['symbol']] = {
                            'price': item.get('lastTradedPrice'),
                            'change': item.get('percentChange')
                        }
            return Response(prices)
        
        # Get all prices
        live_data = NepseClient.get_live_prices()
        return Response(live_data or [])
    
class MarketStatusView(APIView):
    """Check if market is open"""
    
    def get(self, request):
        from services.market_hours import is_market_open
        import datetime
        import pytz
        
        nepali_time = datetime.datetime.now(pytz.timezone('Asia/Kathmandu'))
        
        return Response({
            'is_open': is_market_open(),
            'current_time': nepali_time.isoformat(),
            'market_hours': 'Sunday-Thursday, 11:00 AM - 3:00 PM NPT'
        })