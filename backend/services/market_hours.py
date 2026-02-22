from datetime import datetime, time
import pytz

def is_market_open():
    """
    Check if NEPSE market is currently open
    NEPSE Trading Hours: Sunday-Thursday, 11:00 AM - 3:00 PM NPT
    """
    nepali_tz = pytz.timezone('Asia/Kathmandu')
    now = datetime.now(nepali_tz)
    
    # Check day of week (0=Monday, 6=Sunday)
    # NEPSE: Sunday (6) to Thursday (3)
    day = now.weekday()
    
    # Sunday (6) to Thursday (3)
    if day > 4 or day == 5:  # Friday(4) or Saturday(5)
        return False
    
    # Check time between 11:00 and 15:00
    market_open = time(11, 0)   # 11:00 AM
    market_close = time(15, 0)   # 3:00 PM
    
    return market_open <= now.time() <= market_close

def get_market_status():
    """Return detailed market status"""
    return {
        'is_open': is_market_open(),
        'current_time': datetime.now(pytz.timezone('Asia/Kathmandu')).isoformat(),
        'next_open': get_next_market_open(),
        'next_close': get_next_market_close()
    }

def get_next_market_open():
    """Calculate next market opening time"""
    # Implementation for when market will next open
    pass