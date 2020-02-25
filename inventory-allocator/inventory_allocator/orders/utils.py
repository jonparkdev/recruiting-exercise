import numpy as np
from rest_framework.response import Response
from rest_framework import status
# File for helper functions

# calculate distance in km between two coordinates
def calculate_distance(warehouse, home):
    R = 6371  # Radius of earth in km
    home_lat = home[0]
    home_lng = home[1]
    warehouse_lat = warehouse[0]
    warehouse_lng = warehouse[1]

    # Equirectangular approximation
    x = (abs(warehouse_lat - home_lat) * R * np.pi) / 180;
    y = (abs(warehouse_lng - home_lng) *
         np.cos(((warehouse_lat - home_lat) * np.pi) / 360) *
         R *
         np.pi /
         180
        )

    return round(np.hypot(x, y), 2)

# function to parse data in request
def parse_order(data):
    # Check format of data in request
    PARAMS = ['order', 'lat', 'lng']
    # test if data is of the write type and structure
    try:
        for key, val in data.items():
            if key in PARAMS:
                continue
            else:
                return [None, None]
    except AttributeError:
        return [None, None]

    # If no lat or lng are specified in the HTTP request then it will default
    # to Toronto
    lat = data.get('lat', 43.6532)
    lng = data.get('lng', -79.3832)
    my_coordinates =  [lat, lng]

    order = data.get('order', None)

    # Type check data in request
    if(not isinstance(lat,float) and not isinstance(lng,float)):
        my_coordinates = None

    if(not isinstance(order, dict)):
        order = None

    # test if coordinates fall in the right range
    # latitude --> [-90, 90]
    # longitude --> [-180, 180]
    if not -90 < lat < 90 or not -180 < lng < 180:
        my_coordinates = None

    return [my_coordinates, order]
