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
            title VARCHAR(300) NOT NULL,
            text TEXT NOT NULL,
            image 
        );
    ''')

    cursor.execute('''
        CREATE TABLE vulnerability(,
            title VARCHAR(200) NOT NULL,
            hits INTEGER NOT NULL,
            related_products TEXT [] NOT NULL
        );
    ''')

    cursor.execute('''
        CREATE TABLE malware(
            name VARCHAR(100) NOT NULL,
            hits INTEGER NOT NULL,
            targets TEXT [] NOT NULL
        );
    ''')

    cursor.execute('''
        CREATE TABLE suspicious_ip(
            ip_address TEXT NOT NULL,
            hits INTEGER NOT NULL
            first_seen TEXT NOT NULL
        )
    ''')


def save_suspicious_ip_address(cursor, ip_address, hits, first_seen):
    cursor.execute('''
        INSERT INTO suspicious_ip_address(ip_address_hits,first_seen)
        VALUES (%s,%d,%s)
        ''', (ip_address, hits, first_seen))


def save_malware(cursor, name, hits, targets):
    cursor.execute('''
        INSERT INTO malware (name,hits,targets) 
    ''')


def save_vulnerability(cursor, cve, hits, related_products):
    pass


def close_postgresql_connection(connection, cursor):
    if connection:
        cursor.close()
        connection.close()
        print('PostgreSQL connection has been closed')
