from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.db.models import Sum, Avg, Count
from decimal import Decimal
from trading.models import Holding, Trade, Stock
from trading.serializers import HoldingSerializer, TradeSerializer

class PortfolioDashboardView(APIView):
    """
    Complete portfolio dashboard data
    Returns everything frontend needs for the main dashboard
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        portfolio = user.portfolio
        
        # Get all holdings with current values
        holdings = Holding.objects.filter(user=user)
        holdings_data = []
        sector_breakdown = {}
        
        for holding in holdings:
            # Update with current stock price
            holding_data = {
                'symbol': holding.stock.symbol,
                'company_name': holding.stock.name,
                'quantity': holding.quantity,
                'avg_price': float(holding.average_buy_price),
                'current_price': float(holding.stock.current_price),
                'current_value': float(holding.quantity * holding.stock.current_price),
                'invested': float(holding.total_invested),
                'profit_loss': float(
                    (holding.quantity * holding.stock.current_price) - 
                    holding.total_invested
                ),
                'sector': holding.stock.sector or 'Other'
            }
            
            # Calculate percentage
            if holding_data['invested'] > 0:
                holding_data['profit_loss_percentage'] = round(
                    (holding_data['profit_loss'] / holding_data['invested']) * 100, 2
                )
            else:
                holding_data['profit_loss_percentage'] = 0
            
            holdings_data.append(holding_data)
            
            # Build sector breakdown
            sector = holding_data['sector']
            if sector not in sector_breakdown:
                sector_breakdown[sector] = 0
            sector_breakdown[sector] += holding_data['current_value']
        
        # Calculate portfolio totals
        total_stock_value = sum(h['current_value'] for h in holdings_data)
        total_invested = sum(h['invested'] for h in holdings_data)
        total_profit_loss = total_stock_value - total_invested
        
        # Get recent trades
        recent_trades = Trade.objects.filter(user=user).order_by('-timestamp')[:10]
        trades_data = []
        for trade in recent_trades:
            trades_data.append({
                'id': trade.id,
                'symbol': trade.stock.symbol,
                'company': trade.stock.name,
                'type': trade.order_type,
                'quantity': trade.quantity,
                'price': float(trade.price_per_share),
                'total': float(trade.total_amount),
                'date': trade.timestamp.isoformat()
            })
        
        # Get top performing stocks
        sorted_holdings = sorted(
            holdings_data, 
            key=lambda x: x['profit_loss_percentage'], 
            reverse=True
        )
        top_performers = sorted_holdings[:3] if sorted_holdings else []
        worst_performers = sorted_holdings[-3:] if len(sorted_holdings) > 3 else []
        
        # Prepare response
        response_data = {
            'summary': {
                'cash_balance': float(portfolio.cash_balance),
                'total_invested': float(total_invested),
                'total_stock_value': float(total_stock_value),
                'total_portfolio_value': float(portfolio.cash_balance) + float(total_stock_value),
                'total_profit_loss': float(total_profit_loss),
                'profit_loss_percentage': round(
                    (total_profit_loss / total_invested * 100) if total_invested > 0 else 0, 2
                ),
                'holdings_count': len(holdings_data),
                'total_trades': Trade.objects.filter(user=user).count(),
                'diversification_score': len(holdings_data)  # Simple version
            },
            'holdings': holdings_data,
            'recent_trades': trades_data,
            'top_performers': top_performers,
            'worst_performers': worst_performers,
            'sector_breakdown': [
                {'sector': k, 'value': v} for k, v in sector_breakdown.items()
            ],
            'charts': {
                'portfolio_growth': [],  # Will add later
                'sector_allocation': list(sector_breakdown.values())
            }
        }
        
        return Response(response_data)


class PortfolioPerformanceView(APIView):
    """
    Historical performance data for charts
    Shows portfolio value over time
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        days = int(request.query_params.get('days', 30))
        
        # Get trades for the period
        from datetime import datetime, timedelta
        start_date = datetime.now() - timedelta(days=days)
        
        trades = Trade.objects.filter(
            user=user, 
            timestamp__gte=start_date
        ).order_by('timestamp')
        
        # Build timeline data
        timeline = []
        current_date = start_date
        end_date = datetime.now()
        
        # This is simplified - you might want to calculate actual portfolio value
        # on each day based on trades and stock prices
        balance = user.portfolio.cash_balance
        
        # Group trades by date
        from collections import defaultdict
        daily_trades = defaultdict(list)
        for trade in trades:
            date_key = trade.timestamp.date()
            daily_trades[date_key].append(trade)
        
        # Calculate daily portfolio value
        for i in range(days):
            date = start_date + timedelta(days=i)
            date_key = date.date()
            
            # Get trades for this day
            day_trades = daily_trades.get(date_key, [])
            
            # This is a simplified calculation
            # In reality, you'd need stock prices for each day
            day_value = float(user.portfolio.cash_balance)  # Simplified
            
            timeline.append({
                'date': date.isoformat(),
                'value': day_value
            })
        
        return Response({
            'timeline': timeline,
            'period': f"{days}_days"
        })


class HoldingDetailView(APIView):
    """
    Detailed view for a single holding
    Shows trade history and performance metrics
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, symbol):
        user = request.user
        
        try:
            stock = Stock.objects.get(symbol=symbol.upper())
            holding = Holding.objects.get(user=user, stock=stock)
        except (Stock.DoesNotExist, Holding.DoesNotExist):
            return Response(
                {"error": "You don't own this stock"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get all trades for this stock
        trades = Trade.objects.filter(
            user=user, 
            stock=stock
        ).order_by('-timestamp')
        
        trades_data = []
        for trade in trades:
            trades_data.append({
                'date': trade.timestamp.isoformat(),
                'type': trade.order_type,
                'quantity': trade.quantity,
                'price': float(trade.price_per_share),
                'total': float(trade.total_amount)
            })
        
        # Calculate buy/sell summary
        buy_trades = trades.filter(order_type='BUY')
        sell_trades = trades.filter(order_type='SELL')
        
        response_data = {
            'symbol': stock.symbol,
            'company_name': stock.name,
            'sector': stock.sector,
            'current_price': float(stock.current_price),
            'holdings': {
                'quantity': holding.quantity,
                'average_buy_price': float(holding.average_buy_price),
                'total_invested': float(holding.total_invested),
                'current_value': float(holding.quantity * stock.current_price),
                'profit_loss': float(
                    (holding.quantity * stock.current_price) - holding.total_invested
                ),
                'profit_loss_percentage': round(
                    ((holding.quantity * stock.current_price) - holding.total_invested) /
                    holding.total_invested * 100 if holding.total_invested > 0 else 0, 2
                )
            },
            'trade_summary': {
                'total_buys': buy_trades.count(),
                'total_buy_value': float(buy_trades.aggregate(Sum('total_amount'))['total_amount__sum'] or 0),
                'total_sells': sell_trades.count(),
                'total_sell_value': float(sell_trades.aggregate(Sum('total_amount'))['total_amount__sum'] or 0),
                'net_cash_flow': float(
                    (sell_trades.aggregate(Sum('total_amount'))['total_amount__sum'] or 0) -
                    (buy_trades.aggregate(Sum('total_amount'))['total_amount__sum'] or 0)
                )
            },
            'recent_trades': trades_data[:10]
        }
        
        return Response(response_data)