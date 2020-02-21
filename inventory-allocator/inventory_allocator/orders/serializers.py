from rest_framework import serializers
from orders.models import *



class WarehouseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Warehouse
        fields = ['name', 'lat', 'lng']


class ItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = Item
        fields = ['name']


class InventorySerializer(serializers.ModelSerializer):

    item = ItemSerializer()
    warehouse = WarehouseSerializer()

    class Meta:
        model = Inventory
        fields = ['id', 'item', 'warehouse', 'quantity']


class WarehouseInventorySerializer(serializers.ModelSerializer):
    items = serializers.SerializerMethodField(required=False, read_only=True)

    class Meta:
        model = Warehouse
        fields = ['name', 'items']

    def get_items(self, warehouse):
        inventory = Inventory.objects.filter(warehouse=warehouse)
        inventory_dict = {}
        for item in inventory:
            item_name = ItemSerializer(item.item).data['name']
            item_quantity = item.quantity
            inventory_dict[item_name] = item_quantity

        return inventory_dict
