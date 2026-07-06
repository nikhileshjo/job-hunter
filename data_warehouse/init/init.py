# Importing modules
from sqlalchemy import URL
from sqlalchemy import create_engine
from sqlalchemy import text
from os import listdir
from os.path import isfile, join

class db:
    def __init__(self):
        # connect to database
        self.url = URL.create(
            "postgresql+psycopg2",
            username="admin",
            password="admin",
            host="localhost",
            database="jobs",
        )

        self.engine = create_engine(self.url)
    
    def execute_query(self, query):
        # execute query
        with self.engine.begin() as conn:
            conn.execute(text(query))


conn = db()

files = [f.strip() for f in open("init/ddl_order.txt", "r")]
for file in files:
    if file[-4:] == '.sql':
        print(f"INFO: Executing {file}")
        with open('init/'+file) as f:
            query = f.read()
            # print(query)
            conn.execute_query(query)
