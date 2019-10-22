import numpy as np
import data_preprocessing.RIO_split_dataset as split
# data set for BAM
import data_preprocessing.utils as utils
import time
import pickle
import operator

# dataset for BAM
'''one_month_data = np.array(split.select_one__month(line_id='121'))

for i in range(len(one_month_data[:, 14])):
    one_month_data[:, 14][i] = int(utils.convert_to_timestamp(one_month_data[:, 14][i]))


for i in range(len(one_month_data[:,17])):
    one_month_data[:, 17][i] = time.strptime(one_month_data[:, 17][i], "%H:%M:%S")
    one_month_data[:, 17][i] = int(time.mktime(one_month_data[:, 17][i]))

for i in range(len(one_month_data[:, 6])):
    one_month_data[:, 6][i] = int(one_month_data[:, 6][i])

y = one_month_data[:, 14]
X = np.array((one_month_data[:, 6], one_month_data[:, 17]))
X = np.transpose(X)

np.save('RIO_BAM_one_month_time.npy', y)
np.save('RIO_BAM_one_month_factors.npy', X)'''


# dataset for AAM
f = open('/Users/letv/Desktop/智能交通系统/busgps/travel_time.pkl', 'rb')
RIO_AAM_one_month_cumtime = pickle.load(f)
f1 = open('/Users/letv/Desktop/智能交通系统/busgps/timeinit.pkl', 'rb')
RIO_AAM_one_month_timeInit = pickle.load(f1)
f2 = open('/Users/letv/Desktop/智能交通系统/busgps/weekday.pkl', 'rb')
RIO_AAM_one_month_weekday = pickle.load(f2)
f3 = open('/Users/letv/Desktop/智能交通系统/busgps/weekend.pkl', 'rb')
RIO_AAM_one_month_weekend = pickle.load(f3)
f4 = open('/Users/letv/Desktop/智能交通系统/busgps/timeinit2.pkl', 'rb')
RIO_AAM_one_month_timeInit2 = pickle.load(f4)

init = RIO_AAM_one_month_timeInit
init.sort(key=operator.itemgetter(0), reverse=False)
X = [[0 for x in range(5)] for _ in range(2515*148)]
for i in range(2515):
    for j in range(148):
        X[j + 148 * i][0] = RIO_AAM_one_month_cumtime[i][j]
        X[j + 148 * i][1] = j
        X[j + 148 * i][2] = RIO_AAM_one_month_timeInit2[i][j]
        X[j + 148 * i][3] = RIO_AAM_one_month_weekend[i][j]
        X[j + 148 * i][4] = RIO_AAM_one_month_timeInit[i][j]

X.sort(key=operator.itemgetter(4), reverse = False)
# set the lsat column of X to the traveling time of the last bus
for i in range(2515):
    for j in range(148):
        if i == 0:
            X[j + 148 * i][4] = X[j + 148 * i][0]
        else:
            X[j + 148 * i][4] = X[j + 148 * (i-1)][0]

X = np.array(X)
RIO_AAM_one_month_factors = np.transpose([X[:, 1], X[:, 2], X[:, 3], X[:, 4]])
RIO_AAM_one_month_time = np.transpose([X[:, 0]])
np.save('RIO_AAM_one_month_factors.npy', RIO_AAM_one_month_factors)
np.save('RIO_AAM_one_month_time.npy', RIO_AAM_one_month_time)

