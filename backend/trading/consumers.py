import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Holding, Portfolio

class PortfolioConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        
        if not self.user.is_authenticated:
            await self.close()
        else:
            self.group_name = f'user_{self.user.id}_portfolio'
            
            # Join room group
            await self.channel_layer.group_add(
                self.group_name,
                self.channel_name
            )
            
            await self.accept()
            
            # Send initial portfolio data
            await self.send_portfolio_update()
    
    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        """Handle messages from frontend"""
        data = json.loads(text_data)
        
        if data.get('action') == 'refresh':
            await self.send_portfolio_update()
    
    async def send_portfolio_update(self):
        """Send portfolio data to frontend"""
        portfolio_data = await self.get_portfolio_data()
        
        await self.send(text_data=json.dumps({
            'type': 'portfolio_update',
            'data': portfolio_data
        }))
    
    @database_sync_to_async
    def get_portfolio_data(self):
        """Get portfolio data from database"""
        holdings = Holding.objects.filter(user=self.user)
        
        holdings_data = []
        total_value = self.user.portfolio.cash_balance
        
        for holding in holdings:
            current_value = holding.quantity * holding.stock.current_price
            total_value += current_value
            
            holdings_data.append({
                'symbol': holding.stock.symbol,
                'quantity': holding.quantity,
                'current_price': float(holding.stock.current_price),
                'current_value': float(current_value),
                'profit_loss': float(current_value - holding.total_invested)
            })
        
        return {
            'cash_balance': float(self.user.portfolio.cash_balance),
            'total_value': float(total_value),
            'holdings': holdings_data
        }