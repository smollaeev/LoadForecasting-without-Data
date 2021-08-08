from pahbar.historicalLoad import HistoricalLoad
from pahbar.independentVariables import IndependentVariables
import numpy as np
from pahbar.dataSet import DataSet

class STPredictor:
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

    def __get_Input__ (self, features, hour, historicalLoadList):
        inputX = list (features)
        inputX.extend ([historicalLoadList [hour + 2], historicalLoadList [hour + 26]])
        X = IndependentVariables (inputX)
        X.data = np.array (X.data).reshape (1,-1)
        X.encode_OneHot_Transform_STLF (self.X_train)
        X.scale_Features_STLF (self.X_train)
        return X

    def predict(self, predictDates, R, features, output, replace = False):
        yesterdayLoad = R.unpickle_Data ('YesterdayLoad')
        for row in range (len (predictDates)):
            historicalLoadList = self.__get_HistoricalLoad__ (R, predictDates [row], yesterdayLoad)
            y_pred = []
            for hour in range (24):            
                X = self.__get_Input__ (features.loc [row * 24 + hour, 'Eide Mazhabi':].values, hour, historicalLoadList)
                y_pred.append (self.regressors.predict (X.data) [0])
            # y_pred = y_pred.reshape (1,-1)
            completeFeatures = list (features.loc [row * 24].values)
            del completeFeatures [9]
            completeFeatures.extend (historicalLoadList)

            d = [predictDates[row]]
            d += y_pred
            output.make_CompleteListOfOneRow (row, completeFeatures, y_pred)
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

            R.STOutputHistory.loc [len (R.STOutputHistory)] = output.predictedLoad

        if not (replace):
            featuresData = R.unpickle_Data ('FeaturesData')
            loadData = R.unpickle_Data ('LoadData')
            R.dataSet = DataSet (featuresData, loadData)
        else:
            R.pickle_Data (R.dataSet.featuresData.data, 'FeaturesData')
            R.pickle_Data (R.dataSet.loadData.data, 'LoadData')

        R.pickle_Data (R.STOutputHistory, 'Output_STLF_')

class MTPredictor:
    def __init__ (self, X_train, regressors1, regressors2, regressors3, regressors4):
        self.X_train = X_train
        # self.regressors = regressors
        self.regressors1 = regressors1
        self.regressors2 = regressors2
        self.regressors3 = regressors3
        self.regressors4 = regressors4
    
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
        X.encode_OneHot_Transform_MTLF (self.X_train)
        X.scale_Features_MTLF (self.X_train)
        return X

    def __get_4Ranges__ (self, X):
        X1 = IndependentVariables (np.append (X.data [:, :28], X.data [:, 46:52], axis=1))
        X2 = IndependentVariables (np.append (np.append (X.data [:, :22], X.data [:, 28:35], axis=1), X.data [:, 52:59], axis=1))
        X3 = IndependentVariables (np.append (np.append (X.data [:, :22], X.data [:, 35:42], axis=1), X.data [:, 59:66], axis=1))
        X4 = IndependentVariables (np.append (np.append (X.data [:, :22], X.data [:, 42:46], axis=1), X.data [:, 66:70], axis=1))
        return [X1, X2, X3, X4]

    def predict(self, predictDates, R, features, output):
        yesterdayLoad = R.unpickle_Data ('YesterdayLoad')
        for row in range (len (predictDates)):
            historicalLoadList = self.__get_HistoricalLoad__ (R, predictDates [row], yesterdayLoad)
            X = self.__get_Input__ (features.loc [row, 'Eide Mazhabi':].values, historicalLoadList) 
            Xlist = self.__get_4Ranges__ (X) 

            completeFeatures = list (features.loc [row].values)
            completeFeatures.extend (historicalLoadList)

            d = [predictDates[row]]
            y_pred1 = self.regressors1.predict (Xlist [0].data)
            y_pred2 = self.regressors2.predict (Xlist [1].data)
            y_pred3 = self.regressors3.predict (Xlist [2].data)
            y_pred4 = self.regressors4.predict (Xlist [3].data)

            y_pred = np.append (np.append (np.append (y_pred1, y_pred2, axis=1), y_pred3, axis=1), y_pred4, axis=1)
            y_pred = y_pred.reshape (1,-1)
            for i in range (24):
                d.append (y_pred [0][i])
            output.make_CompleteListOfOneRow (row, completeFeatures, y_pred [0])
            loadDataList = output.predictedDayList [row][-76:]
            loadDataList.append (predictDates [row])
            R.dataSet.loadData.data.loc [R.dataSet.loadData.numberOfRecords] = loadDataList
            R.dataSet.loadData.numberOfRecords += 1

            output.make_ListOfPredictedLoad (d)
            output.output.loc [row] = d

            R.MTOutputHistory.loc [len (R.MTOutputHistory)] = output.predictedLoad


        featuresData = R.unpickle_Data ('FeaturesData')
        loadData = R.unpickle_Data ('LoadData')
        R.dataSet = DataSet (featuresData, loadData)

        R.pickle_Data (R.MTOutputHistory, 'Output_MTLF_')