from scipy.sparse import data
from sklearn.ensemble import RandomForestRegressor
from sklearn.ensemble import GradientBoostingRegressor
import xgboost as xgb
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
import datetime
import matplotlib.pyplot as plt

class Trainer:
    def __init__ (self, X_train, y_train, dataSetType, variablesNames):
        self.X_train = X_train
        self.y_train = y_train
        self.dataSetType = dataSetType
        self.variables = variablesNames

    def train (self):
        ##with clustering

        # clusteringData = copy.deepcopy (self.y_train [:, -2:])
        # sc_Clustering = StandardScaler ()
        # clusteringData = sc_Clustering.fit_transform (clusteringData)
        # self.clusterer = Clusterer (clusteringData)
        # self.clusterer.plot_Clusters (cluster.KMeans, (), {'n_clusters' : 2, 'init' : 'k-means++', 'random_state' : 42})
        # self.clusterer.kMeans ()
        # self.__seperate_LabelsData ()
        # self.__design_RegressorsForEachClass ()
        # self.__train_SVMClassifier ()  
        # self.__train_RandomForestClassifier ()

        ##without clustering

        # self.regressors = xgb.XGBRegressor (gamma = 1, learning_rate = 0.12645036783043867, max_depth = 7, min_child_weight = 2.643065528997738, n_estimators = 500, reg_alpha = 1, reg_lambda = 4)
        # self.regressorsHistory = self.regressors.fit (self.X_train.data, self.y_train)

        self.regressors = xgb.XGBRegressor (gamma = 1, learning_rate = 0.17050036324954973, max_depth = 9, min_child_weight = 7.132296827885341, n_estimators = 300, reg_alpha = 1, reg_lambda = 2)
        self.regressorsHistory = self.regressors.fit (self.X_train.data, self.y_train)

        ###GridSearch
        # self.regressors = GradientBoostingRegressor ()
        # self.regressors = xgb.XGBRegressor ()
        # tunedParameters = [{'gamma':range (0,5), 'learning_rate': uniform (0.01, 0.2), 'max_depth': range (1, 10), 'min_child_weight': uniform (1, 10), 'n_estimators' : [100, 200, 300, 500], 'reg_alpha' : range (1, 5), 'reg_lambda' : range (1, 5)}]
        # self.regressorsSearch = RandomizedSearchCV (self.regressors, tunedParameters)
        # self.regressorsSearch.fit(self.X_train.data, self.y_train)

        # f = open (f'./Results/{datetime.date.today()}/TunedParameters-{self.dataSetType}-{datetime.date.today()}.txt', "w+")
        # f.write (f'Best parameters set found on development set:\n {self.dataSetType}\n{self.variables}\n{self.regressorsSearch.best_params_}\nGrid scores on development set:\n')
        # means = self.regressorsSearch.cv_results_['mean_test_score']
        # stds = self.regressorsSearch.cv_results_['std_test_score']
        # for mean, std, params in zip(means, stds, self.regressorsSearch.cv_results_['params']):
        #     f.write ("%0.3f (+/-%0.03f) for %r"
        #         % (mean, std * 2, params))
        #     f.write ('\n')
        # f.close ()
        # end = 1