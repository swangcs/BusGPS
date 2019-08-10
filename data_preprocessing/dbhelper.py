import psycopg2


def connect():
    """
    connect to postgres database
    :return:
    """
    try:
        connection = psycopg2.connect(user='postgres',
                                      password='postgres',
                                      host='127.0.0.1',
                                      port='5432',
                                      database='postgres')
        return connection
    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgresSQL", error)

