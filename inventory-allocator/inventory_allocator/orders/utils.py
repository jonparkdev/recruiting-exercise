import numpy as np
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

    return [my_coordinates, order]
