import matplotlib.pyplot as plt
import data_preprocessing.process
import numpy as np
from pygam import LinearGAM, s, f, te
import data_preprocessing.process
from additive_Model.translation_TimeStamp import timeTrans
from additive_Model.translation_TimeStamp import isWeekend

trips = data_preprocessing.process.load_json('trips.json')


# Basic additive model

def BAM():
    # filter
    X = np.load('BAM_factors.npy')
    y = np.load('BAM_time.npy')
    for i in range(len(y)):
        if y[i] > 10000:
            lb = (i // 57) * 57
            ub = (i // 57+1) * 57
            X[lb:ub, :] = -1
            y[lb:ub] = -1

    y = np.array(list(filter(lambda _: _ != -1, y)))
    X = np.array(list(filter(lambda _: _[0] != -1, X)))
    '''bamdata = [y, X[:, 0], X[:, 1]]
    np.savetxt('/Users/letv/Desktop/bamdata.txt', bamdata)'''

    # model implementation by PYGAM

    gam = LinearGAM(s(0, n_splines=len(trips['6318']['stop_id']), spline_order=3)
                    +s(1, n_splines=len(trips['6318']['stop_id']), spline_order=3)
                    +te(0, 1))

    print(gam.gridsearch(X, y).summary())

    plt.scatter(X[:, 0], y, s=3, linewidths=0.0001, label='data')
    plt.plot(X[:, 0], gam.predict(X), color='red', linewidth=0.2, label='prediction')
    plt.legend()
    plt.title('Basic Additive Model')
    plt.show()


# Extended additive model


'''def EAM():
    X = np.load('EAM_factors.npy')
    y = np.load('EAM_time.npy')
    gam = LinearGAM(s(0, n_splines=len(trips['6318']['stop_id']), spline_order=3)
                        + s(1, n_splines=len(trips['6318']['stop_id']), spline_order=3)
                        + te(0, 1) + te(0, 2))
    print(gam.gridsearch(X[::200], y[::200]).summary())
    for i in range(len())
    plt.scatter(X[::200, 0], y[::200], s=3, linewidths=0.0001, label = 'data')
    plt.plot(X[::200, 0], gam.predict(X[::200]), color = 'red', linewidth = 0.2, label = 'prediction')
    plt.legend()
    plt.title('Extended Additive Model')
    plt.show()'''

BAM()
'''EAM()'''
