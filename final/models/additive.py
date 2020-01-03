from pygam import LinearGAM, s, te


def train(X, y):
    gam = LinearGAM(s(0) + s(1) + te(0, 1)).fit(X, y)
    # gam.summary()
    return gam


def predict(gam, X):
    return gam.predict(X).reshape(X.shape[0], 1)

