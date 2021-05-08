from scipy.sparse import data
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
        # manipulatedData = copy.deepcopy (self.X_train.data)
        # manipulatedData = np.delete (manipulatedData, [16, 17], 1)
        # self.X_train_Regression = copy.deepcopy (manipulatedData)

        # self.regressors = MultiOutputRegressor (GradientBoostingRegressor ())
        # # self.regressors = MultiOutputRegressor (GradientBoostingRegressor (learning_rate = 0.0499, max_depth = 3, min_samples_leaf = 7, min_samples_split = 2, n_estimators = 300))
        # self.regressors = MultiOutputRegressor (GradientBoostingRegressor (learning_rate = 0.0476, max_depth = 3, min_samples_leaf = 2, min_samples_split = 7, n_estimators = 500))

        # self.regressorsHistory = self.regressors.fit (self.X_train_Regression, self.y_train [:, :-2])



        self.regressors = GradientBoostingRegressor (learning_rate = 0.08761951839869596, max_depth = 7, min_samples_leaf = 12, min_samples_split = 5, n_estimators = 500)
        self.regressorsHistory = self.regressors.fit (self.X_train.data, self.y_train)
        print(self.regressors.feature_importances_)
        plt.bar(range(len(self.regressors.feature_importances_)), self.regressors.feature_importances_)
        plt.show()

        # self.regressors = GradientBoostingRegressor (learning_rate = 0.14644075566188816, max_depth = 8, min_samples_leaf = 3, min_samples_split = 3, n_estimators = 600)
        # self.regressorsHistory = self.regressors.fit (self.X_train.data, self.y_train)

        ###GridSearch
        # self.regressors = GradientBoostingRegressor ()
        # tunedParameters = [{'criterion': ['friedman_mse'], 'learning_rate': uniform (0.01, 0.2), 'n_estimators': [300, 400, 500, 600], 'max_depth' : range (2,13), 'min_samples_split' : range (2, 13), 'min_samples_leaf' : range (2, 13)}]
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