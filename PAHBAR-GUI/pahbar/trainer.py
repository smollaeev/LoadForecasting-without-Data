import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.multioutput import MultiOutputRegressor
from sklearn.svm import SVC
import numpy as np
from sklearn.model_selection import train_test_split
from pahbar.clustering import Clusterer
import copy
import sklearn.cluster as cluster
from sklearn.preprocessing import StandardScaler
import pickle

class Trainer:
    def __init__ (self, R):
        self.R = R

    def train (self):
        if self.R.selectedDataSet == '.pickle':
            self.regressors = GradientBoostingRegressor (learning_rate = 0.08761951839869596, max_depth = 7, min_samples_leaf = 12, min_samples_split = 5, n_estimators = 500)
        else:
            self.regressors = GradientBoostingRegressor (learning_rate = 0.14644075566188816, max_depth = 8, min_samples_leaf = 3, min_samples_split = 3, n_estimators = 600)

        self.regressors.fit (self.R.X_train.data, self.R.y_train)

        self.R.dump_TrainedAlgorithmsData (self)