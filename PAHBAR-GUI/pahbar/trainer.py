from sklearn.ensemble import GradientBoostingRegressor
from sklearn.multioutput import MultiOutputRegressor
from persiantools.jdatetime import JalaliDate
from datetime import date
from pahbar.independentVariables import IndependentVariables
import numpy as np

class Trainer:
    def __init__ (self, R, X_train, y_train):
        self.R = R
        # self.X_train = X_train
        self.X_train1 = IndependentVariables (np.append (X_train.data [:, :28], X_train.data [:, 46:52], axis=1))
        self.X_train2 = IndependentVariables (np.append (np.append (X_train.data [:, :22], X_train.data [:, 28:35], axis=1), X_train.data [:, 52:59], axis=1))
        self.X_train3 = IndependentVariables (np.append (np.append (X_train.data [:, :22], X_train.data [:, 35:42], axis=1), X_train.data [:, 59:66], axis=1))
        self.X_train4 = IndependentVariables (np.append (np.append (X_train.data [:, :22], X_train.data [:, 42:46], axis=1), X_train.data [:, 66:70], axis=1))
        self.y_train = y_train
        self.y_train1 = self.y_train [:, :6]
        self.y_train2 = self.y_train [:, 6:13]
        self.y_train3 = self.y_train [:, 13:20]
        self.y_train4 = self.y_train [:, 20:]

    def train (self):
        if self.R.selectedDataSet == '.pickle':
            self.regressors1 = MultiOutputRegressor (GradientBoostingRegressor (learning_rate = 0.1545603294037822, max_depth = 2, min_samples_leaf = 2, min_samples_split = 6, n_estimators = 600))
            self.regressors2 = MultiOutputRegressor (GradientBoostingRegressor (learning_rate = 0.05312384662574374, max_depth = 3, min_samples_leaf = 11, min_samples_split = 2, n_estimators = 400))
            self.regressors3 = MultiOutputRegressor (GradientBoostingRegressor (learning_rate = 0.09799479361171441, max_depth = 3, min_samples_leaf = 12, min_samples_split = 5, n_estimators = 300))
            self.regressors4 = MultiOutputRegressor (GradientBoostingRegressor (learning_rate = 0.09435769499714551, max_depth = 3, min_samples_leaf = 2, min_samples_split = 6, n_estimators = 400))
        else:
            self.regressors1 = MultiOutputRegressor (GradientBoostingRegressor (learning_rate = 0.12861628259637697, max_depth = 2, min_samples_leaf = 2, min_samples_split = 11, n_estimators = 500))
            self.regressors2 = MultiOutputRegressor (GradientBoostingRegressor (learning_rate = 0.02165431283694489, max_depth = 5, min_samples_leaf = 2, min_samples_split = 4, n_estimators = 500))
            self.regressors3 = MultiOutputRegressor (GradientBoostingRegressor (learning_rate = 0.1105016281437299, max_depth = 4, min_samples_leaf = 6, min_samples_split = 6, n_estimators = 600))
            self.regressors4 = MultiOutputRegressor (GradientBoostingRegressor (learning_rate = 0.12273083283463927, max_depth = 5, min_samples_leaf = 5, min_samples_split = 5, n_estimators = 500))

        self.regressors1.fit (self.X_train1.data, self.y_train1)
        self.regressors2.fit (self.X_train2.data, self.y_train2)
        self.regressors3.fit (self.X_train3.data, self.y_train3)
        self.regressors4.fit (self.X_train4.data, self.y_train4)

        self.R.pickle_Data (self.regressors1, 'Regressors1_')
        self.R.pickle_Data (self.regressors2, 'Regressors2_')
        self.R.pickle_Data (self.regressors3, 'Regressors3_')
        self.R.pickle_Data (self.regressors4, 'Regressors4_')
        self.R.pickle_Data (JalaliDate (date.today ()), 'TrainDate_')