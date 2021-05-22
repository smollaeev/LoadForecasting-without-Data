from pahbar.historicalLoad import HistoricalLoad
from pahbar.independentVariables import IndependentVariables
import numpy as np
from pahbar.dataSet import DataSet

class Predictor:
    def __init__ (self, X_train, regressors):
        self.X_train = X_train
        self.regressors = regressors
        
    def predict (self, predictDates, R, features, output):
        yesterdayLoad = R.unpickle_Data ('YesterdayLoad')        
        for row in range (len (predictDates)):
            historicalLoadList = []
            historicalLoad = HistoricalLoad (R.dataSet)
            historicalLoad.get_HistoricalLoadData (predictDates [row], yesterdayLoad, predictDay = True)
            historicalLoadList.append (max (historicalLoad.yesterdayLoad))
            historicalLoadList.append (historicalLoad.yesterdayLoad.index (max (historicalLoad.yesterdayLoad)) + 1)
            historicalLoadList += historicalLoad.lastWeekLoad
            historicalLoadList += historicalLoad.yesterdayLoad    
            d = []
            d.append (predictDates [row])
            inputX = list (features.loc [row, 'Eide Mazhabi':].values)
            inputX.extend (historicalLoadList)
            completeFeatures = list (features.loc [row].values)
            completeFeatures.extend (historicalLoadList)
            X = IndependentVariables (inputX)
            X.data = np.array (X.data).reshape (1,-1)
            X.encode_OneHot_Transform (self.X_train)
            X.scale_Features (self.X_train)            
            y_pred = self.regressors.predict (X.data)
            y_pred = y_pred.reshape (1,-1)
            for i in range (24):
                d.append (y_pred [0][i])
            output.make_CompleteListOfOneRow (row, completeFeatures, y_pred [0])
            R.dataSet.data.loc [R.dataSet.numberOfRecords] = output.predictedDayList [row]
            R.dataSet.numberOfRecords += 1

            output.make_ListOfPredictedLoad (d)
            output.output.loc [row] = d
            
            R.outputHistory.loc [len (R.outputHistory)] = output.predictedLoad

        data_ = R.unpickle_Data ('DataSet')  
        R.dataSet = DataSet (data_)
        R.pickle_Data (R.outputHistory, 'Output')