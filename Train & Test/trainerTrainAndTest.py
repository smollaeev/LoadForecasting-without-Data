from sklearn.ensemble import RandomForestRegressor
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.multioutput import MultiOutputRegressor
from sklearn.svm import SVC
import pandas as pd
from sklearn.model_selection import train_test_split
import copy
import numpy as np
from sklearn.preprocessing import StandardScaler
from clusteringTrainAndTest import Clusterer
import sklearn.cluster as cluster
from sklearn.ensemble import RandomForestClassifier
from sklearn import metrics
from sklearn.model_selection import cross_validate
from sklearn.model_selection import RandomizedSearchCV
from sklearn.model_selection import cross_val_score
from scipy.stats import uniform

class Trainer:
    def __init__ (self, X_train, y_train):
        self.X_train = X_train
        self.y_train = y_train

    def train (self):
        # self.regressors = GradientBoostingRegressor (learning_rate= 0.13696764945647918, max_depth = 7, min_samples_leaf = 6, min_samples_split = 8, n_estimators = 500)
        # self.regressors = GradientBoostingRegressor (learning_rate = 0.14822684074082734, max_depth = 7, min_samples_leaf = 6, min_samples_split = 6, n_estimators = 500)
        # self.regressorsHistory = self.regressors.fit (self.X_train.data, self.y_train)

        ###GridSearch
        self.regressors = GradientBoostingRegressor ()
        tunedParameters = [{'criterion': ['friedman_mse'], 'learning_rate': uniform (0.01, 0.2), 'n_estimators': [300, 400, 500, 600], 'max_depth' : range (2,13), 'min_samples_split' : range (2, 13), 'min_samples_leaf' : range (2, 13)}]
        self.regressorsSearch = RandomizedSearchCV (self.regressors, tunedParameters)
        self.regressorsSearch.fit(self.X_train.data, self.y_train)

        print("Best parameters set found on development set:")
        print()
        print(self.regressorsSearch.best_params_)
        print()
        print("Grid scores on development set:")
        print()
        means = self.regressorsSearch.cv_results_['mean_test_score']
        stds = self.regressorsSearch.cv_results_['std_test_score']
        for mean, std, params in zip(means, stds, self.regressorsSearch.cv_results_['params']):
            print("%0.3f (+/-%0.03f) for %r"
                % (mean, std * 2, params))
        print()