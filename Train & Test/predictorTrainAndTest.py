import matplotlib.pyplot as plt
import openpyxl
from openpyxl.utils import get_column_letter
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.svm import SVC
from independentVariablesTrainAndTest import IndependentVariables
import numpy as np
from sklearn.model_selection import train_test_split
from clusteringTrainAndTest import Clusterer
import copy
import sklearn.cluster as cluster
from sklearn.preprocessing import StandardScaler

class Predictor:
    def __init__ (self, X_train, y_train, regressors, classifier = None, clusterer = None):
        self.X_train = X_train
        self.y_train = y_train 
        self.classifier = classifier
        self.clusterer = clusterer
        self.regressors = regressors

    def predict (self, R):
        X_test = R.X_test
        y_test = R.y_test

        # X_test.encode_Labels (self.X_train)
        
        X_test.encode_OneHot_Transform (self.X_train)
        X_test.scale_Features (self.X_train)

        # X_testClassifier = self.fs.transform(X_test.data)
        try:
            predictedClasses = self.classifier.predict(X_test.data)
        except:
            print ('without clustering')
        y_pred = np.zeros (len (X_test.data))

        try:
            for i in range (len (X_test.data)):
                for j in range (self.clusterer.numberOfClusters):
                    if predictedClasses [i] == j:
                        y_pred [i] = (self.regressors [j].predict (X_test.data [i].reshape (1,-1)))

        except:
            for i in range (len (X_test.data)): 
                y_pred [i] = (self.regressors.predict (X_test.data [i].reshape (1,-1)))

        error = (sum([abs((y-x)/y) for x, y in zip(y_pred, y_test)])/len(y_test))*100
        print (np.average (error))