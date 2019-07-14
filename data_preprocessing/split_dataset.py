import dbhelper
import pandas as pd


def split(from_date, to_date):
    """
    split the dataset from a date to another date
    :param from_date: start date
    :param to_date: end date
    :return: the dataset between these two date
    """
    sql_split = "select * from public.busGPS where time_frame between %s and %s order by timestamp; "
    connection = dbhelper.connect()
    cursor = connection.cursor()
    cursor.execute(sql_split, (from_date, to_date,))
    dataset = cursor.fetchall()
    print(from_date, to_date, ':', len(dataset))
    return dataset


def to_csv(dataset, filename):
    df = pd.DataFrame(dataset, index=None)
    df.to_csv(filename, index=None, header=False)


# select_one_day = split('2013-01-07', '2013-01-07')
# to_csv(select_one_day, 'one_day.csv')
# select_one_week = split('2013-01-07', '2013-01-13')
# select_one_month = split('2013-01-01', '2013-01-31')
# select_two_month = split('2012-11-05', '2013-01-31')
