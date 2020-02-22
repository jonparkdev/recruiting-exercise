from django.shortcuts import render

from orders.models import *
from orders.serializers import *
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action, api_view

from rest_framework.permissions import AllowAny
from utils import calculate_distance


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

@api_view(['POST'])
def make_order(request):
    data = request.data
    # If no lat or lng are specified in the HTTP request then it will default
    # to toronto
    lat = data.get('lat', 43.6532)
    lng = data.get('lng', -79.3832)
    my_coordinates =  [lat, lng]

    order = data.get('order', None)
    if order is None:
        return Response({"No order was specified in the request"},
                        status=status.HTTP_400_BAD_REQUEST)

    # Calculate distance values for warehouses and sort them from closest
    # nearest to furthest.  The assumption being made here is that closer
    # warehouses are cheaper to ship from
    warehouse_set = WarehouseSerializer(Warehouse.objects.all(), many=True)
    warehouse_distances = []
    for warehouse in warehouse_set:
        warehouse_coordinates = [warehouse.get('lat'), warehouse.get('lng')]
        distance = calculate_distance(warehouse_coordinates, my_coordinates)
        warehouse_distances.append({ 'name': warehouse.name,
                                     'distance': distance })
    sorted_warehouses = sorted(warehouse_distances,
                               key: lambda i: i['distance']
                               reverse=True)

    try:
        for k, v in order.items():
            # The assumption being made in the below query is that if the item
            # does not exist in the items table, then it does not exist in a
            # warehouse. In other words the items in a warehouse is a subset of
            # the set of all items
            item = Item.objects.get(name=k)
            for warehouse in sorted_warehouses:
            
            print(k)
            print(v)
        return Response(order)
    except AttributeError:
        return Response({'The order parameter in the request should be a ' \
                         'dictionary of the form of: {<string: item>: <int: ' \
                         'quantity>}'}, status=status.HTTP_400_BAD_REQUEST)
    except Item.DoesNotExist:
        return Response({'The item in your request does not exist'},
                        status=status.HTTP_400_BAD_REQUEST)
