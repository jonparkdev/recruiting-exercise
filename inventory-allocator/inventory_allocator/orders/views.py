from django.shortcuts import render

from orders.models import *
from orders.serializers import *
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action, api_view

from rest_framework.permissions import AllowAny
# Create your views here.


class WarehouseViewSet(viewsets.ModelViewSet):
    queryset = Warehouse.objects.all()
    serializer_class = WarehouseSerializer
    permission_classes = [AllowAny]


class ItemsViewSet(viewsets.ModelViewSet):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    permission_classes = [AllowAny]


class InventoryViewSet(viewsets.ModelViewSet):
    queryset = Inventory.objects.all()
    serializer_class = InventorySerializer
    permission_classes = [AllowAny]


@api_view(['GET'])
def get_warehouse_inventory(request):
    query = request.query_params
    location = query.get('location', None)
    if location is None:
        queryset = Warehouse.objects.all()
        serialized = WarehouseInventorySerializer(queryset, many=True).data
        return Response(serialized)
    else:
        try:
            queryset = Warehouse.objects.get(name=location)
            serialized = WarehouseInventorySerializer(queryset).data
            return Response(serialized)
        except Exception:
            return Response({"This warehouse location does not exist"}, status=status.HTTP_400_BAD_REQUEST)
