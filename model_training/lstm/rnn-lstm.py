import csv
import os
import time

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from tensorflow.keras.layers import Dense, LSTM, Dropout, BatchNormalization
from tensorflow.keras.models import Sequential, load_model

from bus_evaluation import evaluate


# def loss(y_true, y_pred):
#     loss_sum = 0
#     delta = np.abs(y_pred - y_true)
#     for d in tf.Session().run(delta.eval()):
#         if d < 1:
#             loss_sum += d ** 2 / 2
#         else:
#             loss_sum += d - 0.5
#     return loss_sum


def training(X, Y, model_file):
    if not os.path.exists(model_file):
        print("---Training model---")
        train_x, test_x, train_y, test_y = train_test_split(X, Y, test_size=0.1, shuffle=False)
        # checkpoint_path = "training/lstm.ckpt"
        # checkpoint_dir = os.path.dirname(checkpoint_path)
        #
        # # Create a callback that saves the model's weights
        # cp_callback = tf.keras.callbacks.ModelCheckpoint(filepath=checkpoint_path,
        #                                                  save_weights_only=True,
        #                                                  verbose=1)

        model = create_model(128, 1)
        model.fit(train_x, train_y, epochs=3, batch_size=32, validation_data=(test_x, test_y))
        model.save(model_file)
    else:
        print("---Load model---")
        model = load_model(model_file)
    return model


def create_model(units, step):
    model = Sequential()
    model.add(LSTM(units, input_shape=(step, 3), return_sequences=True))
    model.add(Dropout(0.2))
    model.add(BatchNormalization())

    model.add(LSTM(units, return_sequences=True))
    model.add(Dropout(0.2))
    model.add(BatchNormalization())

    model.add(LSTM(units, return_sequences=True))
    model.add(Dropout(0.1))
    model.add(BatchNormalization())

    model.add(LSTM(units))
    model.add(Dropout(0.2))
    model.add(BatchNormalization())

    # model.add(Dense(32, activation="relu"))
    # model.add(Dropout(0.2))

    model.add(Dense(1))
    model.compile(
        loss="mse",
        optimizer='Adam'
    )
    return model


def rnn_predict(test, l, model):
    predict_set = []
    start = test[l].reshape(-1, 1, 3)
    for i in range(l, len(test) - 1):
        next_time = model.predict(start)
        predict_set.extend(next_time[0])
        # The current time is recorded in the second position
        start[0][0][1] = next_time
        start[0][0][2] = test[i+1][0][2]
    return predict_set


def main():
    home_dir = "/Users/ruixinhua/Documents/BusGPS/BusGPS/"
    bus_number = "46"
    rnn_trips_dir = home_dir + "processed/rnn_trips/" + bus_number + "/"
    for file in os.listdir(rnn_trips_dir)[:1]:
        rnn_result = [["Model", "Direction", "Trips Length", "Training Time(s)", "Prediction Time(s)", "MAE", "MAPE"]]
        start = time.time()
        # load the dataset and print the first 5 rows
        df = pd.read_csv(rnn_trips_dir + file)
        Y = df["target"].values.reshape(-1, 1)
        df.drop("target", axis=1, inplace=True)
        df.drop("next_dis", axis=1, inplace=True)
        x = df.values  # returns a numpy array
        standard_scale = StandardScaler()
        X = standard_scale.fit_transform(x)
        Y = standard_scale.fit_transform(Y)
        dataset = pd.DataFrame(X)
        dataset["target"] = Y
        grouped = dict(list(dataset.groupby([0])))
        dataset = list(grouped.values())
        trip_len = len(dataset[-1])
        test_ratio = int(0.2 * len(grouped.values()))
        # TODO: shuffle the list
        train_sets, test_sets = dataset[test_ratio:], dataset[:test_ratio]
        train_sets = pd.concat(train_sets)
        train_Y = train_sets["target"]
        train_sets.drop(0, axis=1, inplace=True)
        train_sets.drop("target", axis=1, inplace=True)
        train_X = np.array(train_sets.values).reshape((-1, 1, 3))
        print("Time usage for loading data:", time.time() - start)
        model_file = rnn_trips_dir + file.split(".")[0] + ".h5"
        start = time.time()
        model = training(train_X, train_Y, model_file)
        training_time_used = time.time() - start
        print("Time usage for training:", training_time_used)
        print("Test of", file.split(".")[0])
        start = time.time()
        MAE, MAPE, count = 0, 0, 0
        for test_set in test_sets:
            test_Y = standard_scale.inverse_transform(test_set["target"])
            test_set.drop(0, axis=1, inplace=True)
            test_set.drop("target", axis=1, inplace=True)
            test_set = test_set.values.reshape(-1, 1, 3)
            for l in range(0, trip_len - 1):
                predict_set = rnn_predict(test_set, l, model)
                predict_set = standard_scale.inverse_transform(predict_set)
                ae, ape, c = evaluate(test_Y[l+1:], predict_set)
                MAE, MAPE, count = ae + MAE, ape + MAPE, count + c
        MAE, MAPE = MAE / count, MAPE / count
        MAE, MAPE = round(MAE, 2), round(MAPE, 4)
        print("LSTM RNN MAE:", MAE)
        print("LSTM RNN MAPE:", MAPE)
        prediction_time_used = time.time() - start
        print("Time usage for prediction:", prediction_time_used)
        rnn_result.append(["LSTM RNN", file.split(".")[0], trip_len, training_time_used,
                           prediction_time_used, MAE, MAPE])
        print("---Write data---")
        out_dir = home_dir + "result/" + file.split(".")[0] + "Result.csv"
        with open(out_dir, "w", encoding='utf-8') as csv_out:
            cw = csv.writer(csv_out)
            cw.writerows(rnn_result)


if __name__ == "__main__":
    main()
