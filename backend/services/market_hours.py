# services/market_hours.py
from datetime import datetime, time
import pytz

def is_market_open():
    """
    Check if NEPSE market is currently open
    NEPSE Trading Hours: Sunday-Thursday, 11:00 AM - 3:00 PM NPT
    """
    nepali_tz = pytz.timezone('Asia/Kathmandu')
    now = datetime.now(nepali_tz)
    
    # Get day of week (0=Monday, 1=Tuesday, 2=Wednesday, 3=Thursday, 4=Friday, 5=Saturday, 6=Sunday)
    day = now.weekday()
    
    # DEBUG: Print current info
    print(f"Debug - Current time: {now}")
    print(f"Debug - Day number: {day} (0=Mon, 6=Sun)")
    
    # NEPSE is open: Sunday (6) to Thursday (3)
    # Sunday = 6, Monday = 0, Tuesday = 1, Wednesday = 2, Thursday = 3
    # So open days are: 6, 0, 1, 2, 3
    
    # Check if it's a weekend (Friday or Saturday)
    if day == 4 or day == 5:  # Friday(4) or Saturday(5)
        print(f"Debug - Weekend: {day}")
        return False
    
    # Check time between 11:00 and 15:00
    market_open = time(11, 0)   # 11:00 AM
    market_close = time(15, 0)  # 3:00 PM
    
    current_time = now.time()
    is_open_time = market_open <= current_time <= market_close
    
    print(f"Debug - Time check: {market_open} <= {current_time} <= {market_close} = {is_open_time}")
    
    return is_open_time

def get_market_status():
    """Return detailed market status"""
    from datetime import datetime
    import pytz
    
    nepali_tz = pytz.timezone('Asia/Kathmandu')
    now = datetime.now(nepali_tz)
    
    return {
        'is_open': is_market_open(),
        'current_time': now.isoformat(),
        'market_hours': 'Sunday-Thursday, 11:00 AM - 3:00 PM NPT',
        'current_day': now.strftime('%A'),  # Add day name for debugging
        'current_time_str': now.strftime('%H:%M:%S')
    }