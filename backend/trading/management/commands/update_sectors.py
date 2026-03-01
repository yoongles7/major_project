from django.core.management.base import BaseCommand
from trading.models import Stock
import requests
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Update stock sectors from NEPSE CompanyList API'
    
    def handle(self, *args, **options):
        self.stdout.write("Fetching company list from NEPSE API...")
        
        # Get company list which HAS sector information
        try:
            response = requests.get(
                "http://localhost:8000/CompanyList",
                timeout=10
            )
            
            if response.status_code != 200:
                self.stdout.write(self.style.ERROR(f"API returned {response.status_code}"))
                return
            
            companies = response.json()
            self.stdout.write(f"Got {len(companies)} companies from API")
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Failed to fetch companies: {e}"))
            return
        
        # Build sector map
        sector_map = {}
        for company in companies:
            symbol = company.get('symbol')
            sector = company.get('sectorName')
            
            if symbol and sector:
                sector_map[symbol] = sector
        
        self.stdout.write(f"Found sector info for {len(sector_map)} companies")
        
        # Update stocks
        updated = 0
        skipped = 0
        
        for symbol, sector in sector_map.items():
            try:
                stock = Stock.objects.get(symbol=symbol)
                if stock.sector != sector:
                    stock.sector = sector
                    stock.save()
                    updated += 1
                    self.stdout.write(f"✓ {symbol}: {sector}")
            except Stock.DoesNotExist:
                skipped += 1
                continue
        
        self.stdout.write(self.style.SUCCESS(
            f"\n✅ Updated sectors for {updated} stocks"
        ))
        self.stdout.write(f"Stocks not found in database: {skipped}")
        
        # Show remaining unknown stocks
        unknown_count = Stock.objects.filter(sector='Unknown').count()
        self.stdout.write(f"Stocks still Unknown: {unknown_count}")
        
        # Show sample of unknown stocks
        if unknown_count > 0:
            self.stdout.write("\nSample of stocks still Unknown:")
            for stock in Stock.objects.filter(sector='Unknown')[:10]:
                self.stdout.write(f"  {stock.symbol}: {stock.name}")