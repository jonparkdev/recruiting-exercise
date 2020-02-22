"""
This script will generate 5 warehouses and 10 items into the sqlite database.
Each location will be given a randomly generated coordinates within the
boundaries of the Greater Toronto Area.  Then each item will be randomly
assorted into different warehouses
"""

from django.core.management.base import BaseCommand
from orders.models import *

import numpy as np
import math

WAREHOUSES = ['Markham', 'Toronto', 'Mississauga', 'Waterloo', 'London']
ITEMS = ['Lemon', 'Lime', 'Banana', 'Eggs', 'Bread', 'Chicken Legs',
         'New York Striploin', 'Orange', 'Potatos', 'Ground Pork']

class Command(BaseCommand):
    def handle(self, *args, **options):
        # populate Item table with objects
        for item in ITEMS:
            Item(name=item).save()
        # populate Warehouse table with objects
        for warehouse in WAREHOUSES:
            # generate random latitude and longitude for each warehouse in the
            # Greater Toronto Area
            lng = round(np.random.uniform(-79.546811, -79.212679), 6)
            lat = round(np.random.uniform(43.615780, 43.693207), 6)

            Warehouse(name=warehouse, lat=lat, lng=lng).save()

        # randomly stock each warehouse with items
        warehouse_set = Warehouse.objects.all()
        item_set = Item.objects.all()
        for warehouse in warehouse_set:
            for item in item_set:
                binary = np.random.randint(0,2)
                if (binary):
                    quantity = np.random.randint(0,11)
                    Inventory(
                        warehouse=warehouse,
                        item=item,
                        quantity=quantity
                        ).save()
