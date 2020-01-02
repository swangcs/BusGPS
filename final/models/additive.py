from pygam import LinearGAM, s, te


def train(X, y):
    gam = LinearGAM(s(0, spline_order=5) + s(1, spline_order=5) + te(0, 1)).gridsearch(X, y)
    gam.summary()
    return gam


def predict(gam, X):
    return gam.predict(X)

