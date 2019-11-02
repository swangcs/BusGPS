import math
import operator
import pickle
import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics import mean_absolute_error
from scipy.spatial.distance import pdist


# Calculation of Root Mean Squared Error
def rmse(predictions, targets):
    return np.sqrt(((predictions - targets) ** 2).mean())


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
    return (tmp/n)*100


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


def predict(neighbor, testInstance, index, k):
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
    for i in range(len(testInstance) - index):
        for j in range(k):
            timeSum = timeSum + neighbor[j][index + i] - neighbor[j][index - 1]
        timeDiff = timeSum / k
        predictTime.append(predictTime[index - 1] + timeDiff)
        timeSum = 0
    return predictTime


def training(trainingSet):
    """
    :param trainingSet: a list of training sets
    :returns: RMSE, MAE, MAPE
    """
    for j in range(len(trainingSet)):
        for i in range(len(trainingSet)-2):
            testInstance = trainingSet[j]
            result = getNeighbors(trainingSet, testInstance, 25, i+1)
            predictResult = predict(result, testInstance, i+1, 25)
            RMSE.append(rmse(np.array(predictResult[i+1:]), np.array(testInstance[i+1:])))
            MAE.append(mean_absolute_error(testInstance[i+1:], predictResult[i+1:]))
            MAPE.append(mean_absolute_percentage_error(testInstance[i+1:], predictResult[i+1:]))

    RMSEu = np.mean(RMSE)
    MAEu = np.mean(MAE)
    MAPEu = np.mean(MAPE)

    return RMSEu, MAEu, MAPEu


f = open('/Users/letv/Desktop/智能交通系统/busgps/travel_time.pkl', 'rb')
trainingSet = pickle.load(f)
RMSE = []
MAE = []
MAPE = []


# Figure 3
testInstance = trainingSet[13]
result = getNeighbors(trainingSet, testInstance, 25, 50)
predictResult = predict(result, testInstance, 50, 25)
cumDist = np. linspace(0, 14700, 148)
for x in range(25):
    result[x][50] = trainingSet[13][50]
    plt.plot(cumDist[50:], np.array(result[x][50:]), color='red', linestyle='-', linewidth=0.3)
plt.plot(cumDist, np.array(trainingSet[13]), color='blue', linestyle='-', linewidth=0.5)
plt.show()


########################################################################################################################


home_dir = "/Users/letv/Desktop/IntelligentTraffic/datasets/"
y_in = np.load(home_dir + 'additive' + '/' + 'BAM_accumTime_in.npy')
dataSet = []
for i in range(int(len(y_in)/63)):
    dataSet.append([])
    for j in range(63):
        dataSet[i].append(y_in[63*i+j])

trainingSet = dataSet[:1324]
testSet = dataSet[1323:]
RMSEu, MAEu, MAPEu = training_and_evaluation(trainingSet, testSet)
