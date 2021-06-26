import pandas as pd
from independentVariablesTrainAndTest import IndependentVariables
from sklearn.model_selection import train_test_split
import datetime
import os

class Repository:

    def __init__ (self, dataSetType):
        self.dataSet = pd.read_excel ('./data/DataSet.xlsx', index_col= 0, engine='openpyxl')
        self.variables = self.dataSet.iloc [:, :-26].columns
        self.dataSetType = dataSetType

    def get_TrainSet (self):
        self.X = self.dataSet.iloc [:, :-26].values
        self.y = self.dataSet.iloc [:, -26:-2].values
        X_train, X_test, self.y_train, self.y_test = train_test_split (self.X, self.y, test_size = 0.2, random_state= 1)
        testSet = pd.DataFrame (data=X_test, columns=list (self.variables))
        for i in range (24):
            testSet [f'load{i+1}'] = self.y_test [:, i]
        
        dirName = f'./Results/{datetime.date.today ()}'
        try:
            os.mkdir(dirName)
            testSet.to_excel (os.path.join (dirName, f'TestSet_{self.dataSetType}_{datetime.date.today ()}.xlsx'))
        except:
            testSet.to_excel (os.path.join (dirName, f'TestSet_{self.dataSetType}_{datetime.date.today ()}.xlsx'))
        self.X_train = IndependentVariables (X_train)
        self.X_test = IndependentVariables (X_test)

    def prepare_Data (self):        
        # self.X_train.fit_LabelEncoder ()
        # self.X_train.encode_Labels (self.X_train)

        self.X_train.encode_OneHot_FitTransform ()
        self.X_train.fit_FeatureScaler ()
        self.X_train.scale_Features (self.X_train)

    
