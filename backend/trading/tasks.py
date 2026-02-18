from celery import shared_task
from services.price_updater import update_all_prices
from services.market_hours import is_market_open
import logging

logger = logging.getLogger(__name__)

@shared_task
def update_stock_prices_task():
    """Celery task to update stock prices"""
    
    # Optional: Only update during market hours
    # if not is_market_open():
    #     logger.info("Market closed, skipping update")
    #     return
    
    count = update_all_prices()
    return f"Updated {count} stocks"