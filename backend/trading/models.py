from django.db import models

class Stock(models.Model):
    symbol = models.CharField(max_length=10, unique=True)  # E.g., 'NIC', 'NMB'
    name = models.CharField(max_length=200)
    current_price = models.DecimalField(max_digits=10, decimal_places=2)
    sector = models.CharField(max_length=100, blank=True)
    last_updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.symbol} - {self.name}"