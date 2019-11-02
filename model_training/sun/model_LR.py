from sklearn import linear_model
import numpy as np
import pickle
import matplotlib.pyplot as plt

f = open('/Users/letv/Desktop/智能交通系统/busgps/travel_time.pkl', 'rb')
RIO_AAM_one_month_cumtime = pickle.load(f)


def training(dist):
    """
    :param dist: it is a value of distance before which training set is, eg: if dist = 2000, the training set is
    traveling data from 0m to 2000m.
    :return: predict_time: the result of prediction

    """
    dataSet = RIO_AAM_one_month_cumtime
    trainSet_time = np.array(dataSet[0][dist//100:])
    trainSet_dist = np.linspace(dist//100*100, 14700, (148-dist//100))

    # consider just one trip for projection
    dataset_dist = np.linspace(0, (dist//100-1)*100, dist//100)
    dataset_time = dataSet[0][:dist//100]
    dataset_dist = np.reshape(dataset_dist, (-1, 1))
    dataset_time = np.reshape(dataset_time, (-1, 1))
    trainSet_dist = np.reshape(trainSet_dist, (-1, 1))
    trainSet_time = np.reshape(trainSet_time, (-1, 1))
    linear_mod = linear_model.LinearRegression(fit_intercept=True).fit(dataset_dist, dataset_time)
    predict_time = linear_mod.predict(dataset_dist)

    plt.plot(dataset_dist, predict_time)
    plt.scatter(dataset_dist, dataset_time, c = 'r', s = 0.4)
    plt.show()


    # consider all trips for projection
    '''for i in range(len(RIO_AAM_one_month_cumtime)):
        for j in range(dist//100):
            dataset_time.append(RIO_AAM_one_month_cumtime[i][j])

    cumDist = np.linspace(0, (dist/100-1)*100, dist/100)
    for i in range(len(RIO_AAM_one_month_cumtime)):
        for j in range(dist//100):
            dataset_dist.append(cumDist[j])

    plt.scatter(dataset_dist, dataset_time, s=0.01)
    plt.show()

    dataset_dist = np.reshape(dataset_dist, (-1, 1))
    dataset_time = np.reshape(dataset_time, (-1, 1))
    trainSet_dist = np.reshape(trainSet_dist, (-1, 1))

    linear_mod = linear_model.LinearRegression(fit_intercept=True).fit(dataset_dist, dataset_time)  # fitting the data points in the model
    predict_dist = linear_mod.predict(trainSet_dist)'''

    return predict_time

