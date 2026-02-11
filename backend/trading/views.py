from django.http import HttpResponse
from .models import Stock
from .serializers import StockSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


def index(request):
    return HttpResponse("Hello, This is trading UI!")

class StockListView(APIView):
    def get(self, request):
        stocks = Stock.objects.all()
        serializer = StockSerializer(stocks, many=True)
        return Response(serializer.data)