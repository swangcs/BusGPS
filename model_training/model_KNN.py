import math
import operator
import pickle
import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics import mean_absolute_error
from scipy.spatial.distance import pdist


def rmse(predictions, targets):
    return np.sqrt(((predictions - targets) ** 2).mean())


def euclideanDistance(instance1, instance2):
    distance = 0
    '''for x in range(length):
        distance += pow((instance1[x] - instance2[x]), 2)
    return math.sqrt(distance)'''

    X = np.vstack([instance1, instance2])
    return pdist(X)

def mean_absolute_percentage_error(actual, predict):
    tmp, n = 0.0, 0
    for i in range(0, len(actual)):
        if actual[i] != 0:
            tmp += math.fabs(actual[i]-predict[i]) / actual[i]
            n += 1
    return (tmp/n)*100


def getNeighbors(trainingSet, testInstance, k, index):
    distances = []

    for x in range(len(trainingSet)):
        dist = euclideanDistance(testInstance[:index], trainingSet[x][:index])
        # print(dist)
        distances.append((trainingSet[x], dist))

    distances.sort(key=operator.itemgetter(1))
    neighbors = []

    for x in range(k):
        neighbors.append(distances[x][0])
    return neighbors


def predict(neighbor, testInstance, index, k):
    predictTime = []
    timeSum = 0
    for i in range(index):
        predictTime.append(testInstance[i])
    for i in range(len(testInstance) - index):
        for j in range(k):
            timeSum = timeSum + neighbor[j][index + i] - neighbor[j][index - 1]
        timeDiff = timeSum / k
        # print(timeDiff)
        predictTime.append(predictTime[index - 1] + timeDiff)
        timeSum = 0
    return predictTime


def training(trainingSet):
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


# Figure 4 and Figure 5
color = ['b', 'g', 'r', 'c', 'm']
label = ['k = 5', 'k = 10', 'k = 15', 'k = 20', 'k = 25']
tempMAE = []
for x in range(5):
    k = 5 * (x + 1)
    MAE = []
    temp = []
    tempMAE.append(temp)
    for i in range(len(trainingSet)//200):
        testInstance = trainingSet[i]
        for j in range(14):
            result = getNeighbors(trainingSet, testInstance, k, 10*j+1)
            predictResult = predict(result, testInstance, 10*j+1, k)
            MAE.append(mean_absolute_error(testInstance[i+1:], predictResult[i+1:]))

    for j in range(14):
        temp = []
        tempMAE[x].append(temp)
        for i in range(12):
            temp.append(MAE[14*i + j])

    for i in range(len(tempMAE[x])):
        tempMAE[x][i] = np.mean(tempMAE[x][i])

for x in range(5):
    cumDist = np. linspace(1, 14, 14)
    plt.plot(cumDist, tempMAE[x], label=label[x], color = color[x], linewidth = 0.5, linestyle = '-')

plt.legend(loc='upper right')
plt.show()

