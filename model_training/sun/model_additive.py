import os
import matplotlib.pyplot as plt
import numpy as np
from pygam import LinearGAM, s, f, te
import time
import pandas as pd
import math
from datetime import datetime
from sklearn.metrics import mean_absolute_error
from scipy.spatial.distance import pdist

def rmse(predictions, targets):
    return np.sqrt(((predictions - targets) ** 2).mean())


def mean_absolute_percentage_error(actual, predict):
    tmp, n = 0.0, 0
    for i in range(0, len(actual)):
        if actual[i] != 0:
            tmp += math.fabs(actual[i]-predict[i]) / actual[i]
            n += 1
    return (tmp/n)*100

def timeTrans(stamp):
    datatime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(float(str(stamp)[0:10])))
    datatime = datatime+'.'+str(stamp)[10:]
    return datatime


# prepare dataset for additive model
def read_csv(file: str, sep=',', header=None, names=None):
    return pd.read_csv(file, header=0, sep=sep, na_values=['null'], dtype={"stop_name": str},
                       names=names)


# Basic additive model
def BAM(X, y):
    # filter
    '''X = np.load('BAM_factors.npy')
    y = np.load('BAM_time.npy')
    for i in range(len(y)):
        if y[i] > 10000:
            lb = (i // 57) * 57
            ub = (i // 57+1) * 57
            X[lb:ub, :] = -1
            y[lb:ub] = -1

    y = np.array(list(filter(lambda _: _ != -1, y)))
    X = np.array(list(filter(lambda _: _[0] != -1, X)))'''

    # model implementation by PYGAM
    trainingPoint = 83349
    X = X[: trainingPoint]
    y = y[: trainingPoint]
    gam = LinearGAM(s(0, spline_order=3) + s(1, spline_order=3) + te(0, 1))
    gam.gridsearch(X, y)
    # print(gam.gridsearch(X, y).summary())

    '''plt.scatter(X[:, 0], y, s=3, linewidths=0.0001, label='data')
    plt.plot(X[:, 0], gam.predict(X), color='red', linewidth=0.2, label='prediction')
    plt.legend()
    plt.title('Basic Additive Model')
    plt.show()'''

    return gam
# Extended additive model


def EAM():
    X = np.load('EAM_factors.npy')
    y = np.load('EAM_time.npy')
    gam = LinearGAM(s(0, spline_order=3) + s(1, spline_order=3) + te(0, 1) + te(0, 2))
    gam.gridsearch(X, y)
    # print(gam.gridsearch(X, y).summary())


def evaluation_additive(model, X, y):
    trainingPoint = 83348
    X_test = X[trainingPoint:]
    y_test = y[trainingPoint:]

    MAE = []
    MAPE = []
    RMSE = []

    for i in range(331):
        for j in range(63):
            MAE.append(mean_absolute_error(model.predict(X_test[(63*i+j):(i+1)*63]), y_test[(63*i+j):(i+1)*63]))
            MAPE.append(mean_absolute_percentage_error(model.predict(X_test[(63*i+j):(i+1)*63]), y_test[(63*i+j):(i+1)*63]))
            RMSE.append(rmse(model.predict(X_test[(63*i+j):(i+1)*63]), y_test[(63*i+j):(i+1)*63]))
    MAE = np.mean(MAE)
    MAPE = np.mean(MAPE)
    RMSE = np.mean(RMSE)

    return MAE, RMSE, MAPE


home_dir = "/Users/letv/Desktop/IntelligentTraffic/datasets/"
X_in = np.load(home_dir + 'additive' + '/' + 'BAM_factors_in.npy')
y_in = np.load(home_dir + 'additive' + '/' + 'BAM_accumTime_in.npy')
model = BAM(X_in, y_in)
MAE, RMSE, MAPE = evaluation_additive(model, X_in, y_in)
