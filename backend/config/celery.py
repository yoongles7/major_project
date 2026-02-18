from celery.schedules import crontab

app.conf.beat_schedule = {
    'update-stock-prices': {
        'task': 'trading.tasks.update_stock_prices_task',
        'schedule': 60.0,  # Every 60 seconds
    },
}