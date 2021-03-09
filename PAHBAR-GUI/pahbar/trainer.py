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
            self.regressors = GradientBoostingRegressor (learning_rate= 0.13696764945647918, max_depth = 7, min_samples_leaf = 6, min_samples_split = 8, n_estimators = 500)
        else:
            self.regressors = GradientBoostingRegressor (learning_rate = 0.14822684074082734, max_depth = 7, min_samples_leaf = 6, min_samples_split = 6, n_estimators = 500)

        self.regressors.fit (self.R.X_train.data, self.R.y_train)

        self.R.dump_TrainedAlgorithmsData (self)