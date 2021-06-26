from numpy.lib.function_base import append
from independentVariablesTrainAndTest import IndependentVariables
import numpy as np
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.multioutput import MultiOutputRegressor
from scipy.stats import uniform
from sklearn.model_selection import RandomizedSearchCV
import datetime

class Trainer:
    def __init__ (self, X_train, y_train, dataSetType, variablesNames):
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
        self.dataSetType = dataSetType
        self.variables = variablesNames

    def train(self):
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

        self.regressors1 = MultiOutputRegressor (GradientBoostingRegressor (learning_rate = 0.1545603294037822, max_depth = 2, min_samples_leaf = 2, min_samples_split = 6, n_estimators = 600))
        self.regressors2 = MultiOutputRegressor (GradientBoostingRegressor (learning_rate = 0.05312384662574374, max_depth = 3, min_samples_leaf = 11, min_samples_split = 2, n_estimators = 400))
        self.regressors3 = MultiOutputRegressor (GradientBoostingRegressor (learning_rate = 0.09799479361171441, max_depth = 3, min_samples_leaf = 12, min_samples_split = 5, n_estimators = 300))
        self.regressors4 = MultiOutputRegressor (GradientBoostingRegressor (learning_rate = 0.09435769499714551, max_depth = 3, min_samples_leaf = 2, min_samples_split = 6, n_estimators = 400))
        
        # self.regressors1 = MultiOutputRegressor (GradientBoostingRegressor (learning_rate = 0.12861628259637697, max_depth = 2, min_samples_leaf = 2, min_samples_split = 11, n_estimators = 500))
        # self.regressors2 = MultiOutputRegressor (GradientBoostingRegressor (learning_rate = 0.02165431283694489, max_depth = 5, min_samples_leaf = 2, min_samples_split = 4, n_estimators = 500))
        # self.regressors3 = MultiOutputRegressor (GradientBoostingRegressor (learning_rate = 0.1105016281437299, max_depth = 4, min_samples_leaf = 6, min_samples_split = 6, n_estimators = 600))
        # self.regressors4 = MultiOutputRegressor (GradientBoostingRegressor (learning_rate = 0.12273083283463927, max_depth = 5, min_samples_leaf = 5, min_samples_split = 5, n_estimators = 500))

        self.regressorsHistory1 = self.regressors1.fit (self.X_train1.data, self.y_train1)
        self.regressorsHistory2 = self.regressors2.fit (self.X_train2.data, self.y_train2)
        self.regressorsHistory3 = self.regressors3.fit (self.X_train3.data, self.y_train3)
        self.regressorsHistory4 = self.regressors4.fit (self.X_train4.data, self.y_train4)

        # print(self.regressors.feature_importances_)
        # plt.bar(range(len(self.regressors.feature_importances_)), self.regressors.feature_importances_)
        # plt.show()

        #GridSearch
        # self.regressors = MultiOutputRegressor (GradientBoostingRegressor ())
        # # print (self.regressors.get_params().keys())
        # tunedParameters = [{'estimator__criterion': ['friedman_mse'], 'estimator__learning_rate': uniform (0.01, 0.2), 'estimator__n_estimators': [300, 400, 500, 600], 'estimator__max_depth' : range (2,13), 'estimator__min_samples_split' : range (2, 13), 'estimator__min_samples_leaf' : range (2, 13)}]
        # self.regressorsSearch = RandomizedSearchCV (self.regressors, tunedParameters)
        # self.regressorsSearch.fit(self.X_train4.data, self.y_train4)
        # with open (f'./Results/{datetime.date.today()}/TunedParameters-{self.dataSetType}-y_train4-{datetime.date.today()}.txt', "w+") as f:
        #     f.write (f'Best parameters set found on development set:\n {self.dataSetType}\ny_Train4\n{self.variables}\n{self.regressorsSearch.best_params_}\nGrid scores on development set:\n')
        #     means = self.regressorsSearch.cv_results_['mean_test_score']
        #     stds = self.regressorsSearch.cv_results_['std_test_score']
        #     for mean, std, params in zip(means, stds, self.regressorsSearch.cv_results_['params']):
        #         f.write ("%0.3f (+/-%0.03f) for %r"
        #             % (mean, std * 2, params))
        #         f.write ('\n')
        # end = 1