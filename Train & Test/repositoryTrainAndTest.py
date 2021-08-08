import openpyxl
from datetime import date
import pandas as pd
import numpy as np
from independentVariablesTrainAndTest import IndependentVariables
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
import copy
import datetime
import os

class Repository:

    def __init__ (self, dataSetType):
        self.dataSet = pd.read_excel ('./data/DataSet_ExcludingDG_Hourly.xlsx', index_col= 0, engine='openpyxl')
        self.variables = self.dataSet.iloc [:, 1:-1].columns
        self.dataSetType = dataSetType

    def get_TrainSet (self):
        self.X = self.dataSet.iloc [:, 1:-1].values
        self.y = self.dataSet.iloc [:, -1].values
        X_train, X_test, self.y_train, self.y_test = train_test_split (self.X, self.y, test_size = 0.2, random_state= 1)
        testSet = pd.DataFrame (data=X_test, columns=self.dataSet.columns [1:-1])
        testSet ['y_Actual'] = self.y_test
        dirName = f'./Results/{datetime.date.today ()}'
        try:
            os.mkdir(dirName)
            testSet.to_excel (os.path.join (dirName, f'TestSet_{self.dataSetType}_{datetime.date.today ()}.xlsx'))
        except:
            testSet.to_excel (os.path.join (dirName, f'TestSet_{self.dataSetType}_{datetime.date.today ()}.xlsx'))
        self.X_train = IndependentVariables (X_train)
        self.X_test = IndependentVariables (X_test)

    def prepare_Data (self):
        self.X_train.encode_OneHot_FitTransform ()
        self.X_train.fit_FeatureScaler ()
        self.X_train.scale_Features (self.X_train)

    
