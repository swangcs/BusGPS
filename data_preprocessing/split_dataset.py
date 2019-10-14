import dbhelper
import pandas as pd


def split(from_date, to_date, line_id='15'):
    """
    split the dataset from a date to another date
    :param line_id: default 15
    :param from_date: start date
    :param to_date: end date
    :return: the dataset between these two date
    """
    sql_split = "select * from public.busgps where line_id='{}' and time_frame between %s and %s order by timestamp; ".format(line_id)
    connection = dbhelper.connect()
    cursor = connection.cursor()
    cursor.execute(sql_split, (from_date, to_date,))
    dataset = cursor.fetchall()
    print(from_date, to_date, ':', len(dataset))
    return dataset


def to_csv(dataset, filename):
    df = pd.DataFrame(dataset, index=None)
    df.to_csv(filename, index=None, header=False)


def select_one_day(line_id='15'):
    return split('2013-01-07', '2013-01-07', line_id)


def select_one_week(line_id='15'):
    return split('2013-01-07', '2013-01-13', line_id)


def select_one_month(line_id='15'):
    return split('2013-01-01', '2013-01-31', line_id)


def select_two_month(line_id='15'):
    return split('2012-11-05', '2013-01-31', line_id)
