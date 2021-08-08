from sklearn.ensemble import GradientBoostingRegressor
from sklearn.multioutput import MultiOutputRegressor
from persiantools.jdatetime import JalaliDate
from datetime import date
from pahbar.independentVariables import IndependentVariables
import numpy as np
import xgboost as xgb

class Trainer:
    def __init__ (self, R, X_train, y_train):
        self.R = R
        self.X_train = X_train
        self.y_train = y_train

    def trainSTLF (self):
        if self.R.selectedDataSet == '.pickle':
            self.regressors = xgb.XGBRegressor (gamma = 1, learning_rate = 0.12645036783043867, max_depth = 7, min_child_weight = 2.643065528997738, n_estimators = 500, reg_alpha = 1, reg_lambda = 4)
        else:
            self.regressors = xgb.XGBRegressor (gamma = 1, learning_rate = 0.17050036324954973, max_depth = 9, min_child_weight = 7.132296827885341, n_estimators = 300, reg_alpha = 1, reg_lambda = 2)

        self.regressors.fit (self.X_train.data, self.y_train)

        self.R.pickle_Data (self.regressors, 'Regressors_STLF_')
        self.R.pickle_Data (JalaliDate (date.today ()), 'TrainDate_STLF_')

    def trainMTLF (self):
        self.X_train1 = IndependentVariables (np.append (self.X_train.data [:, :28], self.X_train.data [:, 46:52], axis=1))
        self.X_train2 = IndependentVariables (np.append (np.append (self.X_train.data [:, :22], self.X_train.data [:, 28:35], axis=1), self.X_train.data [:, 52:59], axis=1))
        self.X_train3 = IndependentVariables (np.append (np.append (self.X_train.data [:, :22], self.X_train.data [:, 35:42], axis=1), self.X_train.data [:, 59:66], axis=1))
        self.X_train4 = IndependentVariables (np.append (np.append (self.X_train.data [:, :22], self.X_train.data [:, 42:46], axis=1), self.X_train.data [:, 66:70], axis=1))

        self.y_train1 = self.y_train [:, :6]
        self.y_train2 = self.y_train [:, 6:13]
        self.y_train3 = self.y_train [:, 13:20]
        self.y_train4 = self.y_train [:, 20:]

        if self.R.selectedDataSet == '.pickle':
            self.regressors1 = MultiOutputRegressor (GradientBoostingRegressor (learning_rate = 0.0955821802292142, max_depth = 2, min_samples_leaf = 9, min_samples_split = 5, n_estimators = 600))
            self.regressors2 = MultiOutputRegressor (GradientBoostingRegressor (learning_rate = 0.06847158508798183, max_depth = 3, min_samples_leaf = 9, min_samples_split = 7, n_estimators = 600))
            self.regressors3 = MultiOutputRegressor (GradientBoostingRegressor (learning_rate = 0.05607764747827199, max_depth = 5, min_samples_leaf = 11, min_samples_split = 7, n_estimators = 400))
            self.regressors4 = MultiOutputRegressor (GradientBoostingRegressor (learning_rate = 0.06477462527352827, max_depth = 3, min_samples_leaf = 8, min_samples_split = 10, n_estimators = 300))
        else:
            self.regressors1 = MultiOutputRegressor (xgb.XGBRegressor (gamma = 3, learning_rate = 0.05085490648417141, max_depth = 5, min_child_weight = 10.083538615760023, n_estimators = 300, reg_alpha = 2, reg_lambda = 2))
            self.regressors2 = MultiOutputRegressor (xgb.XGBRegressor (gamma = 1, learning_rate = 0.024348946541227493, max_depth = 6, min_child_weight = 7.031440750305921, n_estimators = 400, reg_alpha = 4, reg_lambda = 1))
            self.regressors3 = MultiOutputRegressor (xgb.XGBRegressor (gamma = 1, learning_rate = 0.044951497420213066, max_depth = 7, min_child_weight = 9.747517837177694, n_estimators = 600, reg_alpha = 4, reg_lambda = 4))
            self.regressors4 = MultiOutputRegressor (xgb.XGBRegressor (gamma = 3, learning_rate = 0.16439777858278282, max_depth = 4, min_child_weight = 1.0820037531995867, n_estimators = 500, reg_alpha = 2, reg_lambda = 1))

        self.regressors1.fit (self.X_train1.data, self.y_train1)
        self.regressors2.fit (self.X_train2.data, self.y_train2)
        self.regressors3.fit (self.X_train3.data, self.y_train3)
        self.regressors4.fit (self.X_train4.data, self.y_train4)

        self.R.pickle_Data (self.regressors1, 'Regressors1_MTLF_')
        self.R.pickle_Data (self.regressors2, 'Regressors2_MTLF_')
        self.R.pickle_Data (self.regressors3, 'Regressors3_MTLF_')
        self.R.pickle_Data (self.regressors4, 'Regressors4_MTLF_')
        self.R.pickle_Data (JalaliDate (date.today ()), 'TrainDate_MTLF_')