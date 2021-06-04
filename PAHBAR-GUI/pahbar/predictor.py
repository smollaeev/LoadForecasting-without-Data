from pahbar.historicalLoad import HistoricalLoad
from pahbar.independentVariables import IndependentVariables
import numpy as np
from pahbar.dataSet import DataSet

class Predictor:
    def __init__ (self, X_train, regressors):
        self.X_train = X_train
        self.regressors = regressors
    
    def __get_HistoricalLoad__ (self, R, date, yesterdayLoad):
        historicalLoadList = []
        historicalLoad = HistoricalLoad (R.dataSet)
        historicalLoad.get_HistoricalLoadData (date, yesterdayLoad, predictDay = True)
        historicalLoadList.append (max (historicalLoad.yesterdayLoad))
        historicalLoadList.append (historicalLoad.yesterdayLoad.index (max (historicalLoad.yesterdayLoad)) + 1)
        historicalLoadList += historicalLoad.lastWeekLoad
        historicalLoadList += historicalLoad.yesterdayLoad   
        return historicalLoadList

    def __get_Input__ (self, features, historicalLoadList):
        inputX = list (features)
        inputX.extend (historicalLoadList)
        X = IndependentVariables (inputX)
        X.data = np.array (X.data).reshape (1,-1)
        X.encode_OneHot_Transform (self.X_train)
        X.scale_Features (self.X_train)
        return X

    def predict (self, predictDates, R, features, output, replace = False):
        yesterdayLoad = R.unpickle_Data ('YesterdayLoad')        
        for row in range (len (predictDates)):
            historicalLoadList = self.__get_HistoricalLoad__ (R, predictDates [row], yesterdayLoad)  
            X = self.__get_Input__ (features.loc [row, 'Eide Mazhabi':].values, historicalLoadList)  

            completeFeatures = list (features.loc [row].values)
            completeFeatures.extend (historicalLoadList)

            d = []
            d.append (predictDates [row])
            y_pred = self.regressors.predict (X.data)
            y_pred = y_pred.reshape (1,-1)
            for i in range (24):
                d.append (y_pred [0][i])
            output.make_CompleteListOfOneRow (row, completeFeatures, y_pred [0])
            loadDataList = output.predictedDayList [row][-76:]
            loadDataList.append (predictDates [row])
            R.dataSet.loadData.data.loc [R.dataSet.loadData.numberOfRecords] = loadDataList
            R.dataSet.loadData.numberOfRecords += 1
            if replace:
                R.dataSet.featuresData.data.loc [R.dataSet.featuresData.numberOfRecords] = output.predictedDayList [row][:-76]
                R.dataSet.featuresData.numberOfRecords += 1
                R.dataSet.featuresData.determine_EndDate ()
                R.dataSet.loadData.determine_EndDate ()
            
            output.make_ListOfPredictedLoad (d)
            output.output.loc [row] = d
            
            R.outputHistory.loc [len (R.outputHistory)] = output.predictedLoad

        if not (replace):
            featuresData = R.unpickle_Data ('FeaturesData')
            loadData = R.unpickle_Data ('LoadData')
            R.dataSet = DataSet (featuresData, loadData)
        else:
            R.pickle_Data (R.dataSet.featuresData.data, 'FeaturesData')
            R.pickle_Data (R.dataSet.loadData.data, 'LoadData')

        R.pickle_Data (R.outputHistory, 'Output')