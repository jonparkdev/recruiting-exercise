from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITransactionTestCase
from orders.models import *
from orders.views import *
import json

class InventoryTests(APITransactionTestCase):

    fixtures = ['db_dump']
    def setUp(self):
        self.warehouse_set = Warehouse.objects.all()
        self.warehouse = Warehouse.objects.get(name="London")


    def test_endpoint(self):
        url=reverse('stock')

        # test if endpoint functions properly
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # test if data returned is correct in reference to the database
        response_with_correct_query  = self.client.get(
            url, {'warehouse': 'London'})
        self.assertEqual(response_with_correct_query.data["name"], "London")
        response_data = {
            "Lemon":1,"Eggs":5,"Chicken Legs":5,"Orange":5,"Potatos":0
         }
        self.assertEqual(response_with_correct_query.data["items"], response_data)

        # Bad Requests
        response_with_invalid_warehouse  = self.client.get(
            url, {'warehouse': 'Lndon'})
        self.assertEqual(response_with_invalid_warehouse.status_code,
            status.HTTP_400_BAD_REQUEST)
        response_with_incorrect_query_param = self.client.get(
            url, {'warehoue': 'London'})
        self.assertEqual(response_with_incorrect_query_param.status_code,
            status.HTTP_400_BAD_REQUEST)
        response_with_incorrect_query_parameters = self.client.get(
            url, {'warehouse': 'London', 'something': 'random'})
        self.assertEqual(response_with_incorrect_query_parameters.status_code,
            status.HTTP_400_BAD_REQUEST)


