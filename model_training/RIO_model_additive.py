import math

import matplotlib.pyplot as plt
import numpy as np
from pygam import LinearGAM, s, f, te, l, GammaGAM, GAM
from sklearn.metrics import mean_absolute_error


X = np.load('RIO_BAM_one_month_factors.npy', allow_pickle=True)
y = np.load('RIO_BAM_one_month_time.npy', allow_pickle=True)
X1 = np.load('RIO_AAM_one_month_factors.npy')
y1 = np.load('RIO_AAM_one_month_time.npy')
# X = X[0:14699]
# y = y[0:14699]
X1 = X1[0:14699]
y1 = y1[0:14699]

def rmse(predictions, targets):
    return np.sqrt(((predictions - targets) ** 2).mean())


def mean_absolute_percentage_error(actual, predict):
    tmp, n = 0.0, 0
    for i in range(0, len(actual)):
        if actual[i] != 0:
            tmp += math.fabs(actual[i]-predict[i]) / actual[i]
            n += 1
    return (tmp/n)*100


# Basic additive model

def BAM():

    gam = GAM(s(0, n_splines=25, spline_order=3, constraints='concave', penalties = 'auto', basis = 'cp', edge_knots=[147,147])
                    + s(1, n_splines=25, spline_order=3, constraints='concave', penalties = 'auto', basis = 'cp', edge_knots=[147,147])
                    + te(0, 1, dtype=['numerical', 'numerical']), distribution= 'normal', link = 'identity', fit_intercept=True)
    print(gam.gridsearch(X, y, n_splines=np.arange(50)).summary())
    plt.scatter(X[:, 0][0:56], y[0:56], s=3, linewidths=0.0001, label='data')
    plt.plot(X[:, 0][0:56], gam.predict(X[0:56]), color='red', linewidth=1, label='prediction')
    plt.legend()
    plt.title('Basic Additive Model')
    plt.show()

    # error calculation
    rmse_val = rmse(np.array(y), np.array(gam.predict(X)))
    print("RMSE is: " + str(rmse_val))
    mae = mean_absolute_error(y, gam.predict(X))
    print("MAE is: " + str(mae))
    mape = mean_absolute_percentage_error(np.array(y), np.array(gam.predict(X)))
    print("MAPE is: " + str(mape))


# Extended additive model

def AAM():

    gam = LinearGAM(s(0, n_splines=25, spline_order=3, constraints='concave', penalties = 'auto', basis = 'cp', edge_knots=[147, 147])
                        + l(3)  # the last travel time
                        + te(0, 1)  # distance and departure_time
                        + te(2, 0)  # distance and isWeekend
                        + l(2),  # isWeekend
                    fit_intercept=True)

    print(gam.gridsearch(X1, y1).summary())
    # print(gam.gridsearch(X1,y1).get_params(deep=True))
    '''plt.scatter(X1[:,0][0:56], y1[0:56], s=3, linewidth=1, label = 'data')
    plt.plot(X1[:,0][0:56], gam.predict(X1[0:56]), color = 'red', linewidth = 1, label = 'prediction')
    plt.legend()
    plt.title('Extended Additive Model')
    plt.show()'''
    # error calculation
    rmse_val = rmse(np.array(y1), np.array(gam.predict(X1)))
    print("RMSE is: "+str(rmse_val))
    mae = mean_absolute_error(y1, gam.predict(X1))
    print("MAE is: "+str(mae))
    mape = mean_absolute_percentage_error(np.array(y1), np.array(gam.predict(X1)))
    print("MAPE is: "+ str(mape))


# BAM()
AAM()



# 分逻辑：train predict evaluation