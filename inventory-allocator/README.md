# Inventory Allocator

My solution to this recruitment challenge is a small restful API completed with the Django REST framework.  

##### Why did I chose to complete it this way? 

At my current position our backend is done with Django's ORM so I thought it would be a  good exercise to practice and reinforce the knowledge.

## Set Up

After cloning the repo, in your terminal (NOTE - I am using pipenv for my python virtual env):

```bash
$ cd recruiting-exercise/inventory-allocator/
$ pipenv --python 3
$ pipenv shell
$ pipenv install 
$ cd inventory_allocator/
$ python manage.py migrate
```

At this point you can do 1 of 2 things:

1)  Run the command:

```bash
$ python manage.py generate_data
```

Which will populate the database with warehouses and items, using randomly generated stock for each warehouse

or

2) Run the command:

```bash
$ python manage.py loaddata db_dump
```

Which is data I generated from the above option but modified to have correct latitude and longitude for each warehouse (more on that below).  I also use this fixture for my unit tests.

In reference to the coordinates, I decided to give each warehouse a location as a means to identify which warehouses are cheapest to ship from. That is, I have defined that the closer the warehouse is to the order, the cheaper the cost it is to ship.

## How to use

Run the command:

```bash
$ python manage.py test
```

to run all the unit tests.

### Endpoints

First start the server:

```bash
$ python manage.py runserver
```

The server should be running on port 8000.

The two endpoints that are important for functionality are:

```
/stock
/order
```

First to see if everything is working fine from the above 'Set Up', you can run the shell command:

```bash
$ curl  http://localhost:8000/stock
```

The response will return a  list of warehouses and their stock of each item. The database is populated with the following items: 

```python
WAREHOUSES = ['Markham', 'Toronto', 'Mississauga', 'Waterloo', 'London']
ITEMS = ['Lemon', 'Lime', 'Banana', 'Eggs', 'Bread', 'Chicken Legs',
         'New York Striploin', 'Orange', 'Potatos', 'Ground Pork']
```

Also try,

```bash
$ curl http://localhost:8000/stock?warehouse='Markham'
```

You can query the stock of specific warehouses.  If the warehouse query is provided with endpoint but the string is not in the database then a 400 bad request is returned.

Finally, to make an order:

```bash
$ curl -H 'Content-Type: application/json' \
> -X POST \
> -d '{"order": {"Lemon": 10, "New York Striplon": 3, "Ground Pork": 2}}' \
> http://localhost:8000/order
```

In the above request, the data only contains the 'order'. When this is the case the default location of the order is Toronto but you can specify latitude and longitude like the following: 

```bash
$ curl -H 'Content-Type: application/json' \
> -X POST \
> -d '{"order": {"Lemon": 10, "New York Striplon": 3, "Ground Pork": 2}, "lat": 43.6532, "lng": -79.3832}' \
> http://localhost:8000/order
```

You will notice if you play with the lat and lng your responses will return differently each time due to the proximity of the warehouses to the order. Closer the warehouse, cheaper the cost to ship.

After a request has been made, you can send a request to the /stock endpoint to see the changes made to the database.

#### I think that's about it. Thank you for your time and the opportunity to apply for this position.



---



### Problem

The problem is compute the best way an order can be shipped (called shipments) given inventory across a set of warehouses (called inventory distribution). 

Your task is to implement InventoryAllocator class to produce the cheapest shipment.

The first input will be an order: a map of items that are being ordered and how many of them are ordered. For example an order of apples, bananas and oranges of 5 units each will be 

`{ apple: 5, banana: 5, orange: 5 }`

The second input will be a list of object with warehouse name and inventory amounts (inventory distribution) for these items. For example the inventory across two warehouses called owd and dm for apples, bananas and oranges could look like

`[ 
    {
    	name: owd,
    	inventory: { apple: 5, orange: 10 }
    }, 
    {
    	name: dm:,
    	inventory: { banana: 5, orange: 10 } 
    }
]`

You can assume that the list of warehouses is pre-sorted based on cost. The first warehouse will be less expensive to ship from than the second warehouse. 

You can use any language of your choice to write the solution (internally we use Typescript/Javascript, Python, and some Java). Please write unit tests with your code, a few are mentioned below, but these are not comprehensive. Fork the repository and put your solution inside of the src directory and include a way to run your tests!

### Examples

*Happy Case, exact inventory match!**

Input: `{ apple: 1 }, [{ name: owd, inventory: { apple: 1 } }]`  
Output: `[{ owd: { apple: 1 } }]`

*Not enough inventory -> no allocations!*

Input: `{ apple: 1 }, [{ name: owd, inventory: { apple: 0 } }]`  
Output: `[]`

*Should split an item across warehouses if that is the only way to completely ship an item:*

Input: `{ apple: 10 }, [{ name: owd, inventory: { apple: 5 } }, { name: dm, inventory: { apple: 5 }}]`  
Output: `[{ dm: { apple: 5 }}, { owd: { apple: 5 } }]`

### What are we looking for

We'll evaluate your code via the following guidelines in no particular order:

1. **Readability**: naming, spacing, consistency
2. **Correctness**: is the solution correct and does it solve the problem
1. **Test Code Quality**: Is the test code comperehensive and covering all cases.
1. **Tool/Language mastery**: is the code using up to date syntax and techniques. 
