from django.urls import path
from . import views

urlpatterns = [
    path('status/', views.MarketStatusView.as_view(), name='market-status'),
    path('prices/', views.LivePricesView.as_view(), name='live-prices'),
    path('price/<str:symbol>/', views.StockPriceView.as_view(), name='stock-price'),
    path('intraday/', views.IntradayChartView.as_view(), name='intraday-chart'),
    path('search/', views.StockSearchView.as_view(), name='stock-search'),
    path('summary/', views.MarketSummaryView.as_view(), name='market-summary'),
]