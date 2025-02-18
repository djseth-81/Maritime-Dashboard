# Operator that will interact with Postgres
from pg import DB

### Demonstration by creating a test db with fruit entries
# db = DB(dbname='testdb', host='pgserver', port=5432, user='sdj81')  # assuming this works like the ogr2ogr??
db = DB(dbname='demo')  # assuming this works like the ogr2ogr??

# generate a new db using std SQL notation
db.query("create table fruits(id serial primary key, name varchar)")

tables = db.get_tables() # lists all database tables
print(tables)

attr = db.get_attnames('fruits') # gets the attributes of fruit
print(attr)

privileges = db.has_table_privilege('fruits', 'insert') # check if I can insert data into fruits table
print(privileges)

db.insert('fruits', name='apple') # inserts new row into table
# Row : {'name': 'apple' 'id': 1}

banana = db.insert('fruits', name='banana')

# Enumerating to enter multiple values into fruits table
more_fruit = "cherry papaya eggplant tomato banana fig grapefruit orange".split()
data = list(enumerate(more_fruit, start=2))
db.inserttable('fruits', data)

print(db.query('select * from fruits')) # use std SQL queries to pull all data from fruits, and print them

# can assign queries to variables, which then can be used to manipulate. For Example, can use it to represent the data as a list of tuples
q = db.query('select * from fruits')
print(q.getresult())

print(db.get_as_dict('fruits', scalar=True)) # retrieve db data as a dictionary

# updating entry "banana" to capitalize the name to Banana
db.update('fruits', banana, name=banana['name'].capitalize())

# updating table to capitalize all names using SQL commands
db.query('update fruits set name=initcap(name)')

print(db.query('select * from fruits')) # use std SQL queries to pull all data from fruits, and print them

db.delete('fruits', id=1) # deletes row with id of 1 from fruits
db.query("drop table fruits") # use SQL to drop table fruits
db.close() # close DB connection
