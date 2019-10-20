import numpy as np
import data_preprocessing.RIO_split_dataset as split
# data set for BAM
import data_preprocessing.utils as utils
import time
import pickle
import operator


f = open('/Users/letv/Desktop/智能交通系统/busgps/travel_time.pkl', 'rb')
RIO_AAM_one_month_cumtime = pickle.load(f)
f1 = open('/Users/letv/Desktop/智能交通系统/timeinit.pkl', 'rb')
RIO_AAM_one_month_timeInit = pickle.load(f1)
f2 = open('/Users/letv/Desktop/智能交通系统/busgps/weekday.pkl', 'rb')
RIO_AAM_one_month_weekday = pickle.load(f2)
f3 = open('/Users/letv/Desktop/智能交通系统/busgps/weekend.pkl', 'rb')
RIO_AAM_one_month_weekend = pickle.load(f3)
f4 = open('/Users/letv/Desktop/智能交通系统/busgps/timeinit.pkl', 'rb')
RIO_AAM_one_month_timeInit2 = pickle.load(f4)


