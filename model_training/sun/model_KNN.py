import math
import operator
import time
import pickle
import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics import mean_absolute_error
from scipy.spatial.distance import pdist


# Calculation of Root Mean Squared Error
def rmse(predictions, targets):
    return np.sqrt(((predictions-targets) ** 2).mean())


# Calculation of euclidean distance between two sequences
def euclideanDistance(instance1, instance2):
    distance = 0
    '''for x in range(length):
        distance += pow((instance1[x] - instance2[x]), 2)
    return math.sqrt(distance)'''

    X = np.vstack([instance1, instance2])
    return pdist(X)


# Calculation of mean absolute percentage error
def mean_absolute_percentage_error(actual, predict):
    tmp, n = 0.0, 0
    for i in range(0, len(actual)):
        if actual[i] != 0:
            tmp += math.fabs(actual[i]-predict[i]) / actual[i]
            n += 1
    return (tmp / n) * 100


# getting k nearest neighbors of one trip
def getNeighbors(trainingSet, testInstance, k, index):
    """
    :param trainingSet: it is a list of training sets
    :param testInstance: one trip used for projection
    :param k: donating the number of chosen neighbors
    :param index: the current position
    :return: k nearest neighbors
    """
    distances = []

    # calculating the euclidean distance with all other trips
    for x in range(len(trainingSet)):
        dist = euclideanDistance(testInstance[:index], trainingSet[x][:index])
        distances.append((trainingSet[x], dist))

    # ranking in the order of distance calculated
    distances.sort(key=operator.itemgetter(1))
    neighbors = []

    # return k
    for x in range(k):
        neighbors.append(distances[x][0])
    return neighbors


def predict(neighbor, testInstance, k, index):
    """
    :param neighbor: k neighbors
    :param testInstance: one trip used for projection
    :param index: the current position
    :param k: donating the number of chosen neighbors
    :return: the list of predicted time after the current position
    """
    predictTime = []
    timeSum = 0
    for i in range(index):
        predictTime.append(testInstance[i])
    for i in range(len(testInstance)-index):
        for j in range(k):
            timeSum = timeSum+neighbor[j][index+i]-neighbor[j][index-1]
        timeDiff = timeSum / k
        predictTime.append(predictTime[index-1]+timeDiff)
        timeSum = 0
    return predictTime


def training_and_evaluation(trainingSet, testSet):
    """
    :param testSet:
    :param trainingSet: a list of training sets
    :returns: RMSE, MAE, MAPE
    """
    RMSE = []
    MAE = []
    MAPE = []

    for j in range(len(testSet)):
        testInstance = testSet[j]
        for i in range(len(testInstance)-1):
            result = getNeighbors(trainingSet, testInstance, 25, i+1)
            predictResult = predict(result, testInstance, 25, i+1)
            RMSE.append(rmse(np.array(predictResult[i:]), np.array(testInstance[i:])))
            MAE.append(mean_absolute_error(testInstance[i:], predictResult[i:]))
            MAPE.append(mean_absolute_percentage_error(testInstance[i:], predictResult[i:]))

    RMSEu = np.mean(RMSE)
    MAEu = np.mean(MAE)
    MAPEu = np.mean(MAPE)

    return RMSEu, MAEu, MAPEu


def KNN(y, count, direction):
    sampleNum = 0
    dataset = []
    if direction == 'I':
        sampleNum = 63
        print("Test for in:")
    else:
        sampleNum = 59
        print("Test for out:")
    for i in range(count):
        dataset.append([])
        for j in range(sampleNum):
            dataset[i].append(y[sampleNum * i + j])
    trainingPoint = int(count * 0.8)
    y_train, y_test = dataset[:trainingPoint], dataset[trainingPoint:]
    results = []
    start = time.time()
    for j in range(len(y_test)):
        testInstance = y_test[j]
        Presult = []
        for z in range(len(testInstance)-1):
            result = getNeighbors(y_train, testInstance, 25, z+1)
            predictResult = predict(result, testInstance, 25, z+1)
            Presult.append(predictResult)
        results.append(Presult)
    predict_time = round(time.time()-start, 4)
    print("The predicting time is:", predict_time)
    return results, predict_time

