from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("stocks/", views.StockListView.as_view(), name="stocks"),
]