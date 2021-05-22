from sklearn.ensemble import GradientBoostingRegressor
from sklearn.multioutput import MultiOutputRegressor
from persiantools.jdatetime import JalaliDate
from datetime import date

class Trainer:
    def __init__ (self, R, X_train, y_train):
        self.R = R
        self.X_train = X_train
        self.y_train = y_train

    def train (self):
        if self.R.selectedDataSet == '.pickle':
            self.regressors = MultiOutputRegressor (GradientBoostingRegressor (learning_rate = 0.0468544433312668, max_depth = 5, min_samples_leaf = 8, min_samples_split = 12, n_estimators = 600))
        else:
            self.regressors = MultiOutputRegressor (GradientBoostingRegressor (learning_rate = 0.1610574414711084, max_depth = 3, min_samples_leaf = 12, min_samples_split = 3, n_estimators = 400))

        self.regressors.fit (self.X_train.data, self.y_train)

        self.R.pickle_Data (self.regressors, 'Regressors_')
        self.R.pickle_Data (JalaliDate (date.today ()), 'TrainDate_')