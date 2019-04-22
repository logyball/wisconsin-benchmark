import psycopg2 as pgre
from os import environ as env
from random import sample

def get_setup_vars():
    return {
        'db': env['P_DB'] if env.get('P_DB') else 'wisc',
        'host': env['P_HOST'] if env.get('P_HOST') else 'localhost',
        'port': env['P_PORT'] if env.get('P_PORT') else 5432,
        'user': env['P_USER'] if env.get('P_USER') else 'postgres',
        'pass': env['P_PASS'] if env.get('P_PASS') else 'admin'
    }

# decorator that will do all the try/catching for pyscopg2
# sql errors
def transaction(db_call):
    def transaction_wrapper(conn, *args, **kwargs):
        try:
            cursor = conn.cursor()
            db_call(cursor, *args, **kwargs)
            cursor.close()
            conn.commit()
        except pgre.DatabaseError as error:
            conn.rollback()
            print(error)
    return transaction_wrapper

@transaction
def create_schema(cursor, schema):
    """
    Make sure to pass in a connection object when calling! 
    Decorator will pass in cursor.
    Creates the named schema.
    
    Arguments:
        - cursor (conn) - a postgres connection object
        - schema - name of the schema to be created
    """
    cursor.execute(f"CREATE SCHEMA IF NOT EXISTS {schema};")

@transaction
def create_tables(cursor, schema):
    """
    Make sure to pass in a connection object when calling!
    Creates the tables that the wisconsin benchmark tests: 1k, 10k, 10k2
    
    Arguments:
        - cursor (conn) - a postgres connection object
        - schema - name of the schema
    """
    cursor.execute(f"""CREATE TABLE IF NOT EXISTS {schema}.ONEKTUP (
        unique1         integer NOT NULL,
        unique2         integer NOT NULL PRIMARY KEY,
        two             integer NOT NULL,
        four            integer NOT NULL,
        ten             integer NOT NULL,
        twenty          integer NOT NULL,
        onePercent      integer NOT NULL,
        tenPercent      integer NOT NULL,
        twentyPercent   integer NOT NULL,
        fiftyPercent    integer NOT NULL,
        unique3         integer NOT NULL,
        evenOnePercent  integer NOT NULL,
        oddOnePercent   integer NOT NULL,
        stringu1        char(52) NOT NULL,
        stringu2        char(52) NOT NULL,
        string4         char(52) NOT NULL
    );""")
    cursor.execute(f"""CREATE TABLE IF NOT EXISTS {schema}.TENKTUP1 (
        unique1         integer NOT NULL,
        unique2         integer NOT NULL PRIMARY KEY,
        two             integer NOT NULL,
        four            integer NOT NULL,
        ten             integer NOT NULL,
        twenty          integer NOT NULL,
        onePercent      integer NOT NULL,
        tenPercent      integer NOT NULL,
        twentyPercent   integer NOT NULL,
        fiftyPercent    integer NOT NULL,
        unique3         integer NOT NULL,
        evenOnePercent  integer NOT NULL,
        oddOnePercent   integer NOT NULL,
        stringu1        char(52) NOT NULL,
        stringu2        char(52) NOT NULL,
        string4         char(52) NOT NULL
    );""")
    cursor.execute(f"""CREATE TABLE IF NOT EXISTS {schema}.TENKTUP2 (
        unique1         integer NOT NULL,
        unique2         integer NOT NULL PRIMARY KEY,
        two             integer NOT NULL,
        four            integer NOT NULL,
        ten             integer NOT NULL,
        twenty          integer NOT NULL,
        onePercent      integer NOT NULL,
        tenPercent      integer NOT NULL,
        twentyPercent   integer NOT NULL,
        fiftyPercent    integer NOT NULL,
        unique3         integer NOT NULL,
        evenOnePercent  integer NOT NULL,
        oddOnePercent   integer NOT NULL,
        stringu1        char(52) NOT NULL,
        stringu2        char(52) NOT NULL,
        string4         char(52) NOT NULL
    );""")

@transaction
def insert_tuple(cursor, vals, schema, table):
    """
    Make sure to pass in a connection object when calling!
    Creates the tables that the wisconsin benchmark tests: 1k, 10k, 10k2
    
    Arguments:
        - cursor (conn) - a postgres connection object
        - vals - the tuple to insert
        - schema - name of the schema
        - table - the table to insert the tuple into
    """
    cursor.execute(f"""
        INSERT INTO {schema}.{table} (unique1, unique2, two, four, ten, twenty, onePercent, tenPercent, twentyPercent, fiftyPercent, unique3, evenOnePercent, oddOnePercent, stringu1, stringu2, string4)
        VALUES ({vals[0]}, {vals[1]}, {vals[2]}, {vals[3]}, {vals[4]}, {vals[5]}, {vals[6]}, {vals[7]}, {vals[8]}, {vals[9]}, {vals[10]}, {vals[11]}, {vals[12]}, '{vals[13]}', '{vals[14]}', '{vals[15]}');
    """)

def gen_stringu1_2(uniq):
    ret = ['A','A','A','A','A','A','A']
    i = 6
    while uniq > 0:
        rem = uniq % 26
        ret[i] = chr(ord('A') + rem)
        uniq = uniq // 26
        i -= 1
    return "".join(ret) + 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'

def gen_string4(x):
    string4 = [
        'AAAAxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx',
        'HHHHxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx',
        'OOOOxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx',
        'VVVVxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
    ]
    return string4[x % 4]

def generate_data(conn, schema):
    """
    Generates fake data to be inserted into the 1k, tenk1, tenk2,
    tables.

    Arguments:
        - cursor (conn) - a postgres connection object
        - schema - name of the schema
    """
    ten_thous = sample(range(10000), 10000)
    for uniq2 in range(0, 10000):
        uniq1 = uniq3 = ten_thous[uniq2]
        two = fiftyP = uniq1 % 2
        four = uniq1 % 4
        ten = tenP = uniq1 % 10
        twenty = uniq1 % 20
        oneP = uniq1 % 100
        twentyP = uniq1 % 5
        evenOneP = oneP*2
        oddOneP = evenOneP + 1
        stringu1 = gen_stringu1_2(uniq1)
        stringu2 = gen_stringu1_2(uniq2)
        string4 = gen_string4(uniq2)
        vals = (uniq1, uniq2, two, four, ten, twenty, oneP, tenP, twentyP, fiftyP, uniq3, evenOneP, oddOneP, stringu1, stringu2, string4)
        tables = ['ONEKTUP', 'TENKTUP1', 'TENKTUP2'] if uniq2 < 1000 else ['TENKTUP1', 'TENKTUP2']
        for table in tables:
            insert_tuple(conn, vals=vals, schema=schema, table=table)