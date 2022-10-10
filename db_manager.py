from psycopg2 import connect
from psycopg2 import Error

table_names = ['cyber_daily_article','cyber_daily_vulnerability','cyber_daily_malware','cyber_daily_suspicious_ip']

def create_postgresql_connection(user,password,database,host='localhost',port='5432'):
    try:
        psql_connection = connect(user=user,host=host,password=password,dbname=database)
        psql_connection.autocommit = True
        cursor = psql_connection.cursor()
        print("PostgreSQL server info", psql_connection.get_dsn_parameters(), "\n")
        cursor.execute('''SELECT version();''')
        record = cursor.fetchone()
        print('You are connected to -', record, "\n")
        return psql_connection, cursor
    except (Exception, Error) as error:
        print("Error while try connecting PostgreSQL", error)


def create_db_scheme(psql_connection,cursor):
    create_article_scheme(cursor)
    create_vulnerability_scheme(cursor)
    create_malware_scheme(cursor)
    create_suspicious_ip_scheme(cursor)

def create_article_scheme(cursor):
    cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS {table_names[0]}(
            title TEXT NOT NULL,
            short_text TEXT NOT NULL
        );
    ''')

def create_vulnerability_scheme(cursor):
    cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS {table_names[1]}(
                cve_name TEXT NOT NULL,
                hits TEXT NOT NULL,
                related_products TEXT [] NOT NULL
            );
    ''')

def create_malware_scheme(cursor):
    cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS {table_names[2]}(
            name TEXT NOT NULL,
            hits TEXT NOT NULL,
            targets TEXT [] NOT NULL
        );
    ''')



def create_suspicious_ip_scheme(cursor):
     cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS {table_names[3]}(
             ip_address VARCHAR(15) NOT NULL,
             hits TEXT NOT NULL,
             first_time_seen TEXT NOT NULL
        );
    ''')


def save_article(cursor,title,short_text):
    cursor.execute(f'''INSERT INTO {table_names[0]} (title,short_text) VALUES(%s,%s);''',(title,short_text))

def save_supsicious_ip(cursor,ip_address,hits,first_time_seen):
    cursor.execute('INSERT INTO cyber_daily_suspicious_ip (ip_address,hits,first_time_seen) VALUES(%s,%s,%s);',(ip_address,hits,first_time_seen))

def save_vulnerability(cursor,cve_name,hits,related_product_list):
    cursor.execute('INSERT INTO cyber_daily_vulnerability (cve_name,hits,related_products) VALUES(%s,%s,%s);',(cve_name,hits,related_product_list))

def save_malware(cursor,malware,hits,target_list):
    cursor.execute('INSERT INTO cyber_daily_malware (name,hits,targets) VALUES(%s,%s,%s);',(malware,hits,target_list))

def close_postgresql_connection(psql_connection, cursor):
    if psql_connection:
        cursor.close()
        psql_connection.close()
        print('PostgresSQL connection has been closed')
