import openpyxl
from datetime import date
import pandas as pd
import numpy as np
from independentVariablesTrainAndTest import IndependentVariables
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt

class Repository:

    def __init__ (self):
        self.dataSet = pd.read_excel ('DataSet_ExcludingDG_Hourly.xlsx', index_col= 0, engine='openpyxl')

    def get_TrainSet (self):
        self.X = self.dataSet.iloc [:, 1:-1].values
        self.y = self.dataSet.iloc [:, -1].values
        X_train, X_test, self.y_train, self.y_test = train_test_split (self.X, self.y, test_size = 0.2, random_state= 1)
        self.X_train = IndependentVariables (X_train)
        self.X_test = IndependentVariables (X_test)

    def prepare_Data (self):        
        # self.X_train.fit_LabelEncoder ()
        # self.X_train.encode_Labels (self.X_train)

        self.X_train.encode_OneHot_FitTransform ()

        self.X_train.fit_FeatureScaler ()
        self.X_train.scale_Features (self.X_train)

    
