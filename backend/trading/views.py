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
        
class BuyOrderView(APIView):
    """
    POST: Place a buy order
    Required data: symbol, quantity
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
        except ValueError:
            return Response(
                {"error": "Quantity must be a number"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # === STEP 2: Validate stock exists ===
        try:
            stock = Stock.objects.get(symbol=symbol)
        except Stock.DoesNotExist:
            return Response(
                {"error": f"Stock with symbol '{symbol}' not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # === STEP 3: Validate order parameters ===
        validation_errors = validate_buy_order(stock, quantity)
        if validation_errors:
            return Response(
                {"errors": validation_errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # === STEP 4: Calculate cost and check balance ===
        current_price = stock.current_price
        total_cost = current_price * quantity
        
        # Get user's portfolio (created automatically via signal)
        portfolio = user.portfolio
        
        if not can_user_afford(user, total_cost):
            return Response({
                "error": "Insufficient balance",
                "required": float(total_cost),
                "available": float(portfolio.cash_balance)
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # === STEP 5: Execute the buy order (ALL DATABASE UPDATES INSIDE TRANSACTION) ===
        try:
            # 5.1 Create trade record
            trade = Trade.objects.create(
                user=user,
                stock=stock,
                quantity=quantity,
                price_per_share=current_price,
                order_type=Trade.OrderType.BUY,
                total_amount=total_cost
            )
            
            # 5.2 Update portfolio cash balance
            portfolio.cash_balance -= total_cost
            portfolio.save()
            
            # 5.3 Update holdings (CREATE or UPDATE)
            holding, is_new_holding = update_holdings_after_buy(
                user=user,
                stock=stock,
                quantity=quantity,
                price_per_share=current_price
            )
            
            # === STEP 6: Prepare success response ===
            response_data = {
                "success": True,
                "message": f"Successfully bought {quantity} shares of {symbol}",
                "trade_details": {
                    "trade_id": trade.id,
                    "symbol": symbol,
                    "quantity": quantity,
                    "price_per_share": float(current_price),
                    "total_cost": float(total_cost),
                    "timestamp": trade.timestamp.isoformat()
                },
                "portfolio_update": {
                    "new_balance": float(portfolio.cash_balance),
                    "total_invested": float(portfolio.cash_balance)  # You'll calculate this properly later
                },
                "holding_update": {
                    "is_new_holding": is_new_holding,
                    "total_shares_owned": holding.quantity,
                    "average_price": float(holding.average_buy_price),
                    "total_invested_in_stock": float(holding.total_invested)
                }
            }
            
            return Response(response_data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            # If anything fails, the transaction rolls back automatically
            return Response({
                "error": "Trade failed",
                "detail": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            s
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