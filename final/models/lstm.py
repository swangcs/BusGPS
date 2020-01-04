from keras.models import Sequential
from keras.layers import Dense, LSTM
from keras.optimizers import Adam


def train(X_train, Y_train):
    model = Sequential()
    model.add(LSTM(64, kernel_initializer="glorot_normal",
                   recurrent_initializer="glorot_normal", input_shape=(None, 4)))
    model.add(Dense(X_train.shape[1]))
    # opt = SGD(learning_rate=0.0001, momentum=0.95)
    opt = Adam(learning_rate=0.01)
    model.compile(loss="huber_loss", optimizer=opt)
    # set verbose to 0 to mute training info
    model.fit(X_train, Y_train, epochs=1000, verbose=0)
    return model


def predict(model, X_test):
    return model.predict(X_test)
