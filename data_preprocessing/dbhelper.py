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
        connection = psycopg2.connect(user="postgres",
                                      password="postgres",
                                      host="127.0.0.1",
                                      port="5432",
                                      database="BusGPS"
                                      )
        return connection
    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgresSQL", error)

