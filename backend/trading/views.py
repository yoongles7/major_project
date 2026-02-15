from django.http import HttpResponse
from django.db import transaction
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