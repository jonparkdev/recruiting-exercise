from django.shortcuts import render

from orders.models import *
from orders.serializers import *
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action, api_view

from rest_framework.permissions import AllowAny
from orders.utils import calculate_distance, parse_order

import json


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
    location = query.get('warehouse', None)
    if len(query) > 1 or location is None and len(query) == 1:
        return Response({'Invalid query parameters'},
            status.HTTP_400_BAD_REQUEST)
    elif location is not None:
        try:
            queryset = Warehouse.objects.get(name=location)
            serialized = WarehouseInventorySerializer(queryset).data
            return Response(serialized)
        except Exception:
            return Response({"This warehouse location does not exist"},
                status=status.HTTP_400_BAD_REQUEST)
    else:
        queryset = Warehouse.objects.all()
        serialized = WarehouseInventorySerializer(queryset, many=True).data
        return Response(serialized)




@api_view(['POST'])
def make_order(request):
    # type checking
    my_coordinates, order = parse_order(request.data)

    if order is None:
        return Response({'No order was specified or invalid format or data ' \
                         'in the request'},
                        status=status.HTTP_400_BAD_REQUEST)

    if my_coordinates is None:
        return Response({'Please check the structure of coordinates and the ' \
                         'range of both latitude and longitude'},
                        status=status.HTTP_400_BAD_REQUEST)


    # Calculate distance values for warehouses and sort them from
    # nearest to furthest.  The assumption being made here is that closer
    # warehouses are cheaper to ship from
    warehouse_set = Warehouse.objects.all()
    warehouse_distances = []
    for warehouse in warehouse_set:
        serialized = WarehouseSerializer(warehouse).data
        # lat and lng are stored as str in the db
        warehouse_coordinates = [float(serialized.get('lat')),
                                 float(serialized.get('lng'))]
        distance = calculate_distance(warehouse_coordinates, my_coordinates)
        warehouse_distances.append({ 'name': warehouse.name,
                                     'distance': distance })
    sorted_warehouses = sorted(warehouse_distances,
                               key= lambda i: i['distance'],
                               )

    try:
        # keep track of successful item/warehouse hits in order
        track_stock = {}
        # keep track of database changes
        database_changes = []

        for k, v in order.items():
            # Keep count of how many k's needed for the order
            if isinstance(v, int) and v > 0:
                order_count = v
            else:
                return Response({'Please input a valid number greater than' \
                                 ' 0 for all items in the order '},
                                 status.HTTP_400_BAD_REQUEST)

            # The assumption being made in the below query is that if the item
            # does not exist in the db's items table, then it does not exist in
            # a warehouse.In other words,the items in a warehouse are a subset
            # of the set of all items
            item_object = Item.objects.get(name=k)

            # Loop every warehouse for item k. If found, break loop and move to
            # next item
            for warehouse in sorted_warehouses:
                warehouse_object = Warehouse.objects.get(name=warehouse['name'])
                try:
                    # check if item exist in warehouse
                    inventory_object = Inventory.objects.get(
                        warehouse=warehouse_object,
                        item=item_object
                        )
                    # get quantity of stock in warehouse
                    inventory_stock = inventory_object.quantity
                    if(inventory_stock == 0):
                        continue
                    elif(inventory_stock < order_count):
                        try:
                            track_stock[warehouse['name']][k] = inventory_stock
                        except KeyError:
                            track_stock[warehouse['name']] = { k: inventory_stock }
                        order_count = order_count - inventory_stock
                        database_changes.append((inventory_object,
                                                { 'quantity': 0}))
                    else:
                        try:
                            track_stock[warehouse['name']][k] = order_count
                        except KeyError:
                            track_stock[warehouse['name']] = { k : order_count }
                        database_changes.append(
                            (inventory_object,
                            { 'quantity': inventory_stock - order_count}))
                        order_count = 0
                        break

                except Inventory.DoesNotExist:
                    pass

            # If none of the warehouses have stock on item, return empty array
            if (order_count != 0):
                return Response([])

        # Make database changes to inventory
        for inventory, quantity in database_changes:
            update_inventory = InventorySerializer(
                inventory, data=quantity, partial=True)
            update_inventory.is_valid()
            update_inventory.save()

        # configure data for output
        response = [ { k: v } for k, v in track_stock.items() ]
        return Response(response)

    except AttributeError:
        return Response({'The order parameter in the request should be a ' \
                         'dictionary of the form of: {<string: item>: <int: ' \
                         'quantity>}'}, status=status.HTTP_400_BAD_REQUEST)
    except Item.DoesNotExist:
        return Response({'The item in your request either does not exist ' \
                         'or has an error.  Note that requests are case ' \
                         'sensitive'},
                        status=status.HTTP_400_BAD_REQUEST)
