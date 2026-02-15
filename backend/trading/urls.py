from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("stocks/", views.StockListView.as_view(), name="stocks"),
    path("portfolio/", views.PortfolioView.as_view(), name="portfolio"),
    path("holdings/", views.HoldingsListView.as_view(), name="holdings"),
    path("buy/", views.BuyOrderView.as_view(), name="buy"),
    path("sell/", views.SellOrderView.as_view(), name="sell"),
]