class OrderTests(APITransactionTestCase):

    fixtures = ['db_dump']

    """
    Test the formating of the request, that is type checking and structure of
    the data parameter in the POST request
    """



    """
    Test correctness of response and side effects on database entries
    """
    def test_correctness(self):
        url_order = reverse('order')
        url_stock = reverse('stock')

        """
        The below test will simulate an order to the API
        """
        data = {
        "order":
            {
            "Chicken Legs": 1,
            "New York Striploin": 1,
            "Eggs": 1,
            "Orange":1,
            "Banana": 1
            }
        }
        data_solution = [
            {
                'Toronto': {'Chicken Legs': 1, 'Orange': 1, 'Banana': 1}
            },
            {
                'Waterloo': {'New York Striploin': 1}
            },
            {
                'Mississauga':{'Eggs': 1}
            },
        ]

        mississauga_stock_before = {
                'name': 'Mississauga',
                'items': {'Lemon': 0, 'Lime': 0, 'Banana': 8, 'Eggs': 4}
        }

        mississauga_stock_first_order = {
                'name': 'Mississauga',
                'items': {'Lemon': 0, 'Lime': 0, 'Banana': 8, 'Eggs': 3}
        }

        # first check Mississauga stock
        response_get_stock_before  = self.client.get(
            url_stock, {'warehouse': 'Mississauga'})
        self.assertEqual(response_get_stock_before.status_code,
            status.HTTP_200_OK)
        self.assertEqual(response_get_stock_before.data, mississauga_stock_before)

        # make an order
        response_order_without_location = self.client.post(url_order, data, format='json')
        self.assertEqual(response_order_without_location.status_code, status.HTTP_200_OK)
        self.assertEqual(response_order_without_location.data, data_solution)

        # Check Mississauga stock again. There should be one less Egg
        response_get_stock_after  = self.client.get(
            url_stock, {'warehouse': 'Mississauga'})
        self.assertEqual(response_get_stock_after.status_code,
            status.HTTP_200_OK)
        self.assertEqual(response_get_stock_after.data,
            mississauga_stock_first_order)

        """
        This test demonstrates location sorting if coordinates are provided in
        request
        """

        # coordinates are for London warehouse
        data_with_location = {
            'order':
                {
                "Chicken Legs": 1,
                "New York Striploin": 1,
                "Eggs": 1,
                "Orange":1,
                "Banana": 1,
                "Lemon": 3 # Lemon will be fulfilled by two warehouses
                },
            "lat": 42.9849,
            "lng": -81.2453,

        }

        mississauga_stock_second_order = {
                'name': 'Mississauga',
                'items': {'Lemon': 0, 'Lime': 0, 'Banana': 7, 'Eggs': 3}
        }

        data_with_location_solution = [
            {
                'London': {
                    'Lemon': 1, 'Chicken Legs': 1, 'Eggs': 1, 'Orange': 1}
                },
            {
                'Waterloo': {'New York Striploin': 1}
            },
            {
                'Mississauga': {'Banana': 1}
            },
            {
                'Toronto': {'Lemon':2}
            }
        ]
        # make order, notice the order was fulfilled by London, Waterloo and
        # Mississauga warehouses
        response_order_with_location = self.client.post(
            url_order, data_with_location, format='json')
        self.assertEqual(response_order_with_location.status_code,
            status.HTTP_200_OK)
        self.assertEqual(response_order_with_location.data,
            data_with_location_solution)

        # Check Mississauga stock again
        response_get_stock_after  = self.client.get(
            url_stock, {'warehouse': 'Mississauga'})
        self.assertEqual(response_get_stock_after.status_code,
            status.HTTP_200_OK)
        self.assertEqual(response_get_stock_after.data,
            mississauga_stock_second_order)


        """
        Test unfulfilled orders
        """
        # Not enough stock
        response_out_of_stock = self.client.post(
            url_order, {"order": {"Lemon": 50}}, format='json')
        self.assertEqual(response_out_of_stock.status_code, status.HTTP_200_OK)
        self.assertEqual(response_out_of_stock.data, [])


        """
        Error Testing
        """
        # Item does not exist
        error_1 =  self.client.post(
            url_order, {"order": {"avacado": 1}}, format='json')
        self.assertEqual(error_1.status_code, status.HTTP_400_BAD_REQUEST)

        # Item does not exist with item that exists
        error_9 =  self.client.post(
            url_order, {"order": {"Lemon": 1, "avacado": 1}}, format='json')
        self.assertEqual(error_9.status_code, status.HTTP_400_BAD_REQUEST)

        # Bad Input tests
        error_6 =  self.client.post(
            url_order, {"order": {"Lemon": 50}, "something": "else"},
                format='json')
        self.assertEqual(error_6.status_code, status.HTTP_400_BAD_REQUEST)

        error_2 =  self.client.post(
            url_order, {}, format='json')
        self.assertEqual(error_2.status_code, status.HTTP_400_BAD_REQUEST)

        # type checking
        # string
        error_3 =  self.client.post(
            url_order, "string", format='json')
        self.assertEqual(error_3.status_code, status.HTTP_400_BAD_REQUEST)
        # list
        error_4 =  self.client.post(
            url_order, [{"order": {"avacado": 1}}], format='json')
        self.assertEqual(error_4.status_code, status.HTTP_400_BAD_REQUEST)
        # int
        error_5 =  self.client.post(
            url_order, 42, format='json')
        self.assertEqual(error_5.status_code, status.HTTP_400_BAD_REQUEST)

        # negative numbers
        error_7 =  self.client.post(
            url_order,{"order": {"Lemon": -4}}, format='json')
        self.assertEqual(error_7.status_code, status.HTTP_400_BAD_REQUEST)

        # zero
        error_8 =  self.client.post(
             url_order, {"order": {"Lemon": 0}}, format='json')
        self.assertEqual(error_8.status_code, status.HTTP_400_BAD_REQUEST)

        # Wrong key values
        error_10 =  self.client.post(
             url_order, {"order": {"Lemon": 1}, 'latitd': 40.00, 'long': -90.00}
                , format='json')
        self.assertEqual(error_10.status_code, status.HTTP_400_BAD_REQUEST)

        # Invalid range for latitude and longitude lat -> [-90,90] and
        # lng -> [-180, 180]
        error_11 =  self.client.post(
             url_order, {"order": {"Lemon": 1}, 'lat': 90.10, 'lng': 290.00}
                , format='json')
        self.assertEqual(error_11.status_code, status.HTTP_400_BAD_REQUEST)

        # Coordinates withour order
        error_12 =  self.client.post(
             url_order, {'lat': 80.000, 'lng': -170.00}
                , format='json')
        self.assertEqual(error_12.status_code, status.HTTP_400_BAD_REQUEST)
