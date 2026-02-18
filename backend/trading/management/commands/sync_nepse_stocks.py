from django.core.management.base import BaseCommand
from trading.models import Stock
from services.nepse_client import NepseClient

class Command(BaseCommand):
    help = 'Sync stocks from NEPSE API to database'
    
    def handle(self, *args, **kwargs):
        self.stdout.write("Fetching stocks from NEPSE...")
        
        # Get stock list from API
        stocks_data = NepseClient.get_stock_list()
        
        if not stocks_data:
            self.stdout.write(self.style.ERROR("Failed to fetch stocks"))
            return
        
        # Counter for stats
        created = 0
        updated = 0
        
        for item in stocks_data:
            symbol = item.get('symbol')
            name = item.get('companyName', '')
            
            if not symbol:
                continue
            
            # Update or create
            stock, is_new = Stock.objects.update_or_create(
                symbol=symbol,
                defaults={
                    'name': name,
                    'current_price': item.get('lastTradedPrice', 0),
                    'sector': item.get('sectorName', '')
                }
            )
            
            if is_new:
                created += 1
            else:
                updated += 1
        
        self.stdout.write(
            self.style.SUCCESS(
                f"Done! Created: {created}, Updated: {updated}"
            )
        )