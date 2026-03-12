from django.urls import path

from . import views
from .api.portfolio_views import (
    PortfolioDashboardView, PortfolioPerformanceView,
    HoldingDetailView
)

urlpatterns = [
    path("", views.index, name="index"),
    path("stocks/", views.StockListView.as_view(), name="stocks"),
    path("portfolio/", views.PortfolioView.as_view(), name="portfolio"),
    path("holdings/", views.HoldingsListView.as_view(), name="holdings"),
    path("buy/", views.BuyOrderView.as_view(), name="buy"),
    path("sell/", views.SellOrderView.as_view(), name="sell"),
    path("history/", views.TradeHistoryView.as_view(), name="trading_istory"),
    path("dashboard/", views.DashboardSummaryView.as_view(), name="dashboard_summary"),
    path("stocks/<str:symbol>/", views.CurrentPriceView.as_view(), name="current-price"),
    
    path('portfolio/dashboard/', PortfolioDashboardView.as_view(), name='portfolio-dashboard'),
    path('portfolio/performance/', PortfolioPerformanceView.as_view(), name='portfolio-performance'),
    path('holdings/<str:symbol>/', HoldingDetailView.as_view(), name='holding-detail'),
]