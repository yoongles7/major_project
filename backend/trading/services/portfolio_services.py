from decimal import Decimal
from trading.models import Holding, Trade
from django.db.models import Sum, Avg

class PortfolioService:
    """Service class for complex portfolio calculations"""
    
    def __init__(self, user):
        self.user = user
        self.portfolio = user.portfolio
    
    def get_complete_portfolio_analysis(self):
        """Get comprehensive portfolio analysis"""
        holdings = Holding.objects.filter(user=self.user).select_related('stock')
        
        # Calculate metrics
        total_invested = Decimal('0.00')
        total_current = Decimal('0.00')
        sector_allocation = {}
        
        for holding in holdings:
            invested = holding.total_invested
            current = holding.quantity * holding.stock.current_price
            
            total_invested += invested
            total_current += current
            
            # Sector allocation
            sector = holding.stock.sector or 'Other'
            if sector not in sector_allocation:
                sector_allocation[sector] = Decimal('0.00')
            sector_allocation[sector] += current
        
        # Calculate returns
        total_profit_loss = total_current - total_invested
        if total_invested > 0:
            return_percentage = (total_profit_loss / total_invested) * 100
        else:
            return_percentage = Decimal('0.00')
        
        # Calculate risk metrics
        risk_score = self.calculate_risk_score(holdings)
        
        return {
            'summary': {
                'total_invested': float(total_invested),
                'total_current_value': float(total_current),
                'total_profit_loss': float(total_profit_loss),
                'return_percentage': float(return_percentage),
                'cash_balance': float(self.portfolio.cash_balance),
                'total_portfolio_value': float(self.portfolio.cash_balance + total_current),
                'number_of_holdings': holdings.count(),
                'risk_score': risk_score,
            },
            'sector_allocation': {
                sector: float(value) for sector, value in sector_allocation.items()
            },
            'diversification_score': self.calculate_diversification_score(holdings)
        }
    
    def calculate_risk_score(self, holdings):
        """Calculate risk score based on portfolio composition"""
        if not holdings:
            return 0.0
        
        # Simple risk calculation based on:
        # - Number of holdings (more = less risk)
        # - Sector concentration
        # - Stock volatility (simplified)
        
        # More holdings = lower risk
        holdings_count = holdings.count()
        if holdings_count == 0:
            return 0.5
        
        # This is simplified - you can make it more sophisticated
        diversity_factor = min(holdings_count / 10, 1.0)  # Max at 10 holdings
        
        # Inverse: more diverse = lower risk
        risk_score = 1.0 - (diversity_factor * 0.5)
        
        return round(risk_score, 2)
    
    def calculate_diversification_score(self, holdings):
        """Calculate how well diversified the portfolio is"""
        if not holdings:
            return 0.0
        
        # Get unique sectors
        sectors = set(h.stock.sector for h in holdings if h.stock.sector)
        sector_count = len(sectors)
        
        # More sectors = better diversification
        if holdings.count() == 0:
            return 0.0
        
        sector_score = min(sector_count / 5, 1.0)  # Max at 5 sectors
        
        # Also check if any single holding is too large (>20% of portfolio)
        total_value = sum(h.quantity * h.stock.current_price for h in holdings)
        concentration_penalty = 0
        
        if total_value > 0:
            for holding in holdings:
                holding_value = holding.quantity * holding.stock.current_price
                percentage = holding_value / total_value
                if percentage > 0.2:  # More than 20% in one stock
                    concentration_penalty += (percentage - 0.2) * 2
        
        diversification_score = max(0, sector_score - concentration_penalty)
        return round(diversification_score, 2)
    
    def get_buy_sell_recommendations(self):
        """Generate simple buy/sell recommendations"""
        holdings = Holding.objects.filter(user=self.user).select_related('stock')
        recommendations = []
        
        for holding in holdings:
            current_price = holding.stock.current_price
            avg_price = holding.average_buy_price
            
            # Simple recommendation based on profit/loss
            if current_price > avg_price * 1.1:  # 10% profit
                recommendations.append({
                    'symbol': holding.stock.symbol,
                    'action': 'HOLD or PARTIAL SELL',
                    'reason': f'Stock is up {((current_price/avg_price)-1)*100:.1f}%. Consider taking some profits.',
                    'current_price': float(current_price),
                    'buy_price': float(avg_price)
                })
            elif current_price < avg_price * 0.9:  # 10% loss
                recommendations.append({
                    'symbol': holding.stock.symbol,
                    'action': 'HOLD or AVERAGE',
                    'reason': f'Stock is down {((1 - current_price/avg_price)*100):.1f}%. Consider averaging down if you believe in the stock.',
                    'current_price': float(current_price),
                    'buy_price': float(avg_price)
                })
        
        return recommendations