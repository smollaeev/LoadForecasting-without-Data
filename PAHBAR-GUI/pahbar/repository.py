from datetime import timedelta
from pahbar.dataSet import DataSet
import pandas as pd
from pahbar.independentVariables import IndependentVariables
import os
import pickle
import os.path
from persiantools.jdatetime import JalaliDate
import logging
from pahbar.featuresData import STFeaturesData

class Repository:

    def __init__ (self, path):
        self.directoryPath = path
        self.selectedDataSet = '.pickle'
        self.outputHeaders = ['نوع داده', 'تاریخ']
        for i in range (1, 25):
            self.outputHeaders.append (f'H{i}')
        self.dataSet = DataSet (self.unpickle_Data ('FeaturesData'), self.unpickle_Data ('LoadData'))
        self.STOutputHistory = self.unpickle_Data ('Output_STLF_')
        self.MTOutputHistory = self.unpickle_Data ('Output_MTLF_')
        try:
            self.yesterdayLoadData = self.unpickle_Data ('YesterdayLoad')
        except:
            pass

    def get_ShortTermTrainSet (self):
        hourlyFeatures = STFeaturesData (self.dataSet.featuresData.data)
        hourlyLoadData = self.dataSet.loadData.convert_ToHourly ()
        X = hourlyFeatures.data.iloc [:, 1:].join (hourlyLoadData[['LastWeekLoad', 'YesterdayLoad']])
        X = X.values
        X_train = IndependentVariables (X)
        y_train = hourlyLoadData ['Load'].values
        return X_train, y_train

    def get_MidTermTrainSet (self):
        X = self.dataSet.featuresData.data.iloc [:, 1:].join (self.dataSet.loadData.data.iloc [:, :-27])
        X = X.values
        X_train = IndependentVariables (X)
        y_train = self.dataSet.loadData.data.iloc [:, -27:-3].values
        return X_train, y_train

    def export_PredictionAsXLSX (self, fromDate, toDate, path, predictionMode):
        self.get_PredictedValues (from_date = fromDate, to_date = toDate, predictionMode = predictionMode)
        if self.predictedDataHistory:
            for i in range (len (self.predictedDataHistory)):
                for j in range (len (self.predictedDataHistory [i])):
                    if isinstance (self.predictedDataHistory [i][j], float):
                        self.predictedDataHistory [i][j] = round (self.predictedDataHistory [i][j], 3)
                    
            exportedOutput = pd.DataFrame (data = self.predictedDataHistory, columns= self.outputHeaders)
            exportedOutput.to_excel (path)

    def get_PredictedValues (self, from_date, to_date, predictionMode):
        self.outputHistory = self.unpickle_Data (f'Output_{predictionMode}LF_')
        self.predictedDataHistory = []
        currentDate = from_date - timedelta (days=1)
        while (currentDate != to_date):
            currentDate += timedelta (days=1)
            for i in range (len (self.outputHistory)):
                index = len (self.outputHistory) - i - 1
                dateList = str (self.outputHistory.iloc [index, self.outputHistory.columns.get_loc('تاریخ')]).split ('-')
                gregorianDate = JalaliDate (int (dateList [0]), int (dateList [1]), int (dateList [2])).to_gregorian()
                if (gregorianDate == currentDate):
                    self.predictedDataHistory.append (['Predicted'] + self.outputHistory.iloc [index,:-1].values.tolist ())
                    break

    def export_AsXLSX (variable, path):
        variable.to_excel (path)

    def save_Plot (fig, path):
        try:
            fig.savefig (path)
            return True
        except Exception as inst:
            print (inst)
            logging.warning (inst)
            return False

    def pickle_Data (self, data, name):
        fileName = name + self.selectedDataSet
        fileToWrite = os.path.join (self.directoryPath, fileName)
        with open(fileToWrite, 'wb') as file:
            pickle.dump (data, file)

    def unpickle_Data (self, name):
        fileName = name + self.selectedDataSet
        path = os.path.join (self.directoryPath, fileName)
        with open (path, 'rb') as file:
            data = pickle.load (file)
        return data

    def select_DataSet (self, mode):
        if self.selectedDataSet != mode:
            self.selectedDataSet = mode
            self.dataSet = DataSet (self.unpickle_Data ('FeaturesData'), self.unpickle_Data ('LoadData'))
            self.STOutputHistory = self.unpickle_Data ('Output_STLF_') 
            self.MTOutputHistory = self.unpickle_Data ('Output_MTLF_') 
 
    def export_AllPredictionHistory (self, file_path, midTerm = False):
        if midTerm:
            self.outputHistory = self.unpickle_Data ('Output_MTLF_')
        else:
            self.outputHistory = self.unpickle_Data ('Output_STLF_')
        for i in range (len (self.outputHistory)):
            for j in range (1, 25):
                self.outputHistory.iloc [i, self.outputHistory.columns.get_loc(f'H{j}')] = round (self.outputHistory.iloc [i][f'H{j}'], 3)
        self.outputHistory.to_excel (file_path)        