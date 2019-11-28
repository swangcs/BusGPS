import numpy as np
from pygam import LinearGAM, s, f, te
import time
import pandas as pd
import math


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
    # model implementation by PYGAM
    gam = LinearGAM(s(0, spline_order=3) + s(1, spline_order=3) + te(0, 1))
    gam.gridsearch(X, y)
    # print(gam.gridsearch(X, y).summary())

    return gam


# Extended additive model
def EAM():
    X = np.load('EAM_factors.npy')
    y = np.load('EAM_time.npy')
    gam = LinearGAM(s(0, spline_order=3) + s(1, spline_order=3) + te(0, 1) + te(0, 2))
    gam.gridsearch(X, y)
    # print(gam.gridsearch(X, y).summary())


def predict_additive(model, X_test, y_test, sampleNum):
    predictResult = []
    for i in range(sampleNum):
        predictResult.append([])
        point = i + 1
        for j in range(point):
            predictResult[i].append(y_test[j])
        for z in range(sampleNum-point):
            predictValue = model.predict(X_test[i+z:i+z+1])
            predictResult[i].append(predictValue[0])
    return predictResult


def additive(X, y, count, sampleNum):
    # train
    trainingPoint = int(count*0.8)*sampleNum
    X_train, X_test = X[:trainingPoint], X[trainingPoint:]
    y_train, y_test = y[:trainingPoint], y[trainingPoint:]
    start = time.time()
    model = BAM(X_train, y_train)
    training_time = time.time() - start
    print("The training time is", training_time)

    # predict
    results = []
    start_time = time.time()
    for i in range(int(0.2 * count)):
        result = predict_additive(model, X_test[(sampleNum*i):(sampleNum*(i+1))], y_test[(sampleNum*i):(sampleNum*(i+1))], sampleNum)
        results.append(result)
    predict_time = round(time.time()-start_time, 4)
    print("The predicting time is:", predict_time)
    return training_time, predict_time, results
