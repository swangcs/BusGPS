import psycopg2
import configparser


def connect():
    """
    connect to postgres database and connect configuration can be changed in file config.ini
    :return:
    """
    cf = configparser.ConfigParser()
    cf.read("config.ini")
    try:
        connection = psycopg2.connect(user=cf.get('postgres', 'user'),
                                      password=cf.get('postgres', 'password'),
                                      host=cf.get('postgres', 'host'),
                                      port=cf.get('postgres', 'port'),
                                      database=cf.get('postgres', 'database')
                                      )
        return connection
    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgresSQL", error)

