import psycopg2
from psycopg2 import Error


def create_postgresql_connection():
    try:
        connection = psycopg2.connection(user='postgres',
                                         password='',
                                         host='127.0.0.1',
                                         port='5432',
                                         database='cyber_daily')
        cursor = connection.cursor()
        print("PostgreSQL server info", connection.get_dsn_parameters(), "\n")
        cursor.execute('''SELECT version();''')
        record = cursor.fetchone()
        print('You are connected to -', record, "\n")
        return connection, cursor
    except (Exception, Error) as error:
        print("Error while try connecting PostgreSQL", error)


def create_scheme(cursor):
    cursor.execute('''
        CREATE TABLE article(
            id PRIMARY KEY,
            title VARCHAR(300) NOT NULL,
            text TEXT NOT NULL,
            image 
        );
    ''')

    cursor.execute('''
        CREATE TABLE vulnerability(
            id PRIMARY KEY,
            title VARCHAR(200) NOT NULL,
            hits INTEGER NOT NULL,
            related_products TEXT []
        );
    ''')

    cursor.execute('''
        CREATE TABLE malware(
            id PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            hits INTEGER NOT NULL,
            targets TEXT []
        );
    ''')

    cursor.execute('''
        CREATE TABLE suspicious_ip(
            id PRIMARY KEY,
            ip_address TEXT NOT NULL,
            hits INTEGER NOT NULL
            
        )
    ''')


def close_postgresql_connection(connection, cursor):
    if connection:
        cursor.close()
        connection.close()
        print('PostgreSQL connection has been closed')